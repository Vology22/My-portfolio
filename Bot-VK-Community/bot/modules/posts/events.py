from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from vkbottle import GroupEventType
from vkbottle.bot import BotLabeler

from bot.db.models import NotificationEvent, Post, PostStatus, User
from bot.db.session import get_session
from bot.db.settings_repo import get_setting
from bot.modules.posts.notifications import notify_admins
from bot.vk_client import api
from bot.vk_utils import new_random_id

bl = BotLabeler()


@bl.raw_event(GroupEventType.GROUP_LEAVE, dataclass=dict)
async def on_group_leave(event: dict) -> None:
    user_id = event["object"]["user_id"]
    async with get_session() as session:
        user = await session.get(User, user_id)
        if user is not None:
            user.is_subscribed = False
            user.subscribed_checked_at = datetime.utcnow()

        posts = (
            await session.execute(
                select(Post).where(Post.author_vk_id == user_id, Post.status == PostStatus.ACTIVE)
            )
        ).scalars().all()
        for post in posts:
            post.status = PostStatus.PAUSED
        text = await get_setting(session, "text_unsubscribed")
        await session.commit()
        paused = bool(posts)

    if paused:
        await api.messages.send(user_id=user_id, message=text, random_id=new_random_id())
    await notify_admins(
        NotificationEvent.NEW_UNSUBSCRIBER,
        f"🚪 Пользователь https://vk.com/id{user_id} отписался от сообщества.",
        exclude_vk_id=user_id,
    )


@bl.raw_event(GroupEventType.GROUP_JOIN, dataclass=dict)
async def on_group_join(event: dict) -> None:
    user_id = event["object"]["user_id"]
    async with get_session() as session:
        user = await session.get(User, user_id)
        if user is not None:
            user.is_subscribed = True
            user.subscribed_checked_at = datetime.utcnow()

        posts = (
            await session.execute(
                select(Post).where(Post.author_vk_id == user_id, Post.status == PostStatus.PAUSED)
            )
        ).scalars().all()
        for post in posts:
            post.status = PostStatus.ACTIVE
        text = await get_setting(session, "text_resubscribed")
        await session.commit()
        resumed = bool(posts)

    if resumed:
        await api.messages.send(user_id=user_id, message=text, random_id=new_random_id())
    await notify_admins(
        NotificationEvent.NEW_SUBSCRIBER,
        f"🆕 Пользователь https://vk.com/id{user_id} подписался на сообщество.",
        exclude_vk_id=user_id,
    )


@bl.raw_event(GroupEventType.WALL_REPLY_NEW, dataclass=dict)
async def on_wall_reply_new(event: dict) -> None:
    obj = event["object"]
    from_id = obj.get("from_id")
    text = (obj.get("text") or "").strip() or "(без текста)"
    post_id = obj.get("post_id")
    await notify_admins(
        NotificationEvent.NEW_COMMENT,
        f"💬 Новый комментарий от https://vk.com/id{from_id} к посту #{post_id}:\n{text}",
        exclude_vk_id=from_id,
    )


@bl.raw_event(GroupEventType.LIKE_ADD, dataclass=dict)
async def on_like_add(event: dict) -> None:
    obj = event["object"]
    if obj.get("object_type") != "post":
        return
    liker_id = obj.get("liker_id")
    post_id = obj.get("post_id") or obj.get("object_id")
    await notify_admins(
        NotificationEvent.NEW_LIKE,
        f"👍 Новый лайк от https://vk.com/id{liker_id} на посте #{post_id}.",
        exclude_vk_id=liker_id,
    )
