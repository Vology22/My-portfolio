from __future__ import annotations

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from bot.modules.aggregator.poller import poll_competitor_sources
from bot.modules.audience.poller import poll_competitor_audience
from bot.modules.posts.jobs import auto_publish, check_subscriptions, freeze_expiry, renewal_reminder

scheduler = AsyncIOScheduler()


def setup_scheduler() -> AsyncIOScheduler:
    scheduler.add_job(check_subscriptions, "interval", hours=6, id="check_subscriptions")
    scheduler.add_job(renewal_reminder, "interval", hours=24, id="renewal_reminder")
    scheduler.add_job(freeze_expiry, "interval", hours=24, id="freeze_expiry")
    # Раз в минуту, а не раз в час — post_frequency_minutes теперь можно задать
    # вплоть до 5 минут (см. bot/modules/posts/jobs.py::auto_publish), и часовой
    # интервал job'а не позволил бы это соблюдать.
    scheduler.add_job(auto_publish, "interval", minutes=1, id="auto_publish")
    scheduler.add_job(poll_competitor_sources, "interval", hours=2, id="poll_competitor_sources")
    # Раз в 6 часов, а не чаще — полный обход groups.getMembers по всем источникам
    # заметно дороже по числу запросов к API, чем поллинг постов (см.
    # bot/modules/audience/poller.py и ТЗ_новые_функции.txt, блок 3, пункт 2).
    scheduler.add_job(poll_competitor_audience, "interval", hours=6, id="poll_competitor_audience")
    return scheduler
