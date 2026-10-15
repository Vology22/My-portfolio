from __future__ import annotations

import json

from sqlalchemy import select
from vkbottle.bot import Message

from bot.admin_draft import clear_draft, draft_data, set_draft
from bot.db.models import AdminDraft, CandidateStatus, CompetitorAudienceCandidate
from bot.db.session import get_session
from bot.db.settings_repo import get_int_setting, get_setting, set_setting
from bot.modules.posts.admin import is_admin, resolve_labels
from bot.modules.posts.keyboards import (
    AUDIENCE_CRITERIA_LABELS,
    admin_audience_keyboard,
    audience_criteria_keyboard,
    candidate_card_keyboard,
)

CANDIDATES_PER_SCREEN = 10


async def show_audience_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        new_count = (
            await session.execute(
                select(CompetitorAudienceCandidate).where(CompetitorAudienceCandidate.status == CandidateStatus.NEW)
            )
        ).scalars().all()
        sources_label = (await resolve_labels(session, "content")).get("admin_sources", "🔁 Источники")
    await message.answer(
        f"Кандидатов на обработку: {len(new_count)}.\n\n"
        f"Бот только подбирает и фильтрует кандидатов из участников сообществ-конкурентов "
        f"(тех же, что заданы в разделе «{sources_label}») — писать им и добавлять в друзья "
        "нужно вручную, бот массовых действий не делает.",
        keyboard=admin_audience_keyboard(),
    )


async def show_candidates(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        candidates = (
            await session.execute(
                select(CompetitorAudienceCandidate)
                .where(CompetitorAudienceCandidate.status == CandidateStatus.NEW)
                .order_by(CompetitorAudienceCandidate.found_at.asc())
                .limit(CANDIDATES_PER_SCREEN)
            )
        ).scalars().all()

    if not candidates:
        await message.answer("Новых кандидатов пока нет.", keyboard=admin_audience_keyboard())
        return

    for candidate in candidates:
        name = f"{candidate.first_name} {candidate.last_name}".strip() or f"id{candidate.vk_id}"
        lines = [
            f"{name}",
            f"https://vk.com/id{candidate.vk_id}",
            f"Друзей: {candidate.friends_count}, подписчиков: {candidate.followers_count}",
        ]
        if candidate.city:
            lines.append(f"Город: {candidate.city}")
        if candidate.matched_keyword:
            lines.append(f"Совпадение по подпискам: «{candidate.matched_keyword}»")
        await message.answer("\n".join(lines), keyboard=candidate_card_keyboard(candidate.vk_id))


async def cmd_mark_candidate(message: Message, vk_id: int, status_value: str) -> None:
    if not is_admin(message.from_id):
        return
    try:
        status = CandidateStatus(status_value)
    except ValueError:
        return
    async with get_session() as session:
        candidate = await session.get(CompetitorAudienceCandidate, vk_id)
        if candidate is None:
            return
        candidate.status = status
        await session.commit()
    await message.answer("Отмечено.", keyboard=admin_audience_keyboard())


async def show_criteria(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        min_friends = await get_int_setting(session, "audience_min_friends")
        min_followers = await get_int_setting(session, "audience_min_followers")
        cities = json.loads(await get_setting(session, "audience_cities"))
        keywords = json.loads(await get_setting(session, "audience_keywords"))
        labels = await resolve_labels(session, "audience")

    lines = [
        f"{labels['min_friends']}: {min_friends or 'без ограничения'}",
        f"{labels['min_followers']}: {min_followers or 'без ограничения'}",
        f"{labels['cities']}: {', '.join(cities) if cities else 'без ограничения'}",
        f"{labels['keywords']}: {', '.join(keywords) if keywords else 'без проверки'}",
    ]
    await message.answer(
        "Текущие критерии отбора кандидатов:\n" + "\n".join(lines), keyboard=audience_criteria_keyboard(labels)
    )


async def prompt_edit_criteria(message: Message, key: str) -> None:
    if not is_admin(message.from_id):
        return
    if key not in AUDIENCE_CRITERIA_LABELS:
        return
    async with get_session() as session:
        await set_draft(session, message.from_id, "audience_edit", {"key": key})

    if key in ("min_friends", "min_followers"):
        prompt = "Введите целое число сообщением (0 — без ограничения):"
    else:
        prompt = "Пришлите список через запятую сообщением (пусто — очистить список):"
    await message.answer(prompt)


async def handle_audience_edit_input(message: Message, draft: AdminDraft) -> None:
    key = draft_data(draft).get("key")
    if key not in AUDIENCE_CRITERIA_LABELS:
        return

    text = (message.text or "").strip()
    async with get_session() as session:
        if key in ("min_friends", "min_followers"):
            if not text.isdigit():
                await message.answer("Введите целое число сообщением (0 — без ограничения).")
                return
            await set_setting(session, f"audience_{key}", text)
        else:
            items = [part.strip() for part in text.split(",") if part.strip()]
            await set_setting(session, f"audience_{key}", json.dumps(items, ensure_ascii=False))
        await clear_draft(session, message.from_id)
        labels = await resolve_labels(session, "audience")

    await message.answer(f"{labels[key]}: обновлено.", keyboard=audience_criteria_keyboard(labels))
