# parsers/dgis.py
"""
Парсер 2ГИС.

Подход (исправленный):
1. Открываем главную страницу города https://2gis.ru/<city>
2. Находим поисковое поле и вводим запрос вручную (как человек) — это решает
   проблему двойного URL-кодирования кириллицы
3. Ждём загрузки результатов, прокручиваем список, собираем ссылки /firm/
4. Заходим в каждую карточку, достаём название, адрес, телефон, сайт
"""

import random
import time
from typing import List

from playwright.sync_api import Browser, Page

from .base import Company
from config import PAGE_TIMEOUT_MS, WAIT_AFTER_LOAD_MS, DELAY_BETWEEN_REQUESTS


# ---- Селекторы ----
SEL_SEARCH_INPUT   = "input[placeholder*='оиск'], input[type='search'], input[class*='search']"
SEL_FIRM_LINK      = "a[href*='/firm/']"
SEL_SCROLLABLE     = "[class*='_scrollable'], [class*='search-result'], [class*='results']"
SEL_NAME           = "h1"
SEL_WEBSITE_LINK   = "a[href^='http']:not([href*='2gis'])"
SEL_SKIP_UPDATE    = "text=Пропустить обновление браузера и перейти в 2ГИС"

# Домены, которые не считаются сайтом компании
SKIP_DOMAINS = ["2gis", "yandex", "google", "vk.com", "instagram", "facebook", "otello"]


def _random_delay():
    a, b = DELAY_BETWEEN_REQUESTS
    time.sleep(random.uniform(a, b))


def _bypass_update_screen(page: Page):
    """Пропускаем заглушку 'советует обновить браузер', если появилась."""
    try:
        btn = page.query_selector(SEL_SKIP_UPDATE)
        if btn:
            btn.click()
            page.wait_for_timeout(1500)
    except Exception:
        pass


def _do_search(page: Page, query: str, attempts: int = 3) -> bool:
    """
    Вводим запрос в поисковое поле и нажимаем Enter.
    Возвращает True, если поле найдено и ввод выполнен.

    Используем `page.locator(...)` вместо `query_selector()` + `ElementHandle`:
    2ГИС иногда перерисовывает поле поиска между тем, как мы его нашли, и тем,
    как пробуем кликнуть/ввести текст — `ElementHandle` в этот момент "отваливается"
    от DOM (`Element is not attached to the DOM`). `Locator` при каждом действии
    заново ищет актуальный элемент в DOM, поэтому не ловит эту гонку. Дополнительно
    оборачиваем в несколько попыток — на случай, если перерисовка попадёт даже
    между двумя действиями локатора.
    """
    for attempt in range(1, attempts + 1):
        try:
            locator = page.locator(SEL_SEARCH_INPUT).first
            locator.wait_for(state="visible", timeout=10000)
            locator.click()
            page.wait_for_timeout(300)
            locator.fill("")           # очищаем на случай, если там что-то есть
            locator.type(query, delay=60)   # вводим посимвольно, как человек
            page.wait_for_timeout(500)
            page.keyboard.press("Enter")
            page.wait_for_timeout(WAIT_AFTER_LOAD_MS)
            return True
        except Exception as e:
            print(f"    [!] не удалось ввести запрос в поиск (попытка {attempt}/{attempts}): {e}")
            page.wait_for_timeout(1000)
    return False


def _collect_firm_links(page: Page, max_results: int = 30) -> List[str]:
    """Скроллим список результатов и собираем уникальные ссылки /firm/."""
    links: set[str] = set()

    for attempt in range(20):
        anchors = page.query_selector_all(SEL_FIRM_LINK)
        for a in anchors:
            href = a.get_attribute("href") or ""
            if "/firm/" in href:
                links.add(href.split("?")[0])
        if len(links) >= max_results:
            break

        # Пробуем прокрутить контейнер результатов или всю страницу
        scroller = page.query_selector(SEL_SCROLLABLE)
        if scroller:
            scroller.evaluate("el => el.scrollBy(0, 800)")
        else:
            page.mouse.wheel(0, 800)
        page.wait_for_timeout(700)

    return list(links)[:max_results]


