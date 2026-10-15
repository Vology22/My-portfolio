from __future__ import annotations

import asyncio
from datetime import datetime, timedelta

from bot.vk_client import api

ACTIVITY_WINDOW_DAYS = 30
SEARCH_COUNT = 100  # ограничиваем, иначе проверка активности (wall.get на группу) займёт слишком долго
REPORT_TOP_N = 10
THROTTLE_DELAY = 0.35  # пауза между wall.get, чтобы не словить флуд-контроль VK


async def resolve_city_id(city_name: str) -> int | None:
    result = await api.database.get_cities(country_id=1, q=city_name, count=1)
    if not result.items:
        return None
    return result.items[0].id


async def search_groups(query: str, city_id: int | None) -> list:
    result = await api.groups.search(
        q=query,
        type="group",
        city_id=city_id,
        count=SEARCH_COUNT,
        fields=["members_count"],
    )
    return list(result.items)


async def is_group_active(group_id: int) -> bool:
    try:
        wall = await api.wall.get(owner_id=-group_id, count=1)
    except Exception:
        return False
    if not wall.items:
        return False
    last_post_date = datetime.utcfromtimestamp(wall.items[0].date)
    return last_post_date >= datetime.utcnow() - timedelta(days=ACTIVITY_WINDOW_DAYS)


async def build_report(query: str, city_name: str) -> dict:
    city_id = await resolve_city_id(city_name)
    groups = await search_groups(query, city_id)

    enriched = []
    active_count = 0
    for group in groups:
        active = await is_group_active(group.id)
        if active:
            active_count += 1
        enriched.append({"group": group, "active": active})
        await asyncio.sleep(THROTTLE_DELAY)

    enriched.sort(key=lambda item: item["group"].members_count or 0, reverse=True)

    return {
        "query": query,
        "city": city_name,
        "city_resolved": city_id is not None,
        "total_found": len(groups),
        "active_count": active_count,
        "top": enriched[:REPORT_TOP_N],
    }
