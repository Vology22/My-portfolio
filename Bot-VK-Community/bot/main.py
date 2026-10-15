from __future__ import annotations

import asyncio
import logging

logging.basicConfig(level=logging.DEBUG)

from vkbottle.bot import Bot

from bot.db.session import get_session, init_db
from bot.db.settings_repo import seed_defaults
from bot.modules.posts import dispatcher as posts_dispatcher
from bot.modules.posts import events as posts_events
from bot.scheduler import setup_scheduler
from bot.vk_client import api

bot = Bot(api=api)

# Весь интерфейс кнопочный — единственные labeler'ы с реальными обработчиками:
# posts_events (raw-события group_join/group_leave) и posts_dispatcher (catch-all
# для кнопок и многошаговых диалогов, см. его docstring). posts_dispatcher должен
# грузиться последним, если в будущем сюда вернутся текстовые команды.
bot.labeler.load(posts_events.bl)
bot.labeler.load(posts_dispatcher.bl)


async def main() -> None:
    await init_db()
    async with get_session() as session:
        await seed_defaults(session)

    scheduler = setup_scheduler()
    scheduler.start()

    await bot.run_polling()


if __name__ == "__main__":
    asyncio.run(main())
