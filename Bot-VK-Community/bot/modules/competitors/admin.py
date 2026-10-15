from __future__ import annotations

from datetime import datetime

from vkbottle.bot import Message

from bot.admin_draft import clear_draft, draft_data, set_draft
from bot.db.models import AdminDraft, CompetitorSnapshot
from bot.db.session import get_session
from bot.modules.competitors.vk_search import build_report
from bot.modules.posts.admin import is_admin
from bot.modules.posts.keyboards import admin_panel_keyboard


async def prompt_report_topic(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        await set_draft(session, message.from_id, "report_topic")
    await message.answer("Введите тему для поиска конкурентов сообщением (например: ресницы наращивание):")


async def handle_report_topic_input(message: Message, draft: AdminDraft) -> None:
    topic = (message.text or "").strip()
    if not topic:
        await message.answer("Пришлите тему сообщением.")
        return
    async with get_session() as session:
        await set_draft(session, message.from_id, "report_city", {"topic": topic})
    await message.answer("Теперь введите город сообщением (например: Москва):")


async def handle_report_city_input(message: Message, draft: AdminDraft) -> None:
    city = (message.text or "").strip()
    if not city:
        await message.answer("Пришлите город сообщением.")
        return
    topic = draft_data(draft).get("topic", "")

    async with get_session() as session:
        await clear_draft(session, message.from_id)

    await message.answer(f"Ищу конкурентов по теме «{topic}» в городе «{city}»…")
    report = await build_report(topic, city)

    if not report["city_resolved"]:
        await message.answer(f"Город «{city}» не найден в справочнике VK, поиск выполнен без фильтра по городу.")

    async with get_session() as session:
        for item in report["top"]:
            group = item["group"]
            session.add(
                CompetitorSnapshot(
                    query=topic,
                    city=city,
                    group_id=group.id,
                    group_name=group.name,
                    members_count=group.members_count or 0,
                    is_active=item["active"],
                    captured_at=datetime.utcnow(),
                )
            )
        await session.commit()

    lines = [
        f"Найдено пабликов: {report['total_found']}",
        f"Из них активны (пост за последние 30 дн.): {report['active_count']}",
        "",
        "Топ по числу участников:",
    ]
    for i, item in enumerate(report["top"], start=1):
        group = item["group"]
        active_mark = "🟢" if item["active"] else "⚪"
        lines.append(f"{i}. {active_mark} {group.name} — {group.members_count or 0} участников (vk.com/club{group.id})")

    await message.answer("\n".join(lines), keyboard=admin_panel_keyboard())
