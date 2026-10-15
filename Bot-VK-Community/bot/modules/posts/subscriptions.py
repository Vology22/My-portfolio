from __future__ import annotations

from datetime import datetime

from vkbottle import API

from bot.config import settings
from bot.db.models import User


async def check_is_member(api: API, user_id: int) -> bool:
    result = await api.groups.is_member(group_id=settings.group_id, user_id=user_id)
    return bool(result)


async def get_or_create_user(session, api: API, user_id: int) -> User:
    user = await session.get(User, user_id)
    is_subscribed = await check_is_member(api, user_id)

    if user is None:
        vk_users = await api.users.get(user_ids=[user_id])
        info = vk_users[0]
        user = User(
            vk_id=user_id,
            first_name=info.first_name or "",
            last_name=info.last_name or "",
            is_subscribed=is_subscribed,
            subscribed_checked_at=datetime.utcnow(),
        )
        session.add(user)
    else:
        user.is_subscribed = is_subscribed
        user.subscribed_checked_at = datetime.utcnow()

    await session.commit()
    return user
