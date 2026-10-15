from __future__ import annotations

from datetime import datetime, timedelta

from sqlalchemy import select

from bot.config import settings
from bot.db.models import Post, PostStatus, User
from bot.db.session import get_session
from bot.db.settings_repo import get_int_setting, get_setting
from bot.modules.posts.keyboards import freeze_keyboard
from bot.modules.posts.subscriptions import check_is_member
from bot.vk_client import api
from bot.vk_utils import new_random_id


async def check_subscriptions() -> None:
    """Страховочная сверка подписки для авторов активных/приостановленных постов —
    основной путь обновления это события group_join/group_leave (см. events.py),
    это только подстраховка на случай пропущенных событий (даунтайм бота)."""
    async with get_session() as session:
        author_ids = (
            await session.execute(
                select(Post.author_vk_id)
                .where(Post.status.in_([PostStatus.ACTIVE, PostStatus.PAUSED]))
                .distinct()
            )
        ).scalars().all()

    for user_id in author_ids:
        is_subscribed = await check_is_member(api, user_id)
        async with get_session() as session:
            user = await session.get(User, user_id)
            if user is not None:
                was_subscribed = user.is_subscribed
                user.is_subscribed = is_subscribed
                user.subscribed_checked_at = datetime.utcnow()
            else:
                was_subscribed = is_subscribed

            if is_subscribed and not was_subscribed:
                posts = (
                    await session.execute(
                        select(Post).where(Post.author_vk_id == user_id, Post.status == PostStatus.PAUSED)
                    )
                ).scalars().all()
                for post in posts:
                    post.status = PostStatus.ACTIVE
                text = await get_setting(session, "text_resubscribed") if posts else None
            elif not is_subscribed and was_subscribed:
                posts = (
                    await session.execute(
                        select(Post).where(Post.author_vk_id == user_id, Post.status == PostStatus.ACTIVE)
                    )
                ).scalars().all()
                for post in posts:
                    post.status = PostStatus.PAUSED
                text = await get_setting(session, "text_unsubscribed") if posts else None
            else:
                posts = []
                text = None

            await session.commit()

        if posts and text:
            await api.messages.send(user_id=user_id, message=text, random_id=new_random_id())


async def renewal_reminder() -> None:
    """Раз в renewal_interval_days с момента последнего продления запрашивает у автора
    подтверждение и переводит объявление в заморозку до ответа."""
    async with get_session() as session:
        interval_days = await get_int_setting(session, "renewal_interval_days")
        freeze_days = await get_int_setting(session, "freeze_response_days")
        text_template = await get_setting(session, "text_renewal_reminder")
        threshold = datetime.utcnow() - timedelta(days=interval_days)

        posts = (
            await session.execute(
                select(Post).where(
                    Post.status == PostStatus.ACTIVE,
                    Post.last_renewed_at.is_not(None),
                    Post.last_renewed_at <= threshold,
                )
            )
        ).scalars().all()

        to_notify = [(post.id, post.author_vk_id) for post in posts]
        for post in posts:
            post.status = PostStatus.FROZEN
            post.frozen_at = datetime.utcnow()
        await session.commit()

    text = text_template.format(freeze_response_days=freeze_days)
    for post_id, author_id in to_notify:
        await api.messages.send(
            user_id=author_id,
            message=text,
            keyboard=freeze_keyboard(post_id),
            random_id=new_random_id(),
        )


async def freeze_expiry() -> None:
    """Если автор не ответил на напоминание о продлении в течение freeze_response_days,
    объявление удаляется из системы."""
    async with get_session() as session:
        freeze_days = await get_int_setting(session, "freeze_response_days")
        text = await get_setting(session, "text_freeze_deleted")
        threshold = datetime.utcnow() - timedelta(days=freeze_days)

        posts = (
            await session.execute(
                select(Post).where(Post.status == PostStatus.FROZEN, Post.frozen_at <= threshold)
            )
        ).scalars().all()

        to_notify = [(post.id, post.author_vk_id) for post in posts]
        for post in posts:
            post.status = PostStatus.DELETED
        await session.commit()

    for _post_id, author_id in to_notify:
        await api.messages.send(user_id=author_id, message=text, random_id=new_random_id())


async def auto_publish() -> None:
    """Публикует активные объявления подписанных авторов на стену сообщества раз в
    post_frequency_minutes. Гранулярность — минуты (раньше были только дни), поэтому
    сам job теперь запускается раз в минуту (bot/scheduler.py), а не раз в час."""
    async with get_session() as session:
        frequency_minutes = await get_int_setting(session, "post_frequency_minutes")
        threshold = datetime.utcnow() - timedelta(minutes=frequency_minutes)

        posts = (
            await session.execute(
                select(Post)
                .join(User, User.vk_id == Post.author_vk_id)
                .where(
                    Post.status == PostStatus.ACTIVE,
                    User.is_subscribed.is_(True),
                    (Post.last_published_at.is_(None)) | (Post.last_published_at <= threshold),
                )
            )
        ).scalars().all()
        post_ids = [post.id for post in posts]

    for post_id in post_ids:
        async with get_session() as session:
            post = await session.get(Post, post_id)
            if post is None or post.status != PostStatus.ACTIVE:
                continue
            result = await api.wall.post(
                owner_id=-settings.group_id,
                message=post.text,
                attachments=post.attachments or None,
                from_group=1,
            )
            post.wall_post_id = result.post_id
            post.last_published_at = datetime.utcnow()
            await session.commit()
