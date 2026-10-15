from __future__ import annotations

import json

from sqlalchemy import delete, select

from bot.db.models import CompetitorAudienceCandidate, CompetitorMember, CompetitorSource
from bot.db.session import get_session
from bot.db.settings_repo import get_int_setting, get_setting
from bot.vk_client import api

MEMBERS_PAGE_SIZE = 1000
MAX_MEMBERS_PER_SOURCE = 10_000  # защита от разбора огромных пабликов за один проход
USERS_BATCH_SIZE = 500  # users.get принимает больше, но берём с запасом

# Список источников для аудитории — тот же CompetitorSource, что и у аггрегатора
# постов (bot/modules/aggregator/poller.py): отдельного списка "источников для
# парсинга" не завели, чтобы не дублировать сущность "сообщество-конкурент".


async def _fetch_all_member_ids(group_id: int) -> set[int]:
    members: set[int] = set()
    offset = 0
    while offset < MAX_MEMBERS_PER_SOURCE:
        try:
            response = await api.groups.get_members(group_id=str(group_id), offset=offset, count=MEMBERS_PAGE_SIZE)
        except Exception:
            break
        items = list(response.items or [])
        if not items:
            break
        members.update(items)
        offset += MEMBERS_PAGE_SIZE
        if len(items) < MEMBERS_PAGE_SIZE:
            break
    return members


async def _load_criteria(session) -> dict:
    return {
        "min_friends": await get_int_setting(session, "audience_min_friends"),
        "min_followers": await get_int_setting(session, "audience_min_followers"),
        "cities": {
            c.strip().lower() for c in json.loads(await get_setting(session, "audience_cities")) if c.strip()
        },
        "keywords": [
            k.strip().lower() for k in json.loads(await get_setting(session, "audience_keywords")) if k.strip()
        ],
    }


def _passes_basic_filters(user, criteria: dict) -> bool:
    if criteria["min_friends"] > 0:
        friends = user.counters.friends if user.counters else None
        if friends is None or friends < criteria["min_friends"]:
            return False
    if criteria["min_followers"] > 0:
        followers = user.counters.followers if user.counters else None
        if followers is None or followers < criteria["min_followers"]:
            return False
    if criteria["cities"]:
        city_title = (user.city.title if user.city else "").strip().lower()
        if city_title not in criteria["cities"]:
            return False
    return True


async def _matched_keyword(user_id: int, keywords: list[str]) -> str | None:
    """None значит 'не прошёл проверку', "" значит 'проверка не задана — считаем,
    что прошёл'. Дорогой вызов (1 запрос groups.get на кандидата), поэтому
    выполняется только для тех, кто уже прошёл дешёвые фильтры друзей/гео/подписчиков."""
    if not keywords:
        return ""
    try:
        response = await api.groups.get(user_id=user_id, extended=True, count=1000)
    except Exception:
        return None
    for group in response.items or []:
        name = (getattr(group, "name", "") or "").lower()
        for keyword in keywords:
            if keyword in name:
                return keyword
    return None


async def _update_snapshot(session, group_id: int, current_members: set[int]) -> set[int]:
    known = set(
        (await session.execute(select(CompetitorMember.vk_id).where(CompetitorMember.group_id == group_id)))
        .scalars()
        .all()
    )
    new_member_ids = current_members - known
    removed = known - current_members

    for vk_id in new_member_ids:
        session.add(CompetitorMember(group_id=group_id, vk_id=vk_id))
    if removed:
        await session.execute(
            delete(CompetitorMember).where(CompetitorMember.group_id == group_id, CompetitorMember.vk_id.in_(removed))
        )
    await session.commit()
    return new_member_ids


async def poll_competitor_audience() -> None:
    async with get_session() as session:
        source_group_ids = (
            await session.execute(select(CompetitorSource.group_id).where(CompetitorSource.active.is_(True)))
        ).scalars().all()
        criteria = await _load_criteria(session)

    for group_id in source_group_ids:
        current_members = await _fetch_all_member_ids(group_id)
        if not current_members:
            continue

        async with get_session() as session:
            new_member_ids = await _update_snapshot(session, group_id, current_members)
        if not new_member_ids:
            continue

        new_member_ids = list(new_member_ids)
        for i in range(0, len(new_member_ids), USERS_BATCH_SIZE):
            batch = new_member_ids[i : i + USERS_BATCH_SIZE]
            try:
                users = await api.users.get(user_ids=batch, fields=["city", "counters"])
            except Exception:
                continue

            for user in users:
                if not _passes_basic_filters(user, criteria):
                    continue
                keyword = await _matched_keyword(user.id, criteria["keywords"])
                if keyword is None:
                    continue

                async with get_session() as session:
                    exists = await session.get(CompetitorAudienceCandidate, user.id)
                    if exists is not None:
                        continue
                    session.add(
                        CompetitorAudienceCandidate(
                            vk_id=user.id,
                            source_group_id=group_id,
                            first_name=user.first_name or "",
                            last_name=user.last_name or "",
                            friends_count=(user.counters.friends if user.counters else None) or 0,
                            followers_count=(user.counters.followers if user.counters else None) or 0,
                            city=(user.city.title if user.city else "") or "",
                            matched_keyword=keyword or None,
                        )
                    )
                    await session.commit()
