from __future__ import annotations

from vkbottle.bot import BotLabeler, Message

from bot.db.models import AdminDraft, NotificationEvent, PostDraft
from bot.db.session import get_session
from bot.modules.aggregator import admin as aggregator_admin
from bot.modules.audience import admin as audience_admin
from bot.modules.competitors import admin as competitors_admin
from bot.modules.posts import admin, client
from bot.modules.posts.notifications import notify_admins

# Единая точка входа для ВСЕГО, что не является слэш-командой (их в проекте больше
# нет — весь интерфейс кнопочный): нажатия кнопок (VK присылает их как обычное
# сообщение с заполненным message.payload) и продолжение многошаговых диалогов
# (визард объявления — PostDraft; админские сценарии — AdminDraft).
#
# ВАЖНО: этот labeler — единственный в проекте и должен оставаться единственным
# message-обработчиком (см. main.py) — если когда-то потребуется вернуть текстовые
# команды, их labeler нужно грузить ДО этого, иначе catch-all перехватит всё.
bl = BotLabeler()

PAYLOAD_HANDLERS = {
    "new_post": lambda message, payload: client.cmd_new_post(message),
    "my_posts": lambda message, payload: client.cmd_my_posts(message),
    "category": lambda message, payload: client.cmd_category(message, payload["id"]),
    "paid": lambda message, payload: client.cmd_paid(message, payload["value"]),
    "skip_attachments": lambda message, payload: client.cmd_skip_attachments(message),
    "confirm": lambda message, payload: client.cmd_confirm(message),
    "cancel": lambda message, payload: client.cmd_cancel(message),
    "approve": lambda message, payload: admin.cmd_approve(message, payload["post_id"]),
    "reject": lambda message, payload: admin.cmd_reject(message, payload["post_id"]),
    "freeze_continue": lambda message, payload: client.cmd_freeze_continue(message, payload["post_id"]),
    "freeze_delete": lambda message, payload: client.cmd_freeze_delete(message, payload["post_id"]),
    "freeze_edit": lambda message, payload: client.cmd_freeze_edit(message, payload["post_id"]),
    "menu_main": lambda message, payload: client.show_main_menu(message),
    "admin_panel": lambda message, payload: admin.show_admin_panel(message),
    "admin_moderation": lambda message, payload: admin.show_moderation_menu(message),
    "admin_settings": lambda message, payload: admin.show_settings_menu(message),
    "admin_setting": lambda message, payload: admin.show_days_options(message, payload["key"]),
    "admin_set_days": lambda message, payload: admin.cmd_set_days(message, payload["key"], payload["value"]),
    "admin_set_days_custom": lambda message, payload: admin.prompt_custom_days(message, payload["key"]),
    "admin_set_frequency": lambda message, payload: admin.cmd_set_frequency(message, payload["value"]),
    "admin_set_frequency_custom": lambda message, payload: admin.prompt_custom_frequency(message),
    "admin_texts": lambda message, payload: admin.show_text_keys_menu(message),
    "admin_edit_text": lambda message, payload: admin.prompt_edit_text(message, payload["key"]),
    "admin_content": lambda message, payload: aggregator_admin.show_content_menu(message),
    "admin_categories": lambda message, payload: admin.show_categories_menu(message),
    "admin_add_category": lambda message, payload: admin.prompt_add_category(message),
    "admin_rename_category_menu": lambda message, payload: admin.prompt_rename_category_menu(message),
    "admin_rename_category_pick": lambda message, payload: admin.cmd_rename_category_pick(message, payload["id"]),
    "admin_report_start": lambda message, payload: competitors_admin.prompt_report_topic(message),
    "admin_sources": lambda message, payload: aggregator_admin.show_sources_menu(message),
    "admin_sources_add": lambda message, payload: aggregator_admin.prompt_sources_add(message),
    "admin_sources_add_category": lambda message, payload: aggregator_admin.cmd_sources_add_category(
        message, payload["id"]
    ),
    "admin_sources_remove_menu": lambda message, payload: aggregator_admin.show_sources_remove_menu(message),
    "admin_sources_remove": lambda message, payload: aggregator_admin.cmd_sources_remove(message, payload["id"]),
    "admin_notifications": lambda message, payload: admin.show_notifications_menu(message),
    "admin_notif_toggle": lambda message, payload: admin.cmd_toggle_notification(message, payload["event"]),
    "admin_labels": lambda message, payload: admin.show_label_groups(message),
    "admin_label_group": lambda message, payload: admin.show_label_group(message, payload["group"]),
    "admin_label_edit": lambda message, payload: admin.prompt_edit_label(message, payload["group"], payload["key"]),
    "admin_audience": lambda message, payload: audience_admin.show_audience_menu(message),
    "admin_audience_candidates": lambda message, payload: audience_admin.show_candidates(message),
    "admin_audience_mark": lambda message, payload: audience_admin.cmd_mark_candidate(
        message, payload["vk_id"], payload["status"]
    ),
    "admin_audience_criteria": lambda message, payload: audience_admin.show_criteria(message),
    "admin_audience_edit": lambda message, payload: audience_admin.prompt_edit_criteria(message, payload["key"]),
}

ADMIN_DRAFT_HANDLERS = {
    "set_days_custom": admin.handle_set_days_custom_input,
    "set_frequency_custom": admin.handle_set_frequency_custom_input,
    "edit_text": admin.handle_edit_text_input,
    "add_category": admin.handle_add_category_input,
    "rename_category": admin.handle_rename_category_input,
    "edit_label": admin.handle_edit_label_input,
    "report_topic": competitors_admin.handle_report_topic_input,
    "report_city": competitors_admin.handle_report_city_input,
    "sources_add_ref": aggregator_admin.handle_sources_add_ref_input,
    "audience_edit": audience_admin.handle_audience_edit_input,
}


@bl.message()
async def fallback_handler(message: Message) -> None:
    payload = message.get_payload_json()
    if payload and "cmd" in payload:
        handler = PAYLOAD_HANDLERS.get(payload["cmd"])
        if handler is not None:
            await handler(message, payload)
        return

    async with get_session() as session:
        post_draft = await session.get(PostDraft, message.from_id)
        post_step = post_draft.step if post_draft is not None else None
        admin_draft = await session.get(AdminDraft, message.from_id)
        admin_action = admin_draft.action if admin_draft is not None else None
        admin_draft_snapshot = admin_draft

    if post_step == "text":
        await client.handle_text_step(message)
        return
    if post_step == "attachments":
        await client.handle_attachments_step(message)
        return

    if admin_action is not None:
        handler = ADMIN_DRAFT_HANDLERS.get(admin_action)
        if handler is not None:
            await handler(message, admin_draft_snapshot)
            return

    # Нет активного диалога и это не кнопка — по требованию бот реагирует на
    # любую фразу показом главного меню, а не молчанием. Если написал не админ —
    # это ещё и повод уведомить админов (see NotificationEvent.NEW_MESSAGE), т.к.
    # свободный текст без активного сценария обычно значит, что человеку нужен
    # ответ, а не просто клик по кнопке.
    if not admin.is_admin(message.from_id):
        preview = (message.text or "(сообщение без текста, например вложение)").strip()
        await notify_admins(
            NotificationEvent.NEW_MESSAGE,
            f"✉️ Сообщение от https://vk.com/id{message.from_id}:\n{preview}",
        )
    await client.show_main_menu(message)
