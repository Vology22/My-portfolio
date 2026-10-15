from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from vkbottle.bot import Message

from bot.admin_draft import clear_draft, draft_data, set_draft
from bot.config import settings
from bot.db.models import AdminDraft, Category, NotificationEvent, Post, PostStatus, User
from bot.db.session import get_session
from bot.db.settings_repo import get_int_setting, get_label, get_setting, set_setting
from bot.modules.posts.keyboards import (
    LABEL_GROUPS,
    MENU_LABEL_DEFAULTS,
    SETTING_LABELS,
    TEXT_KEY_LABELS,
    UNIT_LABELS,
    admin_panel_keyboard,
    categories_admin_keyboard,
    category_rename_pick_keyboard,
    days_preset_keyboard,
    frequency_label,
    frequency_minutes,
    frequency_preset_keyboard,
    frequency_times_per_week,
    label_groups_keyboard,
    label_items_keyboard,
    moderation_keyboard,
    notifications_menu_keyboard,
    settings_menu_keyboard,
    text_keys_keyboard,
)
from bot.modules.posts.notifications import is_notification_enabled, toggle_notification
from bot.vk_client import api
from bot.vk_utils import new_random_id


def is_admin(user_id: int) -> bool:
    return user_id in settings.admin_ids


PAID_LABEL = {True: "платное", False: "бесплатное"}

FREQUENCY_KEY = "post_frequency_minutes"


def label_setting_key(group: str, key: str) -> str:
    """Ключ в таблице settings для редактируемой подписи раздела/кнопки — не
    путать с ключами самих настроек (renewal_interval_days и т.п.) или текстов
    уведомлений (text_*), у которых своё пространство ключей."""
    return f"label_{group}_{key}"


async def resolve_labels(session, group: str) -> dict[str, str]:
    _title, defaults = LABEL_GROUPS[group]
    return {key: await get_label(session, label_setting_key(group, key), default) for key, default in defaults.items()}


async def _setting_label(session, key: str) -> str:
    return await get_label(session, label_setting_key("settings", key), SETTING_LABELS[key])


async def notify_admins_new_post(post_id: int) -> None:
    async with get_session() as session:
        post = await session.get(Post, post_id)
        category = await session.get(Category, post.category_id)
        author = await session.get(User, post.author_vk_id)

    subscribed_label = "✅ подписан" if author and author.is_subscribed else "❌ не подписан"
    text = (
        f"Новое объявление #{post.id} на модерацию\n"
        f"Категория: {category.name if category else '?'}\n"
        f"Тип: {PAID_LABEL.get(post.is_paid, '?')}\n"
        f"Автор подписан на сообщество: {subscribed_label}\n\n"
        f"{post.text}"
    )
    for admin_id in settings.admin_ids:
        await api.messages.send(
            user_id=admin_id,
            message=text,
            attachment=post.attachments or None,
            keyboard=moderation_keyboard(post.id),
            random_id=new_random_id(),
        )


async def cmd_approve(message: Message, post_id: int) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        post = await session.get(Post, post_id)
        if post is None:
            await message.answer("Объявление не найдено.", keyboard=admin_panel_keyboard())
            return
        post.status = PostStatus.ACTIVE
        post.approved_at = datetime.utcnow()
        post.last_renewed_at = datetime.utcnow()
        author_id = post.author_vk_id
        text = await get_setting(session, "text_approved")
        await session.commit()

    await message.answer(f"Объявление #{post_id} одобрено.", keyboard=admin_panel_keyboard())
    await api.messages.send(user_id=author_id, message=text, random_id=new_random_id())


async def cmd_reject(message: Message, post_id: int) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        post = await session.get(Post, post_id)
        if post is None:
            await message.answer("Объявление не найдено.", keyboard=admin_panel_keyboard())
            return
        post.status = PostStatus.REJECTED
        author_id = post.author_vk_id
        text = await get_setting(session, "text_rejected")
        await session.commit()

    await message.answer(f"Объявление #{post_id} отклонено.", keyboard=admin_panel_keyboard())
    await api.messages.send(user_id=author_id, message=text, random_id=new_random_id())


