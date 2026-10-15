from __future__ import annotations

from vkbottle import Keyboard, KeyboardButtonColor, Text

from bot.db.models import Category, NotificationEvent

# Все клавиатуры сделаны обычными (inline=False), а не inline-кнопками VK.
# Обычная кнопка при нажатии присылает боту новое сообщение с payload — это
# обрабатывается тем же универсальным message-хендлером, что и остальной ввод,
# и не требует отдельной обработки message_event/sendMessageEventAnswer.


def _menu(items: list[tuple[str, dict, KeyboardButtonColor]], one_time: bool = True) -> str:
    """items — список (подпись, payload, цвет). Общий конструктор для меню-клавиатур,
    в отличие от клавиатур визарда объявления (ниже), у которых своя специфика."""
    kb = Keyboard(inline=False, one_time=one_time)
    for i, (label, payload, color) in enumerate(items):
        if i:
            kb.row()
        kb.add(Text(label, payload=payload), color=color)
    return kb.get_json()


def main_menu_keyboard(is_admin: bool) -> str:
    items = [
        ("📢 Подать объявление", {"cmd": "new_post"}, KeyboardButtonColor.PRIMARY),
        ("📋 Мои объявления", {"cmd": "my_posts"}, KeyboardButtonColor.SECONDARY),
    ]
    if is_admin:
        items.append(("🛠 Админ-панель", {"cmd": "admin_panel"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)


# Ключи и подписи по умолчанию для пунктов админ-панели верхнего уровня.
# "Категории" и "Источники" сюда не входят — начиная с объединения этих двух
# пунктов в один раздел ("Заимствование контента") они находятся не здесь, а в
# CONTENT_MENU_DEFAULTS/content_menu_keyboard() ниже.
MENU_LABEL_DEFAULTS = {
    "admin_moderation": "🗂 Модерация",
    "admin_settings": "📋 Регламент по бесплатным публикациям",
    "admin_content": "🔁 Заимствование контента",
    "admin_report_start": "📊 Анализ конкурентов",
    "admin_notifications": "🔔 Мои уведомления",
    "admin_audience": "🎯 Аудитория конкурентов",
}


def admin_panel_keyboard(labels: dict[str, str] | None = None) -> str:
    labels = labels or MENU_LABEL_DEFAULTS
    items = [
        (labels.get(cmd, default), {"cmd": cmd}, KeyboardButtonColor.PRIMARY)
        for cmd, default in MENU_LABEL_DEFAULTS.items()
    ]
    items.append(("✏️ Названия разделов", {"cmd": "admin_labels"}, KeyboardButtonColor.SECONDARY))
    items.append(("⬅️ В главное меню", {"cmd": "menu_main"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)


# Пункты внутри объединённого раздела "Заимствование контента" (бывшие отдельные
# кнопки "🏷 Категории" и "🔁 Источники (агрегатор)" на верхнем уровне админ-панели).
# cmd у каждого пункта не изменился — изменилось только то, откуда до него
# добираются (через admin_content, а не напрямую с админ-панели) и подпись по
# умолчанию.
CONTENT_MENU_DEFAULTS = {
    "admin_categories": "🔎 Поиск постов по ключевым словам",
    "admin_sources": "📥 С каких пабликов были взяты посты",
}


def content_menu_keyboard(labels: dict[str, str] | None = None) -> str:
    labels = labels or CONTENT_MENU_DEFAULTS
    items = [
        (labels.get(cmd, default), {"cmd": cmd}, KeyboardButtonColor.PRIMARY)
        for cmd, default in CONTENT_MENU_DEFAULTS.items()
    ]
    items.append(("⬅️ Назад", {"cmd": "admin_panel"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)


SETTING_LABELS = {
    "renewal_interval_days": "📅 Срок активности поста до заморозки",
    "freeze_response_days": "⏱ Срок ответа до удаления из системы",
    "post_frequency_minutes": "🔁 Частота публикации",
    "aggregator_posts_per_cycle": "📥 Сколько постов в день у конкурентов",
    "aggregator_max_age_hours": "🕒 Не брать посты конкурента старше",
    "aggregator_repost_ttl_days": "♻️ Повтор поста конкурента через",
}

DAY_PRESETS = [1, 3, 7, 14, 30]

# Единица измерения и набор пресетов для каждой настройки — не у всех дни, как
# было раньше (см. show_settings_menu/show_days_options/cmd_set_days в admin.py,
# которые раньше жёстко писали "дн." для любого ключа). post_frequency_minutes
# сюда не входит — у неё отдельный UX (frequency_preset_keyboard и т.д. ниже),
# т.к. админу удобнее думать "раз в неделю", а не в сырых минутах.
UNIT_LABELS = {
    "aggregator_posts_per_cycle": "шт.",
    "aggregator_max_age_hours": "ч.",
}

PRESETS_BY_KEY = {
    "aggregator_posts_per_cycle": [1, 3, 5, 10, 20],
    "aggregator_max_age_hours": [6, 12, 24, 48, 72],
    "aggregator_repost_ttl_days": [1, 3, 7, 14, 30],
}

# --- Частота публикации (post_frequency_minutes), UX в терминах "раз в неделю" ---
# Хранится в БД по-прежнему в минутах (это то, чем оперирует auto_publish в jobs.py),
# но админ выбирает "сколько раз в неделю" — 10080 мин. (7 дн.) делится без остатка
# на большинство разумных значений 1..7 и кратных, поэтому конвертация точная.
MINUTES_PER_WEEK = 7 * 24 * 60

FREQUENCY_PRESETS_PER_WEEK = [1, 2, 3, 5, 7]  # 7 = "Каждый день"


def _times_word(n: int) -> str:
    if n % 10 == 1 and n % 100 != 11:
        return "раз"
    if 2 <= n % 10 <= 4 and not 11 <= n % 100 <= 14:
        return "раза"
    return "раз"


def frequency_label(times_per_week: int) -> str:
    if times_per_week == 7:
        return "Каждый день"
    return f"{times_per_week} {_times_word(times_per_week)} в неделю"


def frequency_minutes(times_per_week: int) -> int:
    times_per_week = max(1, times_per_week)
    return max(1, round(MINUTES_PER_WEEK / times_per_week))


def frequency_times_per_week(minutes: int) -> int:
    if minutes <= 0:
        return 1
    return max(1, round(MINUTES_PER_WEEK / minutes))


def frequency_preset_keyboard() -> str:
    items = [
        (frequency_label(n), {"cmd": "admin_set_frequency", "value": n}, KeyboardButtonColor.PRIMARY)
        for n in FREQUENCY_PRESETS_PER_WEEK
    ]
    items.append(("Своё значение", {"cmd": "admin_set_frequency_custom"}, KeyboardButtonColor.SECONDARY))
    items.append(("⬅️ Назад", {"cmd": "admin_settings"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=True)

TEXT_KEY_LABELS = {
    "text_renewal_reminder": "Напоминание о продлении",
    "text_freeze_deleted": "Удаление после заморозки",
    "text_unsubscribed": "Отписка от сообщества",
    "text_resubscribed": "Повторная подписка",
    "text_rejected": "Отклонение объявления",
    "text_approved": "Одобрение объявления",
}


def settings_menu_keyboard(labels: dict[str, str] | None = None) -> str:
    labels = labels or SETTING_LABELS
    items = [
        (labels.get(key, default), {"cmd": "admin_setting", "key": key}, KeyboardButtonColor.PRIMARY)
        for key, default in SETTING_LABELS.items()
    ]
    items.append(("✏️ Тексты уведомлений", {"cmd": "admin_texts"}, KeyboardButtonColor.PRIMARY))
    items.append(("⬅️ Назад", {"cmd": "admin_panel"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)


def days_preset_keyboard(key: str) -> str:
    items = [
        (str(d), {"cmd": "admin_set_days", "key": key, "value": d}, KeyboardButtonColor.PRIMARY)
        for d in PRESETS_BY_KEY.get(key, DAY_PRESETS)
    ]
    items.append(("Своё значение", {"cmd": "admin_set_days_custom", "key": key}, KeyboardButtonColor.SECONDARY))
    items.append(("⬅️ Назад", {"cmd": "admin_settings"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=True)


def text_keys_keyboard(labels: dict[str, str] | None = None) -> str:
    labels = labels or TEXT_KEY_LABELS
    items = [
        (labels.get(key, default), {"cmd": "admin_edit_text", "key": key}, KeyboardButtonColor.PRIMARY)
        for key, default in TEXT_KEY_LABELS.items()
    ]
    items.append(("⬅️ Назад", {"cmd": "admin_settings"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)


NOTIF_EVENT_LABELS = {
    NotificationEvent.NEW_SUBSCRIBER: "🆕 Новые подписки",
    NotificationEvent.NEW_UNSUBSCRIBER: "🚪 Отписки",
    NotificationEvent.NEW_COMMENT: "💬 Комментарии на стене",
    NotificationEvent.NEW_LIKE: "👍 Лайки на постах",
    NotificationEvent.NEW_MESSAGE: "✉️ Сообщения от пользователей",
}


def notifications_menu_keyboard(
    states: dict[NotificationEvent, bool], labels: dict[str, str] | None = None
) -> str:
    items = [
        (
            f"{'✅' if states.get(event, True) else '⛔'} {(labels or {}).get(event.value, default)}",
            {"cmd": "admin_notif_toggle", "event": event.value},
            KeyboardButtonColor.PRIMARY,
        )
        for event, default in NOTIF_EVENT_LABELS.items()
    ]
    items.append(("⬅️ Назад", {"cmd": "admin_panel"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)


def categories_admin_keyboard() -> str:
    items = [
        ("➕ Добавить категорию", {"cmd": "admin_add_category"}, KeyboardButtonColor.POSITIVE),
        ("✏️ Переименовать категорию", {"cmd": "admin_rename_category_menu"}, KeyboardButtonColor.PRIMARY),
        ("⬅️ Назад", {"cmd": "admin_content"}, KeyboardButtonColor.SECONDARY),
    ]
    return _menu(items, one_time=False)


def category_pick_keyboard(categories: list[Category]) -> str:
    items = [
        (c.name, {"cmd": "admin_sources_add_category", "id": c.id}, KeyboardButtonColor.PRIMARY) for c in categories
    ]
    items.append(("⬅️ Отмена", {"cmd": "admin_sources"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=True)


def category_rename_pick_keyboard(categories: list[Category]) -> str:
    items = [
        (c.name, {"cmd": "admin_rename_category_pick", "id": c.id}, KeyboardButtonColor.PRIMARY) for c in categories
    ]
    items.append(("⬅️ Отмена", {"cmd": "admin_categories"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=True)


def sources_admin_keyboard() -> str:
    items = [
        ("➕ Добавить источник", {"cmd": "admin_sources_add"}, KeyboardButtonColor.POSITIVE),
        ("🗑 Удалить источник", {"cmd": "admin_sources_remove_menu"}, KeyboardButtonColor.NEGATIVE),
        ("⬅️ Назад", {"cmd": "admin_content"}, KeyboardButtonColor.SECONDARY),
    ]
    return _menu(items, one_time=False)


def sources_remove_keyboard(sources) -> str:
    items = [
        (s.name or f"#{s.id}", {"cmd": "admin_sources_remove", "id": s.id}, KeyboardButtonColor.NEGATIVE)
        for s in sources
    ]
    items.append(("⬅️ Назад", {"cmd": "admin_sources"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=True)


def categories_keyboard(categories: list[Category]) -> str:
    kb = Keyboard(inline=False, one_time=True)
    for i, category in enumerate(categories):
        if i:
            kb.row()
        kb.add(Text(category.name, payload={"cmd": "category", "id": category.id}))
    return kb.get_json()


def paid_keyboard() -> str:
    kb = Keyboard(inline=False, one_time=True)
    kb.add(Text("Платное", payload={"cmd": "paid", "value": True}), color=KeyboardButtonColor.POSITIVE)
    kb.row()
    kb.add(Text("Бесплатное", payload={"cmd": "paid", "value": False}), color=KeyboardButtonColor.SECONDARY)
    return kb.get_json()


def attachments_keyboard() -> str:
    kb = Keyboard(inline=False, one_time=True)
    kb.add(Text("Без фото", payload={"cmd": "skip_attachments"}), color=KeyboardButtonColor.SECONDARY)
    return kb.get_json()


def confirm_keyboard() -> str:
    kb = Keyboard(inline=False, one_time=True)
    kb.add(Text("Отправить на модерацию", payload={"cmd": "confirm"}), color=KeyboardButtonColor.POSITIVE)
    kb.row()
    kb.add(Text("Отмена", payload={"cmd": "cancel"}), color=KeyboardButtonColor.NEGATIVE)
    return kb.get_json()


def moderation_keyboard(post_id: int) -> str:
    kb = Keyboard(inline=False, one_time=True)
    kb.add(Text("Одобрить", payload={"cmd": "approve", "post_id": post_id}), color=KeyboardButtonColor.POSITIVE)
    kb.row()
    kb.add(Text("Отклонить", payload={"cmd": "reject", "post_id": post_id}), color=KeyboardButtonColor.NEGATIVE)
    return kb.get_json()


AUDIENCE_CRITERIA_LABELS = {
    "min_friends": "👥 Мин. число друзей",
    "min_followers": "📣 Мин. число подписчиков",
    "cities": "🏙 Города (через запятую)",
    "keywords": "🔑 Ключевые слова в подписках",
}


def admin_audience_keyboard() -> str:
    items = [
        ("📋 Кандидаты", {"cmd": "admin_audience_candidates"}, KeyboardButtonColor.PRIMARY),
        ("⚙️ Критерии фильтра", {"cmd": "admin_audience_criteria"}, KeyboardButtonColor.PRIMARY),
        ("⬅️ Назад", {"cmd": "admin_panel"}, KeyboardButtonColor.SECONDARY),
    ]
    return _menu(items, one_time=False)


def audience_criteria_keyboard(labels: dict[str, str] | None = None) -> str:
    labels = labels or AUDIENCE_CRITERIA_LABELS
    items = [
        (labels.get(key, default), {"cmd": "admin_audience_edit", "key": key}, KeyboardButtonColor.PRIMARY)
        for key, default in AUDIENCE_CRITERIA_LABELS.items()
    ]
    items.append(("⬅️ Назад", {"cmd": "admin_audience"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)


def candidate_card_keyboard(vk_id: int) -> str:
    kb = Keyboard(inline=False, one_time=True)
    kb.add(
        Text("✅ Обработал(а)", payload={"cmd": "admin_audience_mark", "vk_id": vk_id, "status": "contacted"}),
        color=KeyboardButtonColor.POSITIVE,
    )
    kb.row()
    kb.add(
        Text("🗑 Пропустить", payload={"cmd": "admin_audience_mark", "vk_id": vk_id, "status": "dismissed"}),
        color=KeyboardButtonColor.NEGATIVE,
    )
    return kb.get_json()


def freeze_keyboard(post_id: int) -> str:
    kb = Keyboard(inline=False, one_time=True)
    kb.add(
        Text("Продолжить", payload={"cmd": "freeze_continue", "post_id": post_id}),
        color=KeyboardButtonColor.POSITIVE,
    )
    kb.row()
    kb.add(
        Text("Редактировать", payload={"cmd": "freeze_edit", "post_id": post_id}),
        color=KeyboardButtonColor.PRIMARY,
    )
    kb.row()
    kb.add(
        Text("Удалить", payload={"cmd": "freeze_delete", "post_id": post_id}),
        color=KeyboardButtonColor.NEGATIVE,
    )
    return kb.get_json()


# --- "✏️ Названия разделов" — редактирование подписей из групп выше одним общим
# UI (bot/modules/posts/admin.py::show_label_groups/show_label_group/prompt_edit_label).
# Группа "content" тут — это CONTENT_MENU_DEFAULTS (см. выше), не сама категория
# объявлений: переименование конкретных категорий — отдельный сценарий
# (category_rename_pick_keyboard), т.к. категории хранятся как строки в БД, а не
# как хардкод-подписи.
LABEL_GROUPS: dict[str, tuple[str, dict[str, str]]] = {
    "menu": ("Разделы админ-панели", MENU_LABEL_DEFAULTS),
    "content": ("Заимствование контента", CONTENT_MENU_DEFAULTS),
    "settings": ("Регламент по бесплатным публикациям", SETTING_LABELS),
    "texts": ("Названия текстов уведомлений", TEXT_KEY_LABELS),
    "notifications": ("Мои уведомления", {e.value: label for e, label in NOTIF_EVENT_LABELS.items()}),
    "audience": ("Критерии аудитории конкурентов", AUDIENCE_CRITERIA_LABELS),
}


def label_groups_keyboard() -> str:
    items = [
        (title, {"cmd": "admin_label_group", "group": group}, KeyboardButtonColor.PRIMARY)
        for group, (title, _defaults) in LABEL_GROUPS.items()
    ]
    items.append(("⬅️ Назад", {"cmd": "admin_panel"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)


def label_items_keyboard(group: str, current: dict[str, str]) -> str:
    _title, defaults = LABEL_GROUPS[group]
    items = [
        (current.get(key, default), {"cmd": "admin_label_edit", "group": group, "key": key}, KeyboardButtonColor.PRIMARY)
        for key, default in defaults.items()
    ]
    items.append(("⬅️ Назад", {"cmd": "admin_labels"}, KeyboardButtonColor.SECONDARY))
    return _menu(items, one_time=False)
