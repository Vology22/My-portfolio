from __future__ import annotations

from vkbottle import API

from bot.config import settings

# Единый низкоуровневый API-клиент сообщества, используемый везде: в обработчиках
# сообщений, в обработчиках raw-событий (group_join/group_leave) и в фоновых job'ах
# планировщика, у которых нет входящего Message/event с привязанным ctx_api.
api = API(settings.group_token)
