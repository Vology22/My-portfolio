# login_telegram.py
"""
Одноразовый скрипт: логинится в Telegram под твоим аккаунтом и печатает строку
сессии (Telethon StringSession) — её нужно вставить в config.py -> TELEGRAM_SESSION.

Перед запуском:
1. Получи api_id и api_hash на https://my.telegram.org/apps (раздел "API development
   tools", создать любое приложение — название и платформа значения не имеют).
2. Впиши их в config.py -> TELEGRAM_API_ID, TELEGRAM_API_HASH.
3. Запусти: python login_telegram.py
   Скрипт спросит номер телефона (в международном формате, например +79991234567),
   код из Telegram/SMS и, если включена двухфакторная аутентификация — пароль.
4. Скопируй строку сессии, которую скрипт напечатает в конце, в config.py.

Строка сессии даёт полный доступ к аккаунту наравне с паролем — никому не
показывай и никуда, кроме config.py, не сохраняй.

После логина скрипт также печатает список твоих диалогов (чатов/групп/каналов)
с их id — оттуда бери значения для TELEGRAM_CHAT_IDS.
"""

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from config import TELEGRAM_API_ID, TELEGRAM_API_HASH

if not TELEGRAM_API_ID or not TELEGRAM_API_HASH:
    raise SystemExit(
        "Сначала впиши TELEGRAM_API_ID и TELEGRAM_API_HASH в config.py "
        "(получить на https://my.telegram.org/apps)"
    )

with TelegramClient(StringSession(), TELEGRAM_API_ID, TELEGRAM_API_HASH) as client:
    session_string = client.session.save()
    print("\n=== Строка сессии (вставь в config.py -> TELEGRAM_SESSION) ===")
    print(session_string)

