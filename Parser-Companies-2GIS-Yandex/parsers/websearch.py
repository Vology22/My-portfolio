# parsers/websearch.py
"""
Общая логика для источников типа "поисковая выдача" (Яндекс.Поиск, Google) —
в отличие от 2ГИС/Яндекс.Карт, тут нет общей карточки с чистым JSON: каждый
сайт в выдаче — самостоятельная страница со своей вёрсткой. Поэтому вместо
чтения структуры страницы вытаскиваем телефон/email регуляркой по видимому
тексту (`page.inner_text('body')`), а название — из <h1>/<title>.

Что не пытаемся вытащить регуляркой: адрес. Формат слишком разный (сокращения,
порядок улица/дом/город), риск намусорить в БД перевешивает пользу — если
найдётся надёжный способ, добавим отдельно.
"""

import re
from typing import Optional

from playwright.sync_api import BrowserContext, Page

from .base import Company

PHONE_RE = re.compile(r"(?:\+7|8)[\s\-\(]?\d{3}[\s\-\)]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2}")
EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")

# Агрегаторы, соцсети, маркетплейсы, реестры компаний и подобное — это не
# карточка конкретной компании, такие ссылки из выдачи пропускаем.
SKIP_DOMAINS = [
    "avito.ru", "profi.ru", "uslugi.yandex.ru", "2gis.ru",
    "yandex.ru", "ya.ru", "yabs.yandex.ru", "an.yandex.ru",
    "google.", "youtube.com", "vk.com", "ok.ru", "instagram.com",
    "facebook.com", "t.me", "wikipedia.org", "flamp.ru", "zoon.ru",
    "market.yandex.ru", "ozon.ru", "wildberries.ru", "tiu.ru",
    "rusprofile.ru", "list-org.com", "spark-interfax.ru", "prom.ua",
    "yell.ru", "nashgorod.ru", "youla.ru",
]


def is_skippable(url: str) -> bool:
    return any(domain in url for domain in SKIP_DOMAINS)


def _extract_contacts(page: Page) -> dict:
    try:
        text = page.inner_text("body")
    except Exception:
        text = ""

    name = ""
    try:
        h1 = page.query_selector("h1")
        if h1:
            name = h1.inner_text().strip()[:150]
    except Exception:
        pass
    if not name:
        try:
            name = (page.title() or "").strip()[:150]
        except Exception:
            name = ""

    phone_match = PHONE_RE.search(text)
    email_match = EMAIL_RE.search(text)

    return {
        "name": name,
        "phone": phone_match.group(0) if phone_match else "",
        "email": email_match.group(0) if email_match else "",
    }


def visit_and_build_company(
    context: BrowserContext,
    url: str,
    region: str,
    query: str,
    source: str,
    page_timeout_ms: int,
) -> Optional[Company]:
    """
    Заходит на `url`, вытаскивает название/телефон/email, возвращает `Company`.
    Возвращает `None`, если страница вообще не открылась (мёртвый домен, таймаут) —
    вызывающий код такие пропускает, а не добавляет пустую запись.
    """
    page = context.new_page()
    try:
        page.goto(url, wait_until="domcontentloaded", timeout=page_timeout_ms)
        page.wait_for_timeout(1500)
        data = _extract_contacts(page)
    except Exception:
        return None
    finally:
        page.close()

    if not data["phone"] and not data["email"] and not data["name"]:
        return None

    return Company(
        name=data["name"] or "Без названия",
        phone=data["phone"],
        email=data["email"],
        website=url,
        address="",
        region=region,
        activity=query,
        source=source,
        source_url=url,
    )
