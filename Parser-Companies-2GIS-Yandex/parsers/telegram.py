# parsers/telegram.py
"""
Парсер Telegram — сканирует ВСЕ сообщения в заданных чатах (config.TELEGRAM_CHAT_IDS)
без фильтра по ключевым словам и регуляркой (PHONE_RE/EMAIL_RE из websearch.py)
проверяет каждое: если нашёлся телефон или email — это контакт, забираем кто написал
(имя отправителя/канала) и о чём сообщение (текст — в поле activity).

В отличие от остальных источников не привязан ни к городу, ни к поисковому запросу —
main.py вызывает его отдельным проходом (`main.collect_telegram`), а не через общую
очередь (город, запрос, источник).
"""

from typing import List, Optional

from telethon.sync import TelegramClient
from telethon.sessions import StringSession

from .base import Company
from .websearch import PHONE_RE, EMAIL_RE
from config import TELEGRAM_API_ID, TELEGRAM_API_HASH, TELEGRAM_SESSION, TELEGRAM_CHAT_IDS

_client: Optional[TelegramClient] = None


def _get_client() -> TelegramClient:
    """
    Один клиент на весь прогон (переиспользуется между чатами) — открывать
    MTProto-сессию заново на каждый вызов было бы намного медленнее.
    """
    global _client
    if _client is None:
        if not TELEGRAM_SESSION:
            raise RuntimeError(
                "TELEGRAM_SESSION пуст — сначала запусти login_telegram.py и впиши "
                "строку сессии в config.py"
            )
        _client = TelegramClient(StringSession(TELEGRAM_SESSION), TELEGRAM_API_ID, TELEGRAM_API_HASH)
        _client.connect()
    return _client


def _sender_name(msg) -> str:
    sender = msg.sender
    if not sender:
        return ""
    title = getattr(sender, "title", None)
    if title:
        return title
    first = getattr(sender, "first_name", "") or ""
    last = getattr(sender, "last_name", "") or ""
    return f"{first} {last}".strip()


def parse_telegram(limit_per_chat: Optional[int] = None) -> List[Company]:
    """
    Проходит по всем сообщениям в каждом чате из TELEGRAM_CHAT_IDS (без фильтра по
    тексту) и оставляет только те, где регуляркой нашёлся телефон или email.
    `limit_per_chat=None` — пройти всю историю чата; иначе — не больше limit_per_chat
    последних сообщений (полезно для быстрой проверки на большом чате).
    """
    results: List[Company] = []
    if not TELEGRAM_CHAT_IDS:
        return results

    try:
        client = _get_client()
    except Exception as e:
        print(f"  [!] telegram: не удалось подключиться: {e}")
        return results

    seen_phones = set()
    for chat_id in TELEGRAM_CHAT_IDS:
        count_found = 0
        count_scanned = 0
        try:
            for msg in client.iter_messages(chat_id, limit=limit_per_chat):
                count_scanned += 1
                text = msg.text or ""
                phone_match = PHONE_RE.search(text)
                email_match = EMAIL_RE.search(text)
                if not phone_match and not email_match:
                    continue

                phone = phone_match.group(0) if phone_match else ""
                if phone and phone in seen_phones:
                    continue
                if phone:
                    seen_phones.add(phone)

                name = _sender_name(msg)
                msg_url = f"https://t.me/c/{str(chat_id).replace('-100', '')}/{msg.id}"

                company = Company(
                    name=name or "Без названия",
                    phone=phone,
                    email=email_match.group(0) if email_match else "",
                    website="",
                    address="",
                    region="",
                    activity=text[:200].replace("\n", " "),
                    source="telegram",
                    source_url=msg_url,
                )
                results.append(company)
                count_found += 1
                try:
                    print(f"    + {company.name} | {company.phone} | {company.email} | {msg_url}")
                except Exception:
                    print(f"    + [добавлено, не печатается из-за спецсимволов] {msg_url}")

            print(f"  [telegram] chat={chat_id}: просмотрено {count_scanned}, с контактами {count_found}")
        except Exception as e:
            print(f"  [!] ошибка telegram chat={chat_id}: {e}")

    return results
