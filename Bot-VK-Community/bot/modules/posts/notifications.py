from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import settings
from bot.db.models import NotificationEvent, NotificationPreference
from bot.db.session import get_session
from bot.vk_client import api
from bot.vk_utils import new_random_id


async def is_notification_enabled(session: AsyncSession, admin_vk_id: int, event: NotificationEvent) -> bool:
    row = await session.get(NotificationPreference, (admin_vk_id, event))
    return row.enabled if row is not None else True


async def toggle_notification(session: AsyncSession, admin_vk_id: int, event: NotificationEvent) -> bool:
    row = await session.get(NotificationPreference, (admin_vk_id, event))
    if row is None:
        row = NotificationPreference(admin_vk_id=admin_vk_id, event_type=event, enabled=False)
        session.add(row)
    else:
        row.enabled = not row.enabled
    await session.commit()
    return row.enabled


async def notify_admins(event: NotificationEvent, text: str, *, exclude_vk_id: int | None = None) -> None:
    """Отправляет text всем ADMIN_IDS, у кого включён event, кроме exclude_vk_id
    (чтобы не слать админу уведомление о его же действии, если он окажется
    актёром события, например прокомментирует свой же пост)."""
    async with get_session() as session:
        recipients = [
            admin_id
            for admin_id in settings.admin_ids
            if admin_id != exclude_vk_id and await is_notification_enabled(session, admin_id, event)
        ]

    for admin_id in recipients:
        await api.messages.send(user_id=admin_id, message=text, random_id=new_random_id())
