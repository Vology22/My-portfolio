import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
# config.py
# Настройки парсера: что искать и где

# Поисковые запросы (можно расширять)
SEARCH_QUERIES = [
    "рабочий дом",
    "ремонт квартир недорого",
    "отделка помещений бригада",
    "строительство коттеджей объекты",
    "ремонт под ключ цены",
    "отделочные работы строительство",
    "строительство бани под ключ",
    "ремонт загородного дома",
    "строительные работы объекты",
    "отделка под ключ недорого",
]

# Города/регионы для поиска (общие для всех источников — 2ГИС, Яндекс.Карты).
# Список можно расширять под нужные регионы
CITIES = [
    "moscow",
    "spb",
    "novosibirsk",
    "ekaterinburg",
    "kazan",
    "krasnodar",
    "rostov",
    "voronezh",
    "nn_novgorod",
    "samara",
    "chelyabinsk",
    "krasnoyarsk",
    "ufa",
    "omsk",
    "volgograd",
]

# Настройки браузера
HEADLESS = True
PAGE_TIMEOUT_MS = 60000
WAIT_AFTER_LOAD_MS = 3500

# Задержки между запросами (секунды), чтобы не нагружать сайт и снижать риск блокировки
DELAY_BETWEEN_REQUESTS = (2, 5)  # (min, max) для random.uniform

# Сколько воркеров (браузеров) работают параллельно в main.py.
# Каждый воркер — свой процесс Chromium, поэтому реальная нагрузка на сайты растёт
# пропорционально. Если начнёт вылезать капча — в первую очередь снижай это число.
PARALLEL_WORKERS = 1

# Файл результата
OUTPUT_XLSX = "companies.xlsx"


# ру капча
API_KEY_RU_CAPTCHA = os.getenv('RUCAPTCHA_KEY', '')


# ---- Telegram ----
# api_id/api_hash получаешь на https://my.telegram.org/apps (свои, под аккаунт,
# с которого будем читать чаты)
TELEGRAM_API_ID = int(os.getenv('TELEGRAM_API_ID', '0'))
TELEGRAM_API_HASH = os.getenv('TELEGRAM_API_HASH', '')
# Строка сессии Telethon (StringSession) уже авторизованного аккаунта — получить
# через login_telegram.py (запускается один раз вручную, спросит номер телефона
# и код из Telegram/SMS, при необходимости — пароль 2FA). Не публиковать, даёт
# полный доступ к аккаунту.
TELEGRAM_SESSION = os.getenv('TELEGRAM_SESSION', '')
# id чатов/групп, где ищем контакты компаний (можно узнать через login_telegram.py —
# он печатает список диалогов с их id при первом запуске)
TELEGRAM_CHAT_IDS = [int(x) for x in os.getenv('TELEGRAM_CHAT_IDS', '').split(',') if x.strip()]
# Сколько последних сообщений сканировать в каждом чате (None — всю историю чата)
TELEGRAM_SCAN_LIMIT = 3000

# ---- ВКонтакте ----
# Пользовательский токен VK API (Standalone-приложение, https://vk.com/dev,
# нужны права groups/wall для чтения постов в пабликах)
VK_ACCESS_TOKEN = os.getenv('VK_ACCESS_TOKEN', '')
# Ссылки на паблики VK, где ищем контакты компаний
VK_GROUP_URLS = []