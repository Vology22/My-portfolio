from __future__ import annotations

from vkbottle.bot import Message

from bot.vk_attachments import attachments_to_string


def message_attachments_to_string(message: Message) -> str:
    return attachments_to_string(message.attachments)