def _get_profile_data(page: Page) -> dict | None:
    """
    2ГИС встраивает в карточку фирмы JSON `window.initialState`, который React
    использует для гидрации — там есть незамаскированные телефон, сайт и полный
    адрес (в отличие от DOM, где номер спрятан за кнопкой «Показать телефон»,
    а классы адреса — обфусцированные хеши вида `_wrdavn`, меняющиеся при
    каждом деплое). Читаем эти данные напрямую вместо скрейпинга разметки.
    """
    try:
        state = page.evaluate("() => window.initialState")
        profile = state["data"]["entity"]["profile"]
        return next(iter(profile.values()))["data"]
    except Exception:
        return None


def _extract_company(page: Page, url: str, region: str, query: str) -> Company:
    name = phone = website = address = email = ""
    data = _get_profile_data(page)

    if data:
        name = data.get("name") or data.get("full_name") or ""
        address = data.get("address_name") or ""
        for group in data.get("contact_groups") or []:
            for contact in group.get("contacts") or []:
                ctype = contact.get("type")
                if ctype == "phone" and not phone:
                    phone = contact.get("value", "")
                elif ctype == "website" and not website:
                    website = contact.get("url") or contact.get("value", "")
                elif ctype == "email" and not email:
                    email = contact.get("value", "")
        # Часть фирм физически находится не в самом городе, а в пригородном
        # посёлке/селе того же района — там нет записи с type == "city".
        # Тогда берём максимально точный уровень: посёлок, иначе район.
        adm_div = data.get("adm_div") or []
        city_div = (
            next((d for d in adm_div if d.get("type") == "city" and d.get("name")), None)
            or next(
                (d for d in adm_div if d.get("name") and (d.get("is_default") or d.get("flags", {}).get("is_default"))),
                None,
            )
            or next((d for d in adm_div if d.get("type") == "settlement" and d.get("name")), None)
            or next((d for d in adm_div if d.get("type") == "district_area" and d.get("name")), None)
        )
        if city_div:
            region = city_div["name"].replace("\xa0", " ")

    # Запасной вариант, если initialState не найден (сайт изменил разметку)
    if not name:
        try:
            el = page.query_selector(SEL_NAME)
            if el:
                name = el.inner_text().strip()
        except Exception:
            pass

    if not website:
        try:
            for a in page.query_selector_all(SEL_WEBSITE_LINK):
                href = a.get_attribute("href") or ""
                if not any(d in href for d in SKIP_DOMAINS):
                    website = href
                    break
        except Exception:
            pass

    return Company(
        name=name or "Без названия",
        phone=phone,
        email=email,
        website=website,
        address=address,
        region=region,
        activity=query,
        source="2gis",
        source_url=url,
    )


def parse_2gis(browser: Browser, query: str, city_slug: str, max_results: int = 20) -> List[Company]:
    """
    Возвращает список компаний по запросу `query` в городе `city_slug`.
    Принимает уже запущенный `browser` (создаётся один раз на весь прогон в main.py) —
    здесь только открываем новый context/page под конкретный поиск.
    """
    results: List[Company] = []
    city_url = f"https://2gis.ru/{city_slug}"

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
        # 1. Открываем страницу города (без запроса в URL — нет проблем с кодировкой)
        page.goto(city_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
        page.wait_for_timeout(2000)
        _bypass_update_screen(page)

        # 2. Вводим запрос в поисковое поле руками
        ok = _do_search(page, query)
        if not ok:
            print(f"  [!] не нашли поисковое поле на {city_url}")
            return results

        current_url = page.url
        print(f"  [2gis] {city_slug} / '{query}': URL после поиска: {current_url}")

        # 3. Собираем ссылки на карточки
        firm_links = _collect_firm_links(page, max_results=max_results)
        print(f"  [2gis] {city_slug} / '{query}': найдено карточек: {len(firm_links)}")

        if not firm_links:
            print(f"  [!] результатов нет — возможно, запрос не дал совпадений")
            return results

        # 4. Обходим каждую карточку
        for href in firm_links:
            full_url = href if href.startswith("http") else f"https://2gis.ru{href}"
            try:
                detail = context.new_page()
                detail.goto(full_url, wait_until="domcontentloaded", timeout=PAGE_TIMEOUT_MS)
                detail.wait_for_timeout(1500)
                _bypass_update_screen(detail)
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