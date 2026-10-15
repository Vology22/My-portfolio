from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from vkbottle.bot import Message

from bot.db.models import Category, Post, PostDraft, PostStatus
from bot.db.session import get_session
from bot.modules.posts.admin import is_admin
from bot.modules.posts.attachments import message_attachments_to_string
from bot.modules.posts.keyboards import (
    attachments_keyboard,
    categories_keyboard,
    confirm_keyboard,
    main_menu_keyboard,
    paid_keyboard,
)
from bot.modules.posts.subscriptions import get_or_create_user
from bot.vk_client import api
from bot.vk_utils import new_random_id

PAID_LABEL = {True: "платное", False: "бесплатное"}
STATUS_LABEL = {
    PostStatus.PENDING: "на модерации",
    PostStatus.ACTIVE: "активно",
    PostStatus.REJECTED: "отклонено",
    PostStatus.PAUSED: "приостановлено (нет подписки)",
    PostStatus.FROZEN: "ждёт вашего подтверждения",
    PostStatus.DELETED: "удалено",
}


async def show_main_menu(message: Message) -> None:
    async with get_session() as session:
        await get_or_create_user(session, api, message.from_id)
    await message.answer(
        "Здравствуйте! Выберите действие:",
        keyboard=main_menu_keyboard(is_admin(message.from_id)),
    )


async def cmd_my_posts(message: Message) -> None:
    async with get_session() as session:
        posts = (
            await session.execute(
                select(Post).where(Post.author_vk_id == message.from_id).order_by(Post.created_at.desc())
            )
        ).scalars().all()

    if not posts:
        await message.answer(
            "У вас пока нет поданных объявлений.",
            keyboard=main_menu_keyboard(is_admin(message.from_id)),
        )
        return

    lines = []
    for post in posts:
        preview = post.text[:60] + ("…" if len(post.text) > 60 else "")
        lines.append(f"#{post.id} [{STATUS_LABEL[post.status]}] {preview}")
    await message.answer("\n".join(lines), keyboard=main_menu_keyboard(is_admin(message.from_id)))


async def cmd_new_post(message: Message) -> None:
    async with get_session() as session:
        await get_or_create_user(session, api, message.from_id)
        categories = (await session.execute(select(Category))).scalars().all()
        if not categories:
            await message.answer(
                "Список категорий пока пуст. Попросите администратора добавить категории в админ-панели.",
                keyboard=main_menu_keyboard(is_admin(message.from_id)),
            )
            return

        draft = await session.get(PostDraft, message.from_id)
        if draft is None:
            draft = PostDraft(user_vk_id=message.from_id, step="category")
            session.add(draft)
        else:
            draft.step = "category"
            draft.category_id = None
            draft.is_paid = None
            draft.text = ""
            draft.attachments = ""
            draft.editing_post_id = None
        await session.commit()

    await message.answer("Выберите категорию объявления:", keyboard=categories_keyboard(categories))


async def cmd_category(message: Message, category_id: int) -> None:
    async with get_session() as session:
        draft = await session.get(PostDraft, message.from_id)
        if draft is None or draft.step != "category":
            await show_main_menu(message)
            return
        category = await session.get(Category, category_id)
        if category is None:
            await message.answer("Такой категории не существует, выберите из списка.")
            return
        draft.step = "paid"
        draft.category_id = category_id
        await session.commit()

    await message.answer("Объявление платное или бесплатное?", keyboard=paid_keyboard())


async def cmd_paid(message: Message, value: bool) -> None:
    async with get_session() as session:
        draft = await session.get(PostDraft, message.from_id)
        if draft is None or draft.step != "paid":
            await show_main_menu(message)
            return
        draft.step = "text"
        draft.is_paid = value
        await session.commit()

    await message.answer("Введите текст объявления одним сообщением:")


async def handle_text_step(message: Message) -> None:
    if not message.text:
        await message.answer("Пришлите текст объявления сообщением.")
        return
    async with get_session() as session:
        draft = await session.get(PostDraft, message.from_id)
        if draft is None:
            return
        draft.text = message.text
        draft.step = "confirm" if draft.editing_post_id is not None else "attachments"
        await session.commit()
        if draft.editing_post_id is not None:
            await send_confirmation(message, draft)
            return

    await message.answer(
        "Прикрепите фото следующим сообщением или нажмите «Без фото».",
        keyboard=attachments_keyboard(),
    )


