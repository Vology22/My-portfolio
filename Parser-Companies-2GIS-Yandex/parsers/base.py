# parsers/base.py
from dataclasses import dataclass, field
from typing import Optional

# Русские названия городов для текстового поиска (ключи совпадают со slug'ами в
# config.CITIES) — используется везде, где город вводится текстом в поисковую
# строку сайта, а не подставляется в URL как slug (Яндекс.Карты, Яндекс.Поиск,
# Google).
CITY_NAMES_RU = {
    "moscow": "Москва",
    "spb": "Санкт-Петербург",
    "novosibirsk": "Новосибирск",
    "ekaterinburg": "Екатеринбург",
    "kazan": "Казань",
    "krasnodar": "Краснодар",
    "rostov": "Ростов-на-Дону",
    "voronezh": "Воронеж",
    "nn_novgorod": "Нижний Новгород",
    "samara": "Самара",
    "chelyabinsk": "Челябинск",
    "krasnoyarsk": "Красноярск",
    "ufa": "Уфа",
    "omsk": "Омск",
    "volgograd": "Волгоград",
}


@dataclass
class Company:
    """Унифицированная запись о компании для итоговой таблицы."""
    name: str
    phone: str = ""
    email: str = ""
    website: str = ""
    address: str = ""
    region: str = ""
    activity: str = ""       # вид деятельности / описание
    source: str = ""         # откуда взято (например, "2gis")
    source_url: str = ""     # ссылка на карточку/страницу

    def dedup_key(self) -> str:
        """Ключ для дедупликации: телефон приоритетнее имени."""
        phone_norm = normalize_phone(self.phone)
        if phone_norm:
            return f"phone:{phone_norm}"
        return f"name:{self.name.strip().lower()}"


def merge_company(existing: list["Company"], new: "Company") -> str:
    """
    Ищет в `existing` запись с тем же `dedup_key()`, что и `new`.
    Нашли — дозаполняем пустые поля найденной записи данными из `new` (никогда
    не затираем то, что уже есть) и возвращаем "enriched". Не нашли — добавляем
    `new` в `existing` и возвращаем "added".

    Так каждый следующий источник (2ГИС, Яндекс.Карты, поиск по сайтам) может
    дополнить уже собранную запись (например, найти email там, где два других
    источника его не дали), а не создавать рядом дубль с частью полей пустыми.
    """
    key = new.dedup_key()
    for c in existing:
        if c.dedup_key() == key:
            c.phone = c.phone or new.phone
            c.email = c.email or new.email
            c.website = c.website or new.website
            c.address = c.address or new.address
            c.region = c.region or new.region
            return "enriched"
    existing.append(new)
    return "added"


def normalize_phone(phone: str) -> str:
    """Приводит телефон к виду +7XXXXXXXXXX (только цифры с кодом страны)."""
    if not phone:
        return ""
    digits = "".join(ch for ch in phone if ch.isdigit())
    if len(digits) == 11 and digits.startswith("8"):
        digits = "7" + digits[1:]
    if len(digits) == 10:
        digits = "7" + digits
    if len(digits) == 11 and digits.startswith("7"):
        return "+" + digits
    return digits  # на случай нестандартных номеров — оставляем как есть
