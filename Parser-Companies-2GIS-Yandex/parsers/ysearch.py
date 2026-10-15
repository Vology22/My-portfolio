# parsers/ysearch.py
"""
Парсер Яндекс.Поиска (обычная веб-выдача, не Яндекс.Карты) — заходит на сами
сайты компаний из органической выдачи и вытаскивает контакты (см. websearch.py).

Подход:
1. Открываем https://yandex.ru/search/?text=<запрос город>
2. Закрываем попап "Сделать Яндекс основным поиском?", если появился
3. Собираем ссылки из результатов (li.serp-item) — берём только прямой http(s)
   href (не через yabs.yandex.ru/yandex.ru/an — это трекинг/реклама) и
   отфильтровываем агрегаторы/соцсети (websearch.SKIP_DOMAINS)
4. Заходим на каждый сайт, вытаскиваем название/телефон/email
"""

import random
import time
from typing import List

from playwright.sync_api import Browser, Page

from .base import Company, CITY_NAMES_RU
from .websearch import is_skippable, visit_and_build_company
from config import PAGE_TIMEOUT_MS, DELAY_BETWEEN_REQUESTS

SEL_RESULT_ITEM = "li.serp-item"
SEL_DISMISS_POPUP = "button:has-text('Нет, спасибо')"


def _random_delay():
    a, b = DELAY_BETWEEN_REQUESTS
    time.sleep(random.uniform(a, b))


def _dismiss_popup(page: Page):
    try:
        btn = page.query_selector(SEL_DISMISS_POPUP)
        if btn:
            btn.click()
            page.wait_for_timeout(500)
    except Exception:
        pass


def _collect_result_links(page: Page, max_results: int) -> List[str]:
    links: List[str] = []
    seen = set()
    try:
        items = page.query_selector_all(SEL_RESULT_ITEM)
    except Exception:
        return links

    for item in items:
        try:
            a = item.query_selector("a[href^='http']")
            if not a:
                continue
            href = a.get_attribute("href") or ""
        except Exception:
            continue
        if not href or href in seen:
            continue
        if is_skippable(href):
            continue
        seen.add(href)
        links.append(href)
        if len(links) >= max_results:
            break

    return links


def _looks_like_captcha(page: Page) -> bool:
    try:
        return "робот" in (page.title() or "").lower()
    except Exception:
        return False


def _new_context(browser: Browser):
    return browser.new_context(
        locale="ru-RU",
        user_agent=(
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36"
        ),
        viewport={"width": 1366, "height": 900},
    )


def parse_yandex_search(browser: Browser, query: str, city_slug: str, max_results: int = 10, attempts: int = 4) -> List[Company]:
    """
    Возвращает список компаний, найденных через обычный веб-поиск Яндекса по `query`
    в `city_slug`. Yandex SmartCaptcha иногда всё же проскакивает даже в headed-режиме
    (не стабильно — тот же запрос секундами позже проходит чисто). Простой reload
    той же страницы/сессии её не снимает — если сессию уже пометили подозрительной,
    капча всплывает и на следующей попытке. Поэтому на каждой новой попытке поднимаем
    свежий `context` (чистые cookies) вместо повторной загрузки той же страницы.
    """
    results: List[Company] = []
    city_ru = CITY_NAMES_RU.get(city_slug, city_slug)

    import urllib.parse
    search_url = "https://yandex.ru/search/?text=" + urllib.parse.quote(f"{query} {city_ru}")

    context = None
    links: List[str] = []
    try:
        for attempt in range(1, attempts + 1):
            if context is not None:
                context.close()
            context = _new_context(browser)
            page = context.new_page()

            page.goto(search_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
            try:
                page.wait_for_load_state("networkidle", timeout=6000)
            except Exception:
                pass  # иногда страница ещё дозагружает виджеты/рекламу — не критично
            page.wait_for_timeout(2500)
            _dismiss_popup(page)

            links = _collect_result_links(page, max_results=max_results)
            if links:
                break
            if _looks_like_captcha(page):
                print(f"  [!] ysearch {city_slug} / '{query}': похоже на капчу (попытка {attempt}/{attempts}), новая сессия")
            else:
                print(f"  [ysearch] {city_slug} / '{query}': результатов нет (попытка {attempt}/{attempts}), новая сессия")
            page.wait_for_timeout(3000)

        print(f"  [ysearch] {city_slug} / '{query}': найдено ссылок: {len(links)}")

        if not links:
            return results

        for url in links:
            try:
                company = visit_and_build_company(context, url, city_slug, query, "yandex_search", PAGE_TIMEOUT_MS)
                if company:
                    company.region = city_ru
                    results.append(company)
                    try:
                        print(f"    + {company.name} | {company.phone} | {company.email} | {url}")
                    except Exception:
                        # Спецсимвол (например "м³"), который не печатается в текущей
                        # консоли (cp1251) — компания уже добавлена в results, это
                        # только косметика вывода, не повод прерывать обход остальных ссылок.
                        print(f"    + [добавлено, не печатается из-за спецсимволов] {url}")
            except Exception as e:
                print(f"    [!] ошибка сайта {url}: {e}")
            finally:
                _random_delay()

    except Exception as e:
        print(f"  [!] общая ошибка ysearch ({city_slug} / '{query}'): {e}")
    finally:
        if context is not None:
            context.close()

    return results