async def show_admin_panel(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        labels = await resolve_labels(session, "menu")
    await message.answer("Админ-панель:", keyboard=admin_panel_keyboard(labels))


async def show_moderation_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        posts = (
            await session.execute(select(Post).where(Post.status == PostStatus.PENDING))
        ).scalars().all()

    if not posts:
        await message.answer("Очередь модерации пуста.", keyboard=admin_panel_keyboard())
        return

    for post in posts:
        await message.answer(
            f"#{post.id}: {post.text[:80]}",
            keyboard=moderation_keyboard(post.id),
        )


def _format_setting_value(key: str, raw_value: int) -> str:
    if key == FREQUENCY_KEY:
        return frequency_label(frequency_times_per_week(raw_value))
    return f"{raw_value} {UNIT_LABELS.get(key, 'дн.')}"


async def show_settings_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        labels = await resolve_labels(session, "settings")
        title = (await resolve_labels(session, "menu")).get("admin_settings", MENU_LABEL_DEFAULTS["admin_settings"])
        lines = [
            f"{label}: {_format_setting_value(key, await get_int_setting(session, key))}"
            for key, label in labels.items()
        ]
    await message.answer(
        f"{title}:\n" + "\n".join(lines),
        keyboard=settings_menu_keyboard(labels),
    )


async def show_days_options(message: Message, key: str) -> None:
    if not is_admin(message.from_id):
        return
    if key not in SETTING_LABELS:
        return
    if key == FREQUENCY_KEY:
        await show_frequency_options(message)
        return
    async with get_session() as session:
        current = await get_int_setting(session, key)
        label = await _setting_label(session, key)
    unit = UNIT_LABELS.get(key, "дн.")
    await message.answer(
        f"{label}\nТекущее значение: {current} {unit}\nВыберите новое:",
        keyboard=days_preset_keyboard(key),
    )


async def show_frequency_options(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        current_minutes = await get_int_setting(session, FREQUENCY_KEY)
        label = await _setting_label(session, FREQUENCY_KEY)
    current_label = frequency_label(frequency_times_per_week(current_minutes))
    await message.answer(
        f"{label}\nСейчас: {current_label}\nВыберите новую частоту:",
        keyboard=frequency_preset_keyboard(),
    )


async def cmd_set_frequency(message: Message, times_per_week: int) -> None:
    if not is_admin(message.from_id):
        return
    times_per_week = max(1, int(times_per_week))
    minutes = frequency_minutes(times_per_week)
    async with get_session() as session:
        await set_setting(session, FREQUENCY_KEY, str(minutes))
        label = await _setting_label(session, FREQUENCY_KEY)
        labels = await resolve_labels(session, "settings")
    await message.answer(
        f"{label}: установлено — {frequency_label(times_per_week)}",
        keyboard=settings_menu_keyboard(labels),
    )


async def prompt_custom_frequency(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        await set_draft(session, message.from_id, "set_frequency_custom")
    await message.answer("Сколько раз в неделю публиковать объявление? Введите целое число сообщением:")


async def handle_set_frequency_custom_input(message: Message, draft: AdminDraft) -> None:
    raw = (message.text or "").strip()
    if not raw.isdigit() or int(raw) < 1:
        await message.answer("Введите целое положительное число (раз в неделю) сообщением.")
        return
    times_per_week = int(raw)
    minutes = frequency_minutes(times_per_week)
    async with get_session() as session:
        await set_setting(session, FREQUENCY_KEY, str(minutes))
        await clear_draft(session, message.from_id)
        label = await _setting_label(session, FREQUENCY_KEY)
        labels = await resolve_labels(session, "settings")
    await message.answer(
        f"{label}: установлено — {frequency_label(times_per_week)}",
        keyboard=settings_menu_keyboard(labels),
    )


async def cmd_set_days(message: Message, key: str, value: int) -> None:
    if not is_admin(message.from_id):
        return
    if key not in SETTING_LABELS:
        return
    async with get_session() as session:
        await set_setting(session, key, str(int(value)))
        label = await _setting_label(session, key)
        labels = await resolve_labels(session, "settings")
    unit = UNIT_LABELS.get(key, "дн.")
    await message.answer(f"{label}: установлено {value} {unit}", keyboard=settings_menu_keyboard(labels))


async def prompt_custom_days(message: Message, key: str) -> None:
    if not is_admin(message.from_id):
        return
    if key not in SETTING_LABELS:
        return
    async with get_session() as session:
        await set_draft(session, message.from_id, "set_days_custom", {"key": key})
    unit = UNIT_LABELS.get(key, "дней")
    await message.answer(f"Введите число ({unit}) сообщением, целым числом:")


async def handle_set_days_custom_input(message: Message, draft: AdminDraft) -> None:
    key = draft_data(draft).get("key")
    if key not in SETTING_LABELS or not (message.text or "").strip().isdigit():
        unit = UNIT_LABELS.get(key, "дней")
        await message.answer(f"Введите целое число ({unit}) сообщением.")
        return
    value = int(message.text.strip())
    async with get_session() as session:
        await set_setting(session, key, str(value))
        await clear_draft(session, message.from_id)
        label = await _setting_label(session, key)
        labels = await resolve_labels(session, "settings")
    unit = UNIT_LABELS.get(key, "дн.")
    await message.answer(f"{label}: установлено {value} {unit}", keyboard=settings_menu_keyboard(labels))


async def show_text_keys_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        labels = await resolve_labels(session, "texts")
    await message.answer("Какой текст изменить?", keyboard=text_keys_keyboard(labels))


async def prompt_edit_text(message: Message, key: str) -> None:
    if not is_admin(message.from_id):
        return
    if key not in TEXT_KEY_LABELS:
        return
    async with get_session() as session:
        current = await get_setting(session, key)
        await set_draft(session, message.from_id, "edit_text", {"key": key})
    await message.answer(f"Текущий текст:\n{current}\n\nПришлите новый текст сообщением:")


async def handle_edit_text_input(message: Message, draft: AdminDraft) -> None:
    key = draft_data(draft).get("key")
    if key not in TEXT_KEY_LABELS or not message.text:
        await message.answer("Пришлите текст сообщением.")
        return
    async with get_session() as session:
        await set_setting(session, key, message.text)
        await clear_draft(session, message.from_id)
        label = await get_label(session, label_setting_key("texts", key), TEXT_KEY_LABELS[key])
        labels = await resolve_labels(session, "texts")
    await message.answer(f"Текст «{label}» обновлён.", keyboard=text_keys_keyboard(labels))


async def show_notifications_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        states = {event: await is_notification_enabled(session, message.from_id, event) for event in NotificationEvent}
        labels = await resolve_labels(session, "notifications")
    await message.answer(
        "Ваши уведомления от бота (нажмите, чтобы включить/выключить):",
        keyboard=notifications_menu_keyboard(states, labels),
    )


async def cmd_toggle_notification(message: Message, event_value: str) -> None:
    if not is_admin(message.from_id):
        return
    try:
        event = NotificationEvent(event_value)
    except ValueError:
        return
    async with get_session() as session:
        await toggle_notification(session, message.from_id, event)
        states = {e: await is_notification_enabled(session, message.from_id, e) for e in NotificationEvent}
        labels = await resolve_labels(session, "notifications")
    await message.answer("Обновлено.", keyboard=notifications_menu_keyboard(states, labels))


async def show_categories_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        categories = (await session.execute(select(Category))).scalars().all()
    text = "\n".join(f"#{c.id} {c.name}" for c in categories) if categories else "Категорий пока нет."
    await message.answer(text, keyboard=categories_admin_keyboard())


async def prompt_add_category(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        await set_draft(session, message.from_id, "add_category")
    await message.answer("Введите название новой категории сообщением:")


async def handle_add_category_input(message: Message, draft: AdminDraft) -> None:
    name = (message.text or "").strip()
    if not name:
        await message.answer("Пришлите название категории сообщением.")
        return
    async with get_session() as session:
        existing = (
            await session.execute(select(Category).where(Category.name == name))
        ).scalar_one_or_none()
        if existing is not None:
            await clear_draft(session, message.from_id)
            await message.answer("Такая категория уже есть.", keyboard=categories_admin_keyboard())
            return
        session.add(Category(name=name))
        await clear_draft(session, message.from_id)
    await message.answer(f"Категория «{name}» добавлена.", keyboard=categories_admin_keyboard())


async def prompt_rename_category_menu(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        categories = (await session.execute(select(Category))).scalars().all()
    if not categories:
        await message.answer("Категорий пока нет.", keyboard=categories_admin_keyboard())
        return
    await message.answer("Какую категорию переименовать?", keyboard=category_rename_pick_keyboard(categories))


async def cmd_rename_category_pick(message: Message, category_id: int) -> None:
    if not is_admin(message.from_id):
        return
    async with get_session() as session:
        category = await session.get(Category, category_id)
        if category is None:
            await message.answer("Такой категории не существует.", keyboard=categories_admin_keyboard())
            return
        await set_draft(session, message.from_id, "rename_category", {"category_id": category_id})
    await message.answer(f"Текущее название: «{category.name}»\nВведите новое название сообщением:")


async def handle_rename_category_input(message: Message, draft: AdminDraft) -> None:
    name = (message.text or "").strip()
    category_id = draft_data(draft).get("category_id")
    if not name:
        await message.answer("Пришлите название категории сообщением.")
        return
    async with get_session() as session:
        category = await session.get(Category, category_id)
        if category is None:
            await clear_draft(session, message.from_id)
            await message.answer("Категория не найдена.", keyboard=categories_admin_keyboard())
            return
        existing = (
            await session.execute(select(Category).where(Category.name == name, Category.id != category_id))
        ).scalar_one_or_none()
        if existing is not None:
            await message.answer("Категория с таким названием уже есть, введите другое.")
            return
        old_name = category.name
        category.name = name
        await clear_draft(session, message.from_id)
    await message.answer(f"Категория «{old_name}» переименована в «{name}».", keyboard=categories_admin_keyboard())


async def show_label_groups(message: Message) -> None:
    if not is_admin(message.from_id):
        return
    await message.answer("Какие названия изменить?", keyboard=label_groups_keyboard())


async def show_label_group(message: Message, group: str) -> None:
    if not is_admin(message.from_id):
        return
    if group not in LABEL_GROUPS:
        return
    title, _defaults = LABEL_GROUPS[group]
    async with get_session() as session:
        current = await resolve_labels(session, group)
    await message.answer(f"{title} — нажмите на пункт, чтобы переименовать:", keyboard=label_items_keyboard(group, current))


async def prompt_edit_label(message: Message, group: str, key: str) -> None:
    if not is_admin(message.from_id):
        return
    if group not in LABEL_GROUPS or key not in LABEL_GROUPS[group][1]:
        return
    async with get_session() as session:
        current = await get_label(session, label_setting_key(group, key), LABEL_GROUPS[group][1][key])
        await set_draft(session, message.from_id, "edit_label", {"group": group, "key": key})
    await message.answer(f"Текущее название: «{current}»\nПришлите новое название сообщением:")


async def handle_edit_label_input(message: Message, draft: AdminDraft) -> None:
    data = draft_data(draft)
    group, key = data.get("group"), data.get("key")
    name = (message.text or "").strip()
    if group not in LABEL_GROUPS or key not in LABEL_GROUPS[group][1] or not name:
        await message.answer("Пришлите новое название сообщением.")
        return
    async with get_session() as session:
        await set_setting(session, label_setting_key(group, key), name)
        await clear_draft(session, message.from_id)
        current = await resolve_labels(session, group)
    await message.answer(f"Название обновлено: «{name}».", keyboard=label_items_keyboard(group, current))
