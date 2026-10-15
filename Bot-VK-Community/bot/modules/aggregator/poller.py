from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from bot.config import settings
from bot.db.models import CompetitorSource, RepostedPost
from bot.db.session import get_session
from bot.db.settings_repo import get_int_setting, set_setting
from bot.vk_attachments import attachments_to_string
from bot.vk_client import api

POSTS_PER_SOURCE = 20  # сколько последних постов источника проверять за один проход
THROTTLE_DELAY = 1.0  # пауза между репостами, чтобы не словить антиспам VK


async def _category_ids_with_active_sources(session) -> list[int]:
    return (
        await session.execute(
            select(CompetitorSource.category_id)
            .where(CompetitorSource.active.is_(True))
            .distinct()
            .order_by(CompetitorSource.category_id)
        )
    ).scalars().all()


async def peek_active_category_id(session) -> int | None:
    """Не двигает ротацию — только показывает, какая категория сейчас 'на очереди'
    (для экрана 🔁 Источники в админке)."""
    category_ids = await _category_ids_with_active_sources(session)
    if not category_ids:
        return None
    index = await get_int_setting(session, "aggregator_rotation_index")
    return category_ids[index % len(category_ids)]


async def _advance_rotation(session) -> int | None:
    """Ротация по тематикам (см. ТЗ_новые_функции.txt, блок 2.3): за один запуск
    poll_competitor_sources обрабатываются источники только ОДНОЙ категории — той,
    что дальше по кругу среди категорий, у которых есть активные источники. Шаг
    ротации — раз за запуск (по расписанию в bot/scheduler.py, сейчас раз в 2 часа),
    а не строго раз в календарные сутки, как изначально хотел заказчик — от точной
    привязки ко времени суток отказались осознанно, см. ТЗ."""
    category_ids = await _category_ids_with_active_sources(session)
    if not category_ids:
        return None
    index = (await get_int_setting(session, "aggregator_rotation_index")) % len(category_ids)
    active_category_id = category_ids[index]
    await set_setting(session, "aggregator_rotation_index", str((index + 1) % len(category_ids)))
    return active_category_id


async def poll_competitor_sources() -> None:
    async with get_session() as session:
        active_category_id = await _advance_rotation(session)
        if active_category_id is None:
            return

        sources = (
            await session.execute(
                select(CompetitorSource).where(
                    CompetitorSource.active.is_(True),
                    CompetitorSource.category_id == active_category_id,
                )
            )
        ).scalars().all()
        source_data = [(s.id, s.group_id, s.last_polled_post_date) for s in sources]
        posts_per_cycle = await get_int_setting(session, "aggregator_posts_per_cycle")
        max_age_hours = await get_int_setting(session, "aggregator_max_age_hours")

    max_age_seconds = max_age_hours * 3600 if max_age_hours > 0 else None
    now_ts = datetime.now(timezone.utc).timestamp()

    reposted_any = False
    for source_id, group_id, last_date in source_data:
        try:
            wall = await api.wall.get(owner_id=-group_id, count=POSTS_PER_SOURCE)
        except Exception:
            continue

        new_posts = [p for p in wall.items if last_date is None or p.date > last_date]
        if max_age_seconds is not None:
            new_posts = [p for p in new_posts if now_ts - p.date <= max_age_seconds]
        if not new_posts:
            continue
        new_posts.sort(key=lambda p: p.date)  # публикуем от старых к новым, сохраняя хронологию
        to_repost = new_posts[:posts_per_cycle] if posts_per_cycle > 0 else new_posts

        # last_polled_post_date продвигаем до последнего поста, отобранного лимитом
        # posts_per_cycle (а не до максимума среди всех найденных) — иначе посты,
        # отрезанные лимитом, потеряются и не попадут в следующий цикл.
        max_date = last_date or 0
        for post in to_repost:
            max_date = max(max_date, post.date)
            if await _repost_one(group_id, post):
                reposted_any = True
            await asyncio.sleep(THROTTLE_DELAY)

        async with get_session() as session:
            source = await session.get(CompetitorSource, source_id)
            if source is not None:
                source.last_polled_post_date = max_date
                await session.commit()

    if not reposted_any:
        await _replay_oldest_repost(source_data)


async def _repost_one(group_id: int, post) -> bool:
    async with get_session() as session:
        exists = (
            await session.execute(
                select(RepostedPost).where(
                    RepostedPost.source_group_id == group_id,
                    RepostedPost.source_post_id == post.id,
                )
            )
        ).scalar_one_or_none()
        if exists is not None:
            return False

        attachments = attachments_to_string(post.attachments)
        if not post.text and not attachments:
            return False

        try:
            result = await api.wall.post(
                owner_id=-settings.group_id,
                message=post.text,
                attachments=attachments or None,
                from_group=1,
            )
        except Exception:
            return False

        session.add(
            RepostedPost(
                source_group_id=group_id,
                source_post_id=post.id,
                our_wall_post_id=result.post_id,
            )
        )
        await session.commit()
        return True


async def _replay_oldest_repost(source_data: list[tuple[int, int, int | None]]) -> None:
    """Заказчик хотел разнообразие, а не тишину, когда у конкурентов нет новых
    постов: вместо распознавания 'того же мастера' (от этой идеи отказались, см.
    ТЗ, блок 2.4) — просто повторно публикуем самый старый уже репостнутый пост
    этой же категории, если с его публикации прошло не меньше
    aggregator_repost_ttl_days, и 'сдвигаем' его в конец очереди по свежести.
    aggregator_repost_ttl_days = 0 отключает повтор полностью."""
    group_ids = [group_id for _id, group_id, _date in source_data]
    if not group_ids:
        return

    async with get_session() as session:
        ttl_days = await get_int_setting(session, "aggregator_repost_ttl_days")
        if ttl_days <= 0:
            return
        threshold = datetime.utcnow() - timedelta(days=ttl_days)

        candidate = (
            await session.execute(
                select(RepostedPost)
                .where(
                    RepostedPost.source_group_id.in_(group_ids),
                    RepostedPost.reposted_at <= threshold,
                )
                .order_by(RepostedPost.reposted_at.asc())
                .limit(1)
            )
        ).scalar_one_or_none()
        if candidate is None:
            return
        candidate_id = candidate.id
        source_group_id = candidate.source_group_id
        source_post_id = candidate.source_post_id

    try:
        response = await api.wall.get_by_id(posts=[f"{source_group_id}_{source_post_id}"])
    except Exception:
        return
    items = getattr(response, "items", response)
    if not items:
        return
    post = items[0]

    attachments = attachments_to_string(post.attachments)
    if not post.text and not attachments:
        return

    try:
        await api.wall.post(
            owner_id=-settings.group_id,
            message=post.text,
            attachments=attachments or None,
            from_group=1,
        )
    except Exception:
        return

    async with get_session() as session:
        row = await session.get(RepostedPost, candidate_id)
        if row is not None:
            row.reposted_at = datetime.utcnow()
            await session.commit()
