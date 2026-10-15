# parsers/yandex.py
"""
Парсер Яндекс.Карт.

Подход:
1. Открываем https://yandex.ru/maps/ (без привязки к конкретному городу)
2. Вводим в поиск запрос вместе с названием города текстом — Яндекс сам
   резолвит нужный регион по тексту, отдельный geo_id города не нужен
3. Собираем ссылки на карточки организаций (/maps/org/<slug>/<id>/)
4. Заходим в каждую карточку и читаем встроенный в <script> JSON
   (то же React/Angular-состояние приложения) — там чистые телефон,
   адрес, сайт и населённый пункт, без маскировки и обфусцированных классов
"""

import json
import random
import re
import time
from typing import List

from playwright.sync_api import Browser, Page

from .base import Company, CITY_NAMES_RU
from config import PAGE_TIMEOUT_MS, WAIT_AFTER_LOAD_MS, DELAY_BETWEEN_REQUESTS

# ---- Селекторы ----
SEL_SEARCH_INPUT = "input[placeholder*='оиск']"
SEL_ORG_LINK     = "a[href*='/maps/org/']"
SEL_SCROLLABLE   = "[class*='scroll__container']"

ORG_LINK_RE = re.compile(r"(/maps/org/[^/?]+/\d+)")


def _random_delay():
    a, b = DELAY_BETWEEN_REQUESTS
    time.sleep(random.uniform(a, b))


def _do_search(page: Page, query: str, city_ru: str, attempts: int = 3) -> bool:
    """
    Вводим 'запрос город' в поле поиска и нажимаем Enter.

    Используем `page.locator(...)` вместо `query_selector()` + `ElementHandle` —
    та же защита от гонки ("Element is not attached to the DOM"), что и в
    `parsers/dgis.py:_do_search`, на случай, если карта тоже перерисует поле
    поиска между нашими действиями. Несколько попыток на случай перерисовки
    даже между действиями локатора.
    """
    for attempt in range(1, attempts + 1):
        try:
            locator = page.locator(SEL_SEARCH_INPUT).first
            locator.wait_for(state="visible", timeout=10000)
            locator.click()
            page.wait_for_timeout(300)
            locator.fill("")
            locator.type(f"{query} {city_ru}", delay=60)
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            page.wait_for_timeout(WAIT_AFTER_LOAD_MS)
            return True
        except Exception as e:
            print(f"    [!] не удалось ввести запрос в поиск (попытка {attempt}/{attempts}): {e}")
            page.wait_for_timeout(1000)
    return False


def _collect_org_links(page: Page, max_results: int = 30) -> List[str]:
    """Скроллим список результатов и собираем уникальные ссылки /maps/org/."""
    links: set[str] = set()

    for attempt in range(20):
        anchors = page.query_selector_all(SEL_ORG_LINK)
        for a in anchors:
            href = a.get_attribute("href") or ""
            m = ORG_LINK_RE.search(href)
            if m:
                links.add(m.group(1))
        if len(links) >= max_results:
            break

        scroller = page.query_selector(SEL_SCROLLABLE)
        if scroller:
            scroller.evaluate("el => el.scrollBy(0, 800)")
        else:
            page.mouse.wheel(0, 800)
        page.wait_for_timeout(700)

    return list(links)[:max_results]


def _get_item_data(page: Page, timeout_ms: int = 8000) -> dict | None:
    """
    Карточка организации содержит <script> с сырым JSON (без обёртки JSON.parse) —
    состоянием карты, включающим найденную организацию по пути
    data.stack[0].results.items[0]. Там незамаскированный телефон, сайт,
    полный адрес и населённый пункт (compositeAddress.locality) — в отличие
    от видимого текста на странице, где номер спрятан за кнопкой «Показать телефон».

    Скрипт с этим состоянием иногда дорисовывается на странице с задержкой
    (после domcontentloaded), поэтому вместо фиксированной паузы ждём его
    появления через wait_for_function — так же надёжно на медленном и быстром
    интернете.
    """
    finder_js = (
        "() => Array.from(document.scripts)"
        ".map(s => s.textContent)"
        ".find(t => t && t.includes('\"stack\"') && t.includes('\"results\"') && t.includes('\"items\"'))"
    )
    try:
        page.wait_for_function(finder_js, timeout=timeout_ms)
    except Exception:
        pass  # даже если не дождались — пробуем достать то, что уже есть

    try:
        text = page.evaluate(finder_js)
        if not text:
            return None
        data = json.loads(text)
        stack = data.get("stack") or []
        if not stack:
            return None
        items = (stack[0].get("results") or {}).get("items") or []
        if items:
            return items[0]
    except Exception:
        pass
    return None


def _extract_company(page: Page, url: str, region: str, query: str) -> Company:
    name = phone = website = address = email = ""
    item = _get_item_data(page)

    if item:
        name = item.get("title") or item.get("shortTitle") or ""
        address = item.get("address") or ""

        phones = item.get("phones") or []
        if phones:
            phone = phones[0].get("value", "")

        urls = item.get("urls") or []
        if urls:
            website = urls[0]

        locality = (item.get("compositeAddress") or {}).get("locality")
        if locality:
            region = locality

    return Company(
        name=name or "Без названия",
        phone=phone,
        email=email,
        website=website,
        address=address,
        region=region,
        activity=query,
        source="yandex",
        source_url=url,
    )


def parse_yandex(browser: Browser, query: str, city_slug: str, max_results: int = 20) -> List[Company]:
    """
    Возвращает список компаний по запросу `query` в городе `city_slug` (Яндекс.Карты).
    Принимает уже запущенный `browser` (создаётся один раз на весь прогон в main.py) —
    здесь только открываем новый context/page под конкретный поиск.
    """
    results: List[Company] = []
    city_ru = CITY_NAMES_RU.get(city_slug, city_slug)

    context = browser.new_context(
        locale="ru-RU",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 900},
    )
    page = context.new_page()

    try:
        # 1. Открываем общую страницу карт (без привязки к городу)
        page.goto("https://yandex.ru/maps/", wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
        page.wait_for_timeout(2000)

        # 2. Вводим "запрос город" в поле поиска
        ok = _do_search(page, query, city_ru)
        if not ok:
            print(f"  [!] не нашли поисковое поле на yandex.ru/maps")
            return results

        current_url = page.url
        print(f"  [yandex] {city_slug} / '{query}': URL после поиска: {current_url}")

        # 3. Собираем ссылки на карточки
        org_links = _collect_org_links(page, max_results=max_results)
        print(f"  [yandex] {city_slug} / '{query}': найдено карточек: {len(org_links)}")

        if not org_links:
            print(f"  [!] результатов нет — возможно, запрос не дал совпадений")
            return results

        # 4. Обходим каждую карточку
        for href in org_links:
            full_url = f"https://yandex.ru{href}/"
            try:
                detail = context.new_page()
                detail.goto(full_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
                company = _extract_company(detail, full_url, city_slug, query)
                results.append(company)
                print(f"    + {company.name} | {company.phone} | {company.address}")
                detail.close()
            except Exception as e:
                print(f"    [!] ошибка карточки {full_url}: {e}")
            finally:
                _random_delay()

    except Exception as e:
        print(f"  [!] общая ошибка ({city_slug} / '{query}'): {e}")
    finally:
        context.close()

    return results