# main.py
"""
Точка входа. Запуск:

    python main.py

На выходе — файл companies.xlsx со списком компаний
(название, телефон, email, сайт, адрес, регион, вид деятельности, источник).
"""

import os
import queue
import threading

import pandas as pd
from playwright.sync_api import sync_playwright

from config import SEARCH_QUERIES, CITIES, HEADLESS, PARALLEL_WORKERS, OUTPUT_XLSX, TELEGRAM_SCAN_LIMIT
from parsers.dgis import parse_2gis
from parsers.yandex import parse_yandex
from parsers.ysearch import parse_yandex_search
from parsers.vk import parse_vk
from parsers.telegram import parse_telegram
from parsers.base import Company, merge_company

PARSERS = [parse_2gis, parse_yandex, parse_yandex_search, parse_vk]

# Сколько карточек/сайтов/постов обходить на каждое задание — у поисковых источников
# (произвольные сайты, а не структурированная карточка) меньше, чтобы не тонуть
# в медленных/мёртвых доменах.
MAX_RESULTS = {
    parse_2gis: 20,
    parse_yandex: 20,
    parse_yandex_search: 10,
    parse_vk: 15,
}

# Яндекс.Поиск в headless-режиме почти сразу ловит Yandex SmartCaptcha (детект
# headless-браузера) — в обычном режиме (видимое окно) капчи не было ни разу.
# Поэтому эти источники получают отдельный, "живой" браузер вместо общего
# headless-браузера воркера.
HEADED_PARSERS = {parse_yandex_search}

_root, _ = os.path.splitext(OUTPUT_XLSX)
JOBS_LOG_PATH = f"{_root}.jobs.log"


def _job_key(city: str, query: str, parser) -> str:
    return f"{parser.__name__}\t{city}\t{query}"


def load_completed_jobs(path: str) -> set[str]:
    """
    Читает лог полностью обработанных заданий (город/запрос/источник) — заполняется
    самим прогоном (см. `_worker`). Без этого лога каждый перезапуск после обрыва
    заново гонял ВСЕ 180 заданий с нуля: `merge_company` не плодил дубли, но время на
    повторный обход уже покрытых городов (Москва, часть СПб — десятки минут) терялось
    впустую при каждом из частых обрывов. С логом уже готовые задания просто
    пропускаются при следующем запуске.
    """
    try:
        with open(path, encoding="utf-8") as f:
            return set(line.rstrip("\n") for line in f if line.strip())
    except FileNotFoundError:
        return set()


def _mark_job_done(path: str, key: str):
    with open(path, "a", encoding="utf-8") as f:
        f.write(key + "\n")


def _checkpoint_save(results: list, path: str):
    """
    Сохраняет то, что уже собрано, в xlsx после каждого обработанного задания —
    если прогон прервут (вручную, сбоем, чем угодно), на диске всё равно останется
    актуальный слепок прогресса, а не пусто. Файл может быть занят (открыт в Excel) —
    в этом случае просто пропускаем сохранение, следующий чекпоинт попробует снова.
    """
    try:
        save_to_excel(results, path)
    except Exception as e:
        print(f"  [!] не удалось сохранить чекпоинт в {path}: {e}")


def _worker(worker_id: int, jobs: "queue.Queue", results: list, results_lock: threading.Lock):
    """
    Один воркер — свой процесс Chromium (Playwright sync API живёт в своём потоке и не
    шарится между потоками), который переиспользуется для всех заданий, взятых этим
    воркером из общей очереди `jobs`, пока она не опустеет. Браузер для HEADED_PARSERS
    (см. выше) поднимается отдельно и лениво — только если воркеру реально достанется
    такое задание.
    """
    with sync_playwright() as p:
        headless_browser = p.chromium.launch(headless=HEADLESS)
        headed_browser = None
        try:
            while True:
                try:
                    city, query, parser = jobs.get_nowait()
                except queue.Empty:
                    break
                try:
                    print(f"[w{worker_id}] {parser.__name__} / {city} / '{query}'")
                    if parser in HEADED_PARSERS:
                        if headed_browser is None:
                            headed_browser = p.chromium.launch(headless=False)
                        browser = headed_browser
                    else:
                        browser = headless_browser
                    companies = parser(browser, query, city, max_results=MAX_RESULTS[parser])
                    with results_lock:
                        for c in companies:
                            merge_company(results, c)
                        _checkpoint_save(results, OUTPUT_XLSX)
                        _mark_job_done(JOBS_LOG_PATH, _job_key(city, query, parser))
                except Exception as e:
                    print(f"[w{worker_id}] [!] ошибка задания {parser.__name__}/{city}/'{query}': {e}")
                finally:
                    jobs.task_done()
        finally:
            headless_browser.close()
            if headed_browser:
                headed_browser.close()


def collect_all(cities: list[str] | None = None, seed: list[Company] | None = None) -> list[Company]:
    """
    Раскладываем все комбинации (город, запрос, источник) в общую очередь и разбираем
    её `PARALLEL_WORKERS` потоками — у каждого свой браузер, переиспользуемый между
    заданиями. Больше воркеров = быстрее, но и больше одновременных запросов к сайтам
    с одного IP — см. PARALLEL_WORKERS в config.py, если начнёт вылезать капча.

    `cities` — переопределить список городов (по умолчанию все из config.py). Вместе
    с `seed` (уже собранные записи, например через `load_existing()`) позволяет
    добрать недостающие города после прерванного прогона, не теряя то, что уже есть —
    чекпоинты продолжат сохранять `seed + новое` целиком.
    """
    cities = cities if cities is not None else CITIES
    completed = load_completed_jobs(JOBS_LOG_PATH)
    jobs: "queue.Queue" = queue.Queue()
    skipped = 0
    for city in cities:
        for query in SEARCH_QUERIES:
            for parser in PARSERS:
                if _job_key(city, query, parser) in completed:
                    skipped += 1
                    continue
                jobs.put((city, query, parser))
    if skipped:
        print(f"[*] Пропущено {skipped} уже обработанных заданий (см. {JOBS_LOG_PATH})")

    all_companies: list[Company] = list(seed) if seed else []
    results_lock = threading.Lock()

    workers = [
        threading.Thread(target=_worker, args=(i + 1, jobs, all_companies, results_lock))
        for i in range(PARALLEL_WORKERS)
    ]
    for w in workers:
        w.start()
    for w in workers:
        w.join()

    return all_companies


def collect_telegram(seed: list[Company] | None = None) -> list[Company]:
    """
    Отдельный проход по Telegram (config.TELEGRAM_CHAT_IDS) — в отличие от
    collect_all() не привязан к городам/запросам (см. parsers/telegram.py), просто
    сканирует последние TELEGRAM_SCAN_LIMIT сообщений в каждом чате и сливает
    найденные контакты в общий список через merge_company().
    """
    all_companies: list[Company] = list(seed) if seed else []
    companies = parse_telegram(limit_per_chat=TELEGRAM_SCAN_LIMIT)
    for c in companies:
        merge_company(all_companies, c)
    return all_companies


def load_existing(path: str) -> list[Company]:
    """
    Загружает уже собранные записи из xlsx (например, чекпоинт прерванного прогона) —
    используется, чтобы добрать недостающие города, не начиная сбор с нуля.
    """
    try:
        df = pd.read_excel(path).fillna("")
    except FileNotFoundError:
        return []
    except Exception as e:
        print(f"  [!] не удалось прочитать {path} ({e}) — начинаю с пустой базы")
        return []
    return [
        Company(
            name=str(row["Название"]),
            phone=str(row["Телефон"]),
            email=str(row["Email"]),
            website=str(row["Сайт"]),
            address=str(row["Адрес"]),
            region=str(row["Регион"]),
            activity=str(row["Деятельность"]),
            source=str(row["Источник"]),
            source_url=str(row["Ссылка"]),
        )
        for _, row in df.iterrows()
    ]


def deduplicate(companies: list[Company]) -> list[Company]:
    seen = set()
    unique = []
    for c in companies:
        key = c.dedup_key()
        if key not in seen:
            seen.add(key)
            unique.append(c)
    return unique


def save_to_excel(companies: list[Company], path: str):
    """
    Пишем во временный файл и атомарно переименовываем поверх `path` (`os.replace`).
    Если процесс убьют посреди записи (а фоновые прогоны в этом окружении обрывали
    уже не раз без видимой причины) — испортится только временный файл, а не
    единственная копия уже собранных данных. Раньше `df.to_excel(path, ...)` писал
    прямо в целевой файл — прерывание на середине один раз уже привело к
    `zipfile.BadZipFile` и потере всего прогресса, накопленного за прогон.
    """
    rows = [
        {
            "Название": c.name,
            "Телефон": c.phone,
            "Email": c.email,
            "Сайт": c.website,
            "Адрес": c.address,
            "Регион": c.region,
            "Деятельность": c.activity,
            "Источник": c.source,
            "Ссылка": c.source_url,
        }
        for c in companies
    ]
    df = pd.DataFrame(rows)
    root, ext = os.path.splitext(path)
    tmp_path = f"{root}.tmp{ext}"  # pandas выбирает движок по расширению — оно должно остаться .xlsx
    df.to_excel(tmp_path, index=False)
    os.replace(tmp_path, path)
    print(f"[+] Сохранено {len(rows)} записей в {path}")


def main():
    """
    Подхватывает то, что уже есть в OUTPUT_XLSX, как стартовую базу — так `python
    main.py` можно просто перезапускать после любого обрыва (в этом окружении
    фоновые прогоны периодически обрываются без видимой причины), не думая вручную
    про resume/seed. Проход по всем городам/запросам всё равно происходит целиком,
    но merge_company() безопасно пропускает уже собранное, а не плодит дубли.
    """
    existing = load_existing(OUTPUT_XLSX)
    if existing:
        print(f"[*] Загружено {len(existing)} уже собранных записей из {OUTPUT_XLSX} — продолжаем с них")

    all_companies = collect_all(seed=existing)
    print(f"[*] После браузерных источников: {len(all_companies)} записей")

    all_companies = collect_telegram(seed=all_companies)
    print(f"[*] После Telegram: {len(all_companies)} записей")

    unique_companies = deduplicate(all_companies)
    print(f"[*] После дедупликации: {len(unique_companies)}")

    save_to_excel(unique_companies, OUTPUT_XLSX)


if __name__ == "__main__":
    main()
