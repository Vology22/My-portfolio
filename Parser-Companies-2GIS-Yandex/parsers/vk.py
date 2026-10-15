# parsers/vk.py
"""
Парсер ВКонтакте — поиск по постам (не по заранее заданным пабликам).

Подход:
1. Вызываем VK API `newsfeed.search` с текстом "{запрос} {город}" — это глобальный
   поиск по постам всего ВКонтакте (нужен пользовательский токен, не групповой).
2. Из текста каждого поста регуляркой вытаскиваем телефон/email (те же PHONE_RE/
   EMAIL_RE, что и в websearch.py, — единый стандарт извлечения контактов по проекту).
   Посты без телефона и email пропускаем — в выдаче много шума (вакансии, репосты
   без контактов).
3. Название компании — это группа/паблик, от имени которого опубликован пост
   (owner_id < 0 → ищем в `groups` из extended-ответа; owner_id > 0 → это личная
   страница пользователя, берём имя из `profiles`).

Ограничение API: `newsfeed.search` отдаёт не более 200 постов за вызов и не
поддерживает глубокую пагинацию вглубь всей ленты — это не exhaustive-поиск по
всем постам с этими словами, а срез самых свежих/релевантных.
"""

import re
from typing import List

import requests

from .base import Company, CITY_NAMES_RU
from .websearch import PHONE_RE, EMAIL_RE
from config import VK_ACCESS_TOKEN

VK_API_VERSION = "5.199"
VK_API_URL = "https://api.vk.com/method/"


def _vk_call(method: str, **params) -> dict:
    params["access_token"] = VK_ACCESS_TOKEN
    params["v"] = VK_API_VERSION
    r = requests.get(VK_API_URL + method, params=params, timeout=30)
    data = r.json()
    if "error" in data:
        err = data["error"]
        raise RuntimeError(f"VK API error {err.get('error_code')}: {err.get('error_msg')}")
    return data["response"]


def _owner_name(owner_id: int, groups: dict, profiles: dict) -> str:
    if owner_id < 0:
        group = groups.get(-owner_id)
        return group.get("name", "") if group else ""
    profile = profiles.get(owner_id)
    if not profile:
        return ""
    return f"{profile.get('first_name', '')} {profile.get('last_name', '')}".strip()


def parse_vk(browser, query: str, city_slug: str, max_results: int = 20) -> List[Company]:
    """
    Возвращает список компаний, найденных через поиск постов ВКонтакте по `query` в
    `city_slug`. `browser` не используется (VK — чистый HTTP API, без Playwright) —
    параметр только ради единой сигнатуры с остальными парсерами в `main.PARSERS`.
    """
    results: List[Company] = []
    city_ru = CITY_NAMES_RU.get(city_slug, city_slug)
    search_text = f"{query} {city_ru}"

    try:
        data = _vk_call(
            "newsfeed.search",
            q=search_text,
            count=min(max_results * 4, 200),  # с запасом — много постов отсеется без контактов
            extended=1,
        )
    except Exception as e:
        print(f"  [!] ошибка VK API ({city_slug} / '{query}'): {e}")
        return results

    items = data.get("items", [])
    groups = {g["id"]: g for g in data.get("groups", [])}
    profiles = {p["id"]: p for p in data.get("profiles", [])}

    print(f"  [vk] {city_slug} / '{query}': найдено постов: {len(items)}")

    seen_phones = set()
    for item in items:
        if len(results) >= max_results:
            break
        text = item.get("text", "")
        phone_match = PHONE_RE.search(text)
        email_match = EMAIL_RE.search(text)
        if not phone_match and not email_match:
            continue

        phone = phone_match.group(0) if phone_match else ""
        if phone and phone in seen_phones:
            continue  # один и тот же репост часто встречается по нескольку раз подряд
        if phone:
            seen_phones.add(phone)

        owner_id = item.get("owner_id") or item.get("from_id") or 0
        name = _owner_name(owner_id, groups, profiles)
        post_url = f"https://vk.com/wall{owner_id}_{item.get('id')}"

        company = Company(
            name=name or "Без названия",
            phone=phone,
            email=email_match.group(0) if email_match else "",
            website="",
            address="",
            region=city_ru,
            activity=query,
            source="vk",
            source_url=post_url,
        )
        results.append(company)
        try:
            print(f"    + {company.name} | {company.phone} | {company.email} | {post_url}")
        except Exception:
            print(f"    + [добавлено, не печатается из-за спецсимволов] {post_url}")

    return results
