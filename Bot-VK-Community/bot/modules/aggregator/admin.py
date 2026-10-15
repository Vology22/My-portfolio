from __future__ import annotations

from sqlalchemy import select
from vkbottle.bot import Message

from bot.admin_draft import clear_draft, draft_data, set_draft
from bot.db.models import AdminDraft, Category, CompetitorSource
from bot.db.session import get_session
from bot.modules.aggregator.poller import peek_active_category_id
from bot.modules.posts.admin import is_admin, resolve_labels
from bot.modules.posts.keyboards import (
    admin_panel_keyboard,
    category_pick_keyboard,
    content_menu_keyboard,
    sources_admin_keyboard,
    sources_remove_keyboard,
)
from bot.vk_client import api


async def show_content_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        labels = await resolve_labels(session, "content")
    await message.answer("Заимствование контента:", keyboard=content_menu_keyboard(labels))


async def show_sources_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        sources = (await session.execute(select(CompetitorSource))).scalars().all()
        categories = {c.id: c.name for c in (await session.execute(select(Category))).scalars().all()}
        active_category_id = await peek_active_category_id(session)

    if not sources:
        text = "Источников пока нет."
    else:
        text = "\n".join(
            f"#{s.id} {s.name} — {categories.get(s.category_id, '?')} ({'активен' if s.active else 'выключен'})"
            for s in sources
        )
        rotation_label = categories.get(active_category_id) if active_category_id is not None else None
        if rotation_label:
            text += f"\n\n🔁 Сейчас в ротации агрегатора: «{rotation_label}» (сменится в следующем цикле опроса)."
    await message.answer(text, keyboard=sources_admin_keyboard())


async def prompt_sources_add(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        await set_draft(session, message.from_id, "sources_add_ref")
    await message.answer("Пришлите ссылку на сообщество-конкурент или его короткое имя/ID сообщением:")


async def handle_sources_add_ref_input(message: Message, draft: AdminDraft) -> None:
    group_ref = (message.text or "").strip().lstrip("@")
    if not group_ref:
        await message.answer("Пришлите ссылку или ID сообщества сообщением.")
        return

    try:
        groups = await api.groups.get_by_id(group_id=group_ref)
    except Exception:
        await message.answer("Не удалось найти сообщество — проверьте ссылку/ID и попробуйте снова.")
        return
    if not groups:
        await message.answer("Сообщество не найдено, попробуйте снова.")
        return
    group = groups[0]

    async with get_session() as session:
        categories = (await session.execute(select(Category))).scalars().all()
        if not categories:
            await clear_draft(session, message.from_id)
            await message.answer(
                "Категорий пока нет — сначала добавьте категорию в разделе «Заимствование контента».",
                keyboard=admin_panel_keyboard(),
            )
            return
        await set_draft(
            session,
            message.from_id,
            "sources_add_category",
            {"group_id": group.id, "group_name": group.name},
        )

    await message.answer(f"Сообщество «{group.name}» найдено. Выберите категорию:", keyboard=category_pick_keyboard(categories))


async def cmd_sources_add_category(message: Message, category_id: int) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        draft = await session.get(AdminDraft, message.from_id)
        if draft is None or draft.action != "sources_add_category":
            return
        data = draft_data(draft)
        group_id = data.get("group_id")
        group_name = data.get("group_name", "")

        existing = (
            await session.execute(select(CompetitorSource).where(CompetitorSource.group_id == group_id))
        ).scalar_one_or_none()
        if existing is not None:
            existing.active = True
            existing.category_id = category_id
        else:
            session.add(CompetitorSource(group_id=group_id, name=group_name, category_id=category_id))
        await clear_draft(session, message.from_id)

    await message.answer(f"Источник «{group_name}» добавлен.", keyboard=sources_admin_keyboard())


async def show_sources_remove_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        sources = (await session.execute(select(CompetitorSource))).scalars().all()
    if not sources:
        await message.answer("Источников пока нет.", keyboard=sources_admin_keyboard())
        return
    await message.answer("Выберите источник для удаления:", keyboard=sources_remove_keyboard(sources))


async def cmd_sources_remove(message: Message, source_id: int) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        source = await session.get(CompetitorSource, source_id)
        if source is None:
            await message.answer("Источник не найден.", keyboard=sources_admin_keyboard())
            return
        name = source.name
        await session.delete(source)
        await session.commit()
    await message.answer(f"Источник «{name}» удалён.", keyboard=sources_admin_keyboard())