async def cmd_skip_attachments(message: Message) -> None:
    async with get_session() as session:
        draft = await session.get(PostDraft, message.from_id)
        if draft is None or draft.step != "attachments":
            await show_main_menu(message)
            return
        draft.attachments = ""
        draft.step = "confirm"
        await session.commit()
        await send_confirmation(message, draft)


async def handle_attachments_step(message: Message) -> None:
    attachments = message_attachments_to_string(message)
    if not attachments:
        await message.answer("Не вижу фото во вложении. Пришлите фото или нажмите «Без фото».")
        return
    async with get_session() as session:
        draft = await session.get(PostDraft, message.from_id)
        if draft is None:
            return
        draft.attachments = attachments
        draft.step = "confirm"
        await session.commit()
        await send_confirmation(message, draft)


async def send_confirmation(message: Message, draft: PostDraft) -> None:
    async with get_session() as session:
        category = await session.get(Category, draft.category_id)
    category_name = category.name if category else "?"
    paid_label = PAID_LABEL.get(draft.is_paid, "?")
    photos_label = "есть" if draft.attachments else "нет"
    summary = (
        f"Проверьте объявление:\n"
        f"Категория: {category_name}\n"
        f"Тип: {paid_label}\n"
        f"Фото: {photos_label}\n\n"
        f"{draft.text}"
    )
    await message.answer(summary, keyboard=confirm_keyboard())


async def cmd_cancel(message: Message) -> None:
    async with get_session() as session:
        draft = await session.get(PostDraft, message.from_id)
        if draft is not None:
            await session.delete(draft)
            await session.commit()
    await message.answer("Подача объявления отменена.", keyboard=main_menu_keyboard(is_admin(message.from_id)))


async def cmd_confirm(message: Message) -> None:
    from bot.modules.posts.admin import notify_admins_new_post

    async with get_session() as session:
        draft = await session.get(PostDraft, message.from_id)
        if draft is None or draft.step != "confirm":
            await show_main_menu(message)
            return

        if draft.editing_post_id is not None:
            post = await session.get(Post, draft.editing_post_id)
            post.text = draft.text
            post.attachments = draft.attachments
            post.status = PostStatus.ACTIVE
            post.last_renewed_at = datetime.utcnow()
            post.frozen_at = None
            await session.delete(draft)
            await session.commit()
            await message.answer(
                "Объявление обновлено и продолжает публиковаться.",
                keyboard=main_menu_keyboard(is_admin(message.from_id)),
            )
            return

        post = Post(
            author_vk_id=message.from_id,
            category_id=draft.category_id,
            is_paid=bool(draft.is_paid),
            text=draft.text,
            attachments=draft.attachments,
            status=PostStatus.PENDING,
        )
        session.add(post)
        await session.delete(draft)
        await session.commit()
        await session.refresh(post)
        post_id = post.id

    await message.answer(
        "Объявление отправлено на модерацию, ожидайте решения администратора.",
        keyboard=main_menu_keyboard(is_admin(message.from_id)),
    )
    await notify_admins_new_post(post_id)


async def cmd_freeze_continue(message: Message, post_id: int) -> None:
    async with get_session() as session:
        post = await session.get(Post, post_id)
        if post is None or post.author_vk_id != message.from_id:
            return
        post.status = PostStatus.ACTIVE
        post.frozen_at = None
        post.last_renewed_at = datetime.utcnow()
        await session.commit()
    await message.answer("Публикация объявления продолжена.", keyboard=main_menu_keyboard(is_admin(message.from_id)))


async def cmd_freeze_delete(message: Message, post_id: int) -> None:
    async with get_session() as session:
        post = await session.get(Post, post_id)
        if post is None or post.author_vk_id != message.from_id:
            return
        post.status = PostStatus.DELETED
        await session.commit()
    await message.answer("Объявление удалено.", keyboard=main_menu_keyboard(is_admin(message.from_id)))


async def cmd_freeze_edit(message: Message, post_id: int) -> None:
    async with get_session() as session:
        post = await session.get(Post, post_id)
        if post is None or post.author_vk_id != message.from_id:
            return
        draft = await session.get(PostDraft, message.from_id)
        if draft is None:
            draft = PostDraft(user_vk_id=message.from_id)
            session.add(draft)
        draft.step = "text"
        draft.category_id = post.category_id
        draft.is_paid = post.is_paid
        draft.text = ""
        draft.attachments = post.attachments
        draft.editing_post_id = post.id
        await session.commit()
    await message.answer("Введите новый текст объявления одним сообщением:")
