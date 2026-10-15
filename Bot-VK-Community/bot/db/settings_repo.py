from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from bot.db.models import Setting

# Значения по умолчанию для всех настраиваемых админом параметров.
# Ключи с префиксом text_ — это шаблоны сообщений, редактируемые через /set_text.
DEFAULT_SETTINGS: dict[str, str] = {
    "renewal_interval_days": "30",
    "freeze_response_days": "3",
    "post_frequency_minutes": "10080",  # заменяет прежний post_frequency_days (7 дн. = 10080 мин.)
    "aggregator_posts_per_cycle": "5",  # сколько новых постов с одного источника брать за цикл (0 = без лимита)
    "aggregator_max_age_hours": "48",  # не брать посты конкурента старше N часов (0 = без ограничения)
    "aggregator_repost_ttl_days": "30",  # через сколько дней можно повторно опубликовать тот же пост конкурента (0 = никогда)
    "aggregator_rotation_index": "0",  # служебное: позиция ротации категорий, руками не редактируется
    "audience_min_friends": "0",  # 0 = без ограничения
    "audience_min_followers": "0",  # 0 = без ограничения
    "audience_cities": "[]",  # JSON-список названий городов; [] = без ограничения по гео
    "audience_keywords": "[]",  # JSON-список ключевых слов для проверки тематических подписок; [] = без проверки
    "text_renewal_reminder": (
        "Прошёл срок публикации вашего объявления. Хотите продолжить публикацию, "
        "удалить объявление или отредактировать его? Если не ответите в течение "
        "{freeze_response_days} дн., объявление будет удалено."
    ),
    "text_freeze_deleted": "Вы не ответили в течение отведённого срока, объявление удалено.",
    "text_unsubscribed": (
        "Вы отписались от сообщества, поэтому публикация объявления приостановлена. "
        "Подпишитесь на сообщество, чтобы возобновить показ."
    ),
    "text_resubscribed": "Спасибо за подписку! Публикация объявления возобновлена.",
    "text_rejected": "Ваше объявление отклонено модератором.",
    "text_approved": "Ваше объявление одобрено и будет опубликовано согласно расписанию.",
}


async def seed_defaults(session: AsyncSession) -> None:
    existing = {row.key for row in (await session.execute(select(Setting.key))).all()}
    for key, value in DEFAULT_SETTINGS.items():
        if key not in existing:
            session.add(Setting(key=key, value=value))
    await session.commit()


async def get_setting(session: AsyncSession, key: str) -> str:
    row = await session.get(Setting, key)
    if row is not None:
        return row.value
    return DEFAULT_SETTINGS[key]


async def get_int_setting(session: AsyncSession, key: str) -> int:
    return int(await get_setting(session, key))


async def set_setting(session: AsyncSession, key: str, value: str) -> None:
    row = await session.get(Setting, key)
    if row is None:
        session.add(Setting(key=key, value=value))
    else:
        row.value = value
    await session.commit()


# Названия разделов/кнопок/подписей (в отличие от DEFAULT_SETTINGS выше — это не
# значения настроек, а редактируемые админом ПОДПИСИ элементов интерфейса).
# Хранятся в той же таблице settings, но с отдельным пространством ключей
# ("label_..."), чтобы не путаться с ключами вида text_* (тело шаблона сообщения)
# и с обычными настройками. Значение по умолчанию передаётся вызывающим кодом
# (bot/modules/posts/keyboards.py::EDITABLE_LABEL_GROUPS), а не берётся из
# DEFAULT_SETTINGS — так не нужно сидировать в БД подписи, которые никто не менял.
async def get_label(session: AsyncSession, key: str, default: str) -> str:
    row = await session.get(Setting, key)
    return row.value if row is not None else default
