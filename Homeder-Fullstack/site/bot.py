import telebot
from telebot import types
import time
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import requests
from telebot.types import ReplyKeyboardRemove
import mysql.connector
from mysql.connector import Error
from datetime import datetime
import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
import threading
from PIL import Image
import io

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
URL_channel = 'https://t.me/homederSFEDU'
channel_id = -1003305629380
url_webapp = 'https://homeder.ru'
API_YANDEX_GEO = os.getenv('YANDEX_GEO_KEY', '')

DB_CONFIG = {
    'host': 'localhost',
    'database': 'homeder',
    'user': 'bot',
    'password': 'Mama1946!',
    'port': 3306
}

UPLOAD_PATH = 'uploads/'
os.makedirs(UPLOAD_PATH, exist_ok=True)
os.makedirs(os.path.join(UPLOAD_PATH, 'thumbs'), exist_ok=True)

# {media_group_id: {'photos': [], 'user_id': ..., 'timer': ...}}
media_group_buffer = {}
# {user_id: user_data} — данные анкеты жилья пока буферизуем коллаж
media_group_user_data = {}

last_favorites_check = {}

# Временное хранилище данных профиля между callback и next_step_handler
_profile_temp = {}


# ─────────────────────────────────────────────
#  БД
# ─────────────────────────────────────────────

def create_connection():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        if conn.is_connected():
            return conn
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
    return None


def get_user_by_tg(tg_id):
    conn = create_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM users WHERE tg_id = %s", (str(tg_id),))
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def save_user_to_db(tg_id, full_name, bio="", photo_url="",
                    age=None, gender=None, bad_habits=None, pets=None, partner=None):
    """Создать или обновить пользователя."""
    conn = create_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT user_id FROM users WHERE tg_id = %s", (str(tg_id),))
        row = cursor.fetchone()
        if row:
            fields = ["full_name = %s", "bio = %s"]
            values = [full_name, bio]
            if photo_url:
                fields.append("avatar = %s")
                values.append(photo_url)
            if age is not None:
                fields.append("age = %s")
                values.append(age)
            if gender is not None:
                fields.append("gender = %s")
                values.append(gender)
            if bad_habits is not None:
                fields.append("bad_habits = %s")
                values.append(bad_habits)
            if pets is not None:
                fields.append("pets = %s")
                values.append(pets)
            if partner is not None:
                fields.append("partner = %s")
                values.append(partner)
            values.append(str(tg_id))
            cursor.execute(f"UPDATE users SET {', '.join(fields)} WHERE tg_id = %s", values)
            user_db_id = row[0]
        else:
            cursor.execute(
                """INSERT INTO users (full_name, bio, tg_id, avatar, age, gender, bad_habits, pets, partner)
                   VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                (full_name, bio, str(tg_id), photo_url or None, age, gender, bad_habits, pets, partner)
            )
            user_db_id = cursor.lastrowid
        conn.commit()
        return user_db_id
    except Error as e:
        print(f"Ошибка сохранения пользователя: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()


def get_user_property(tg_id):
    conn = create_connection()
    if not conn:
        return None
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT p.* FROM properties p
               JOIN users u ON u.user_id = p.owner_id
               WHERE u.tg_id = %s
               ORDER BY p.created_at DESC LIMIT 1""",
            (str(tg_id),)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def save_property_to_db(owner_db_id, price, title, description, address,
                        floor, rooms, current_tenants, potential_tenants):
    conn = create_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(
            """INSERT INTO properties
               (owner_id, price, title, description, city, floor, rooms, current_tenants, potential_tenants)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (owner_db_id, price, title, description, "Ростов-на-Дону",
             floor, rooms, current_tenants, potential_tenants)
        )
        property_id = cursor.lastrowid
        conn.commit()
        return property_id
    except Error as e:
        print(f"Ошибка сохранения объявления: {e}")
        conn.rollback()
        return None
    finally:
        cursor.close()
        conn.close()


def save_property_images(property_id, photo_urls):
    """Сохранить пути к фото в таблицу prop_image."""
    conn = create_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        for i, url in enumerate(photo_urls):
            cursor.execute(
                "INSERT INTO prop_image (property, img_url, is_cover) VALUES (%s, %s, %s)",
                (property_id, url, 1 if i == 0 else 0)
            )
        conn.commit()
        print(f"В БД записано {len(photo_urls)} путей к фото для объявления #{property_id}: {photo_urls}")
        return True
    except Error as e:
        print(f"Ошибка сохранения фото в БД: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_favorites(tg_id):
    conn = create_connection()
    if not conn:
        return []
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(
            """SELECT p.prop_id, p.title, p.price, p.description,
                      u.full_name as owner_name
               FROM favorites f
               JOIN properties p ON p.prop_id = f.prop_id
               JOIN users u ON u.user_id = p.owner_id
               WHERE f.user_id = (SELECT user_id FROM users WHERE tg_id = %s)""",
            (str(tg_id),)
        )
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def remove_from_favorites(tg_id, prop_id):
    conn = create_connection()
    if not conn:
        return False
    cursor = conn.cursor()
    try:
        cursor.execute(
            """DELETE FROM favorites
               WHERE user_id = (SELECT user_id FROM users WHERE tg_id = %s)
               AND prop_id = %s""",
            (str(tg_id), prop_id)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Ошибка удаления из избранного: {e}")
        conn.rollback()
        return False
    finally:
        cursor.close()
        conn.close()


def get_all_favorites_snapshot():
    conn = create_connection()
    if not conn:
        return {}
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT prop_id, user_id FROM favorites")
        result = {}
        for prop_id, user_id in cursor.fetchall():
            result.setdefault(prop_id, set()).add(user_id)
        return result
    finally:
        cursor.close()
        conn.close()


def get_property_owner_tg(prop_id):
    conn = create_connection()
    if not conn:
        return None
    cursor = conn.cursor()
    try:
        cursor.execute(
            """SELECT u.tg_id, p.title FROM properties p
               JOIN users u ON u.user_id = p.owner_id
               WHERE p.prop_id = %s""",
            (prop_id,)
        )
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def get_liker_name(user_db_id):
    conn = create_connection()
    if not conn:
        return "Кто-то"
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT full_name FROM users WHERE user_id = %s", (user_db_id,))
        row = cursor.fetchone()
        return row[0] if row else "Кто-то"
    finally:
        cursor.close()
        conn.close()


# ─────────────────────────────────────────────
#  Мониторинг избранного
# ─────────────────────────────────────────────

def favorites_watcher():
    global last_favorites_check
    last_favorites_check = get_all_favorites_snapshot()
    print("Мониторинг избранного запущен.")
    while True:
        time.sleep(30)
        try:
            current = get_all_favorites_snapshot()
            for prop_id, likers in current.items():
                prev_likers = last_favorites_check.get(prop_id, set())
                for liker_db_id in likers - prev_likers:
                    owner_info = get_property_owner_tg(prop_id)
                    if not owner_info:
                        continue
                    owner_tg_id, prop_title = owner_info
                    liker_name = get_liker_name(liker_db_id)
                    try:
                        bot.send_message(
                            owner_tg_id,
                            f"⭐ *Новый лайк!*\n\n"
                            f"Пользователь *{liker_name}* добавил ваше объявление\n"
                            f"«{prop_title}» в избранное!\n\n"
                            f"_ID объявления: #{prop_id}_",
                            parse_mode="Markdown"
                        )
                    except Exception as e:
                        print(f"Не удалось отправить уведомление {owner_tg_id}: {e}")
            last_favorites_check = current
        except Exception as e:
            print(f"Ошибка в favorites_watcher: {e}")


# ─────────────────────────────────────────────
#  Фото
# ─────────────────────────────────────────────

def download_and_save_photo(photo_file, user_id, property_id=None):
    """Скачать фото, сохранить на диск, вернуть путь."""
    try:
        file_info = bot.get_file(photo_file.file_id)
        downloaded = bot.download_file(file_info.file_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
        if property_id:
            filename = f"property_{property_id}_{timestamp}_{photo_file.file_unique_id}.jpg"
        else:
            filename = f"user_{user_id}_{timestamp}_{photo_file.file_unique_id}.jpg"
        full_path = os.path.join(UPLOAD_PATH, filename)
        with open(full_path, 'wb') as f:
            f.write(downloaded)
        # Миниатюра
        try:
            thumb_dir = os.path.join(UPLOAD_PATH, 'thumbs')
            os.makedirs(thumb_dir, exist_ok=True)
            img = Image.open(io.BytesIO(downloaded))
            img.thumbnail((300, 300))
            img.save(os.path.join(thumb_dir, filename), 'JPEG', quality=85)
        except Exception as e:
            print(f"Ошибка миниатюры: {e}")
        photo_url = f"/uploads/{filename}"
        print(f"Фото сохранено на диск: {full_path}")
        return {'success': True, 'photo_url': photo_url}
    except Exception as e:
        print(f"Ошибка сохранения фото: {e}")
        return {'success': False}


# ─────────────────────────────────────────────
#  Медиагруппы (коллаж)
# ─────────────────────────────────────────────

def flush_media_group(user_id, media_group_id):
    """Срабатывает через 1.5 сек после последнего фото коллажа."""
    group = media_group_buffer.pop(media_group_id, None)
    if not group:
        return
    user_data = media_group_user_data.get(user_id)
    if not user_data:
        return
    photos = group['photos']
    # Добавляем все фото коллажа к уже собранным
    user_data['photos'].extend(photos)
    print(f"Коллаж обработан: {len(photos)} фото, итого {len(user_data['photos'])}")
    bot.send_message(user_id, f"✅ Получено {len(user_data['photos'])} фото. Сохраняю объявление...")
    save_property_to_database_from_data(user_id, user_data)


def handle_media_group_photo(message, user_data):
    """Буферизует фото коллажа и перезапускает таймер."""
    mgid = message.media_group_id
    user_id = message.from_user.id

    if mgid not in media_group_buffer:
        media_group_buffer[mgid] = {'photos': [], 'user_id': user_id}

    media_group_buffer[mgid]['photos'].append(message.photo[-1])
    media_group_user_data[user_id] = user_data

    existing_timer = media_group_buffer[mgid].get('timer')
    if existing_timer:
        existing_timer.cancel()

    timer = threading.Timer(1.5, flush_media_group, args=[user_id, mgid])
    media_group_buffer[mgid]['timer'] = timer
    timer.start()


# ─────────────────────────────────────────────
#  Вспомогательные
# ─────────────────────────────────────────────

def webAppKeyboard(user_id):
    keyboard = types.InlineKeyboardMarkup()
    web_app = types.WebAppInfo(f"{url_webapp}?tg_id={user_id}")
    keyboard.add(types.InlineKeyboardButton(text="🌐 Смотреть жильё", web_app=web_app))
    return keyboard


def get_address_yandex(latitude, longitude):
    url = "https://geocode-maps.yandex.ru/1.x/"
    params = {
        'apikey': API_YANDEX_GEO,
        'geocode': f"{longitude},{latitude}",
        'format': 'json',
        'lang': 'ru_RU'
    }
    try:
        resp = requests.get(url, params=params)
        data = resp.json()
        features = data['response']['GeoObjectCollection']['featureMember']
        if features:
            return features[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
    except Exception as e:
        print(f"Яндекс геокодер: {e}")
    return "Адрес не найден"


def cancel_keyboard():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("❌ Отменить"))
    return kb


def is_cancel(message):
    return message.content_type == 'text' and message.text == "❌ Отменить"


def send_cancel_confirm(chat_id):
    bot.send_message(chat_id, "Заполнение отменено.", reply_markup=ReplyKeyboardRemove())


# ─────────────────────────────────────────────
#  Меню
# ─────────────────────────────────────────────

def get_menu(message_or_call):
    if isinstance(message_or_call, int):
        user_id = message_or_call
        chat_id = message_or_call
    elif hasattr(message_or_call, 'from_user'):
        user_id = message_or_call.from_user.id
        chat_id = message_or_call.from_user.id
    else:
        user_id = message_or_call.id
        chat_id = message_or_call.id

    keyboard = webAppKeyboard(user_id)
    keyboard.add(
        types.InlineKeyboardButton(text="🏠 Мой дом", callback_data='my_home'),
        types.InlineKeyboardButton(text="👤 Мой профиль", callback_data='profile')
    )
    keyboard.add(
        types.InlineKeyboardButton(text="⭐ Избранное", callback_data='favorites')
    )
    bot.send_message(chat_id, '📋 *Главное меню:*', parse_mode="Markdown", reply_markup=keyboard)


# ─────────────────────────────────────────────
#  Callbacks
# ─────────────────────────────────────────────

@bot.callback_query_handler(func=lambda call: call.data == "check")
def callback_check(call):
    bot.delete_message(call.from_user.id, call.message.id)
    try:
        member = bot.get_chat_member(channel_id, call.from_user.id)
        if member.status in ["member", "administrator", "creator"]:
            bot.send_message(call.from_user.id, "✅ Подписка подтверждена!")
            get_menu(call)
        else:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Подписаться ✔", url=URL_channel))
            markup.add(types.InlineKeyboardButton('Проверить подписку ✔', callback_data='check'))
            bot.send_message(call.from_user.id, '❌ Ты *НЕ* подписан', parse_mode='MarkdownV2', reply_markup=markup)
    except Exception as e:
        # Бот не админ канала — пускаем без проверки
        print(f"Ошибка проверки подписки: {e}")
        bot.send_message(call.from_user.id, "✅ Добро пожаловать!")
        get_menu(call)


@bot.callback_query_handler(func=lambda call: call.data == "my_home")
def callback_my_home(call):
    bot.delete_message(call.from_user.id, call.message.id)
    existing = get_user_property(call.from_user.id)
    if existing:
        text = (
            f"🏠 *Ваше объявление:*\n\n"
            f"📌 *{existing['title']}*\n"
            f"💰 Цена: {existing['price'] or 'Не указана'}\n"
            f"📝 {(existing['description'] or '')[:200]}\n\n"
            f"ID: #{existing['prop_id']}"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✏️ Изменить объявление", callback_data='edit_home'))
        kb.add(types.InlineKeyboardButton("🔙 В меню", callback_data='menu'))
        bot.send_message(call.from_user.id, text, parse_mode="Markdown", reply_markup=kb)
    else:
        bot.send_message(call.from_user.id,
                         "🏠 *Добавление объявления*\n\nЗаполним анкету! В любой момент нажмите ❌ Отменить.",
                         parse_mode="Markdown")
        start_property_form(call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data in ['edit_home', 'menu'])
def callback_edit_or_menu(call):
    bot.delete_message(call.from_user.id, call.message.id)
    if call.data == 'edit_home':
        bot.send_message(call.from_user.id, "✏️ Заполним новую версию объявления. В любой момент нажмите ❌ Отменить.")
        start_property_form(call.from_user.id)
    else:
        get_menu(call)


@bot.callback_query_handler(func=lambda call: call.data == "profile")
def callback_profile(call):
    bot.delete_message(call.from_user.id, call.message.id)
    user = get_user_by_tg(call.from_user.id)
    if user and user.get('full_name'):
        gender_emoji = "👨" if user.get('gender') == 'Мужской' else "👩" if user.get('gender') == 'Женский' else "👤"
        text = (
            f"{gender_emoji} *Ваш профиль:*\n\n"
            f"👤 ФИО: *{user['full_name']}*\n"
            f"🎂 Возраст: {user.get('age') or '—'}\n"
            f"⚧ Пол: {user.get('gender') or '—'}\n"
            f"📝 О себе: {user.get('bio') or '—'}\n"
            f"🚬 Вредные привычки: {user.get('bad_habits') or '—'}\n"
            f"🐾 Животные: {user.get('pets') or '—'}\n"
            f"❤️ Пара: {user.get('partner') or '—'}\n"
            f"📅 Зарегистрирован: {str(user['created_at'])[:10]}"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("✏️ Редактировать профиль", callback_data='edit_profile'))
        kb.add(types.InlineKeyboardButton("🔙 В меню", callback_data='menu'))
        bot.send_message(call.from_user.id, text, parse_mode="Markdown", reply_markup=kb)
    else:
        bot.send_message(call.from_user.id,
                         "👤 *Создание профиля*\n\nДавайте заполним анкету!",
                         parse_mode="Markdown")
        start_profile_form(call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == "edit_profile")
def callback_edit_profile(call):
    bot.delete_message(call.from_user.id, call.message.id)
    bot.send_message(call.from_user.id, "✏️ Обновим ваш профиль. В любой момент нажмите ❌ Отменить.")
    start_profile_form(call.from_user.id)


@bot.callback_query_handler(func=lambda call: call.data == "favorites")
def callback_favorites(call):
    bot.delete_message(call.from_user.id, call.message.id)
    favs = get_favorites(call.from_user.id)
    if not favs:
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🔙 В меню", callback_data='menu'))
        bot.send_message(call.from_user.id, "⭐ У вас нет избранных объявлений.", reply_markup=kb)
        return
    bot.send_message(call.from_user.id, f"⭐ *Ваше избранное* ({len(favs)}):", parse_mode="Markdown")
    for fav in favs:
        text = (
            f"🏠 *{fav['title']}*\n"
            f"👤 Владелец: {fav['owner_name']}\n"
            f"💰 Цена: {fav['price'] or 'Не указана'}\n"
            f"📝 {(fav['description'] or '')[:150]}"
        )
        kb = types.InlineKeyboardMarkup()
        kb.add(types.InlineKeyboardButton("🗑 Удалить из избранного", callback_data=f"unfav_{fav['prop_id']}"))
        bot.send_message(call.from_user.id, text, parse_mode="Markdown", reply_markup=kb)
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("🔙 В меню", callback_data='menu'))
    bot.send_message(call.from_user.id, "—", reply_markup=kb)


@bot.callback_query_handler(func=lambda call: call.data.startswith('unfav_'))
def callback_unfav(call):
    prop_id = int(call.data.split('_')[1])
    if remove_from_favorites(call.from_user.id, prop_id):
        bot.answer_callback_query(call.id, "🗑 Удалено из избранного")
        bot.delete_message(call.from_user.id, call.message.id)
    else:
        bot.answer_callback_query(call.id, "❌ Ошибка удаления")


@bot.callback_query_handler(func=lambda call: call.data.startswith('fav_'))
def add_to_favorites_cb(call):
    try:
        property_id = int(call.data.split('_')[1])
        user_db_id = save_user_to_db(call.from_user.id, call.from_user.full_name or "Пользователь")
        if not user_db_id:
            bot.answer_callback_query(call.id, "❌ Ошибка")
            return
        conn = create_connection()
        if conn:
            cursor = conn.cursor()
            try:
                cursor.execute(
                    "INSERT INTO favorites (user_id, prop_id) VALUES (%s, %s) "
                    "ON DUPLICATE KEY UPDATE user_id=VALUES(user_id)",
                    (user_db_id, property_id)
                )
                conn.commit()
                bot.answer_callback_query(call.id, "✅ Добавлено в избранное!")
            except Error as e:
                print(f"Ошибка добавления в избранное: {e}")
                bot.answer_callback_query(call.id, "❌ Ошибка")
            finally:
                cursor.close()
                conn.close()
    except Exception as e:
        print(f"Ошибка callback fav_: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")


@bot.callback_query_handler(func=lambda call: call.data.startswith('gender_'))
def callback_gender(call):
    """Выбор пола — кнопкой."""
    gender = 'Мужской' if call.data == 'gender_m' else 'Женский'
    bot.delete_message(call.from_user.id, call.message.id)
    msg = bot.send_message(
        call.from_user.id,
        f"Выбрано: *{gender}*\n\n🎂 *Шаг 4/6* — Введите ваш возраст:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, profile_step_age, gender)


# ─────────────────────────────────────────────
#  Анкета профиля
# ─────────────────────────────────────────────

def start_profile_form(chat_id):
    """Шаг 1 — аватарка."""
    msg = bot.send_message(
        chat_id,
        "📸 *Шаг 1/6* — Отправьте фото для аватарки\n_(или напишите «пропустить»)_",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, profile_step_avatar)


def profile_step_avatar(message):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    photo_url = ""
    if message.content_type == 'photo':
        result = download_and_save_photo(message.photo[-1], message.from_user.id)
        if result['success']:
            photo_url = result['photo_url']
    elif message.content_type == 'text' and message.text.lower() not in ['пропустить', 'skip']:
        bot.send_message(message.chat.id, "Отправьте фото или напишите «пропустить»")
        bot.register_next_step_handler(message, profile_step_avatar)
        return

    msg = bot.send_message(
        message.chat.id,
        "👤 *Шаг 2/6* — Введите ваше ФИО:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, profile_step_name, photo_url)


def profile_step_name(message, photo_url):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    full_name = message.text.strip()

    # Сохраняем временные данные (нужны после callback gender)
    _profile_temp[message.from_user.id] = {'photo_url': photo_url, 'full_name': full_name}

    # Шаг 3 — пол через inline кнопки
    kb = types.InlineKeyboardMarkup()
    kb.add(
        types.InlineKeyboardButton("👨 Мужской", callback_data='gender_m'),
        types.InlineKeyboardButton("👩 Женский", callback_data='gender_f')
    )
    bot.send_message(
        message.chat.id,
        "⚧ *Шаг 3/6* — Выберите пол:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardRemove()
    )
    bot.send_message(message.chat.id, "👇", reply_markup=kb)


def profile_step_age(message, gender):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    try:
        age = int(message.text.strip())
        if not (1 <= age <= 120):
            raise ValueError
    except ValueError:
        bot.send_message(message.chat.id, "Введите корректный возраст (число от 1 до 120):")
        bot.register_next_step_handler(message, profile_step_age, gender)
        return

    msg = bot.send_message(
        message.chat.id,
        "🚬 *Шаг 5/6* — Вредные привычки?\n_(напишите или «нет»)_",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, profile_step_habits, gender, age)


def profile_step_habits(message, gender, age):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    bad_habits = message.text.strip()

    msg = bot.send_message(
        message.chat.id,
        "🐾 *Шаг 6/6* — Есть домашние животные?\n_(напишите или «нет»)_",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, profile_step_pets, gender, age, bad_habits)


def profile_step_pets(message, gender, age, bad_habits):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    pets = message.text.strip()

    msg = bot.send_message(
        message.chat.id,
        "❤️ *Шаг 7/7* — Есть пара?\n_(напишите или «нет»)_",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, profile_step_partner, gender, age, bad_habits, pets)


def profile_step_partner(message, gender, age, bad_habits, pets):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    partner = message.text.strip()

    temp = _profile_temp.pop(message.from_user.id, {})
    full_name = temp.get('full_name', message.from_user.full_name or 'Пользователь')
    photo_url = temp.get('photo_url', '')

    user_db_id = save_user_to_db(
        message.from_user.id,
        full_name,
        bio="",
        photo_url=photo_url,
        age=age,
        gender=gender,
        bad_habits=bad_habits,
        pets=pets,
        partner=partner
    )

    if user_db_id:
        text = (
            f"✅ *Профиль сохранён!*\n\n"
            f"👤 {full_name}\n"
            f"🎂 Возраст: {age}\n"
            f"⚧ Пол: {gender}\n"
            f"🚬 Привычки: {bad_habits}\n"
            f"🐾 Животные: {pets}\n"
            f"❤️ Пара: {partner}"
        )
        bot.send_message(message.chat.id, text, parse_mode="Markdown", reply_markup=ReplyKeyboardRemove())
    else:
        bot.send_message(message.chat.id, "❌ Ошибка при сохранении профиля.", reply_markup=ReplyKeyboardRemove())

    get_menu(message)


# ─────────────────────────────────────────────
#  Анкета объявления
# ─────────────────────────────────────────────

def start_property_form(chat_id):
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📍 Отправить геопозицию", request_location=True))
    kb.add(KeyboardButton("❌ Отменить"))
    msg = bot.send_message(chat_id, "📍 Укажите адрес или отправьте геопозицию:", reply_markup=kb)
    bot.register_next_step_handler(msg, prop_step_address)


def prop_step_address(message):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    if message.content_type == 'location':
        address = get_address_yandex(message.location.latitude, message.location.longitude)
    else:
        address = message.text
    msg = bot.send_message(message.chat.id, "🏢 Укажите этаж:", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, prop_step_floor, address)


def prop_step_floor(message, address):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    msg = bot.send_message(message.chat.id, "🚪 Количество комнат:", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, prop_step_rooms, address, message.text)


def prop_step_rooms(message, address, floor):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    msg = bot.send_message(message.chat.id, "👥 Сколько сожителей живёт сейчас?", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, prop_step_current_tenants, address, floor, message.text)


def prop_step_current_tenants(message, address, floor, rooms):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    msg = bot.send_message(message.chat.id, "🤝 Сколько потенциальных сожителей ищете?", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, prop_step_potential_tenants, address, floor, rooms, message.text)


def prop_step_potential_tenants(message, address, floor, rooms, current_tenants):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    msg = bot.send_message(
        message.chat.id,
        "💰 Укажите плату _(необязательно в деньгах)_:",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, prop_step_price, address, floor, rooms, current_tenants, message.text)


def prop_step_price(message, address, floor, rooms, current_tenants, potential_tenants):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    price = message.text.strip() or 'Не указана'
    msg = bot.send_message(message.chat.id, "📌 Придумайте название объявления:", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, prop_step_title, address, floor, rooms, current_tenants, potential_tenants, price)


def prop_step_title(message, address, floor, rooms, current_tenants, potential_tenants, price):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return
    msg = bot.send_message(message.chat.id, "📝 Опишите жильё подробнее:", reply_markup=cancel_keyboard())
    bot.register_next_step_handler(msg, prop_step_description, address, floor, rooms,
                                   current_tenants, potential_tenants, price, message.text)


def prop_step_description(message, address, floor, rooms, current_tenants, potential_tenants, price, title):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return

    user_data = {
        'address': address,
        'floor': floor,
        'rooms': rooms,
        'current_tenants': current_tenants,
        'potential_tenants': potential_tenants,
        'price': price,
        'title': title,
        'description': message.text,
        'photos': []
    }

    msg = bot.send_message(
        message.chat.id,
        "📸 Отправьте фотографии жилья.\n\n"
        "• Отправьте *коллаж* (несколько фото сразу) — сохранятся автоматически\n"
        "• Одиночные фото — потом напишите *«готово»*\n"
        "• Напишите *«пропустить»* чтобы пропустить фото",
        parse_mode="Markdown",
        reply_markup=cancel_keyboard()
    )
    bot.register_next_step_handler(msg, prop_step_photos, user_data)


def prop_step_photos(message, user_data):
    if is_cancel(message):
        send_cancel_confirm(message.chat.id)
        get_menu(message)
        return

    if message.content_type == 'text':
        text = message.text.lower()
        if text in ['пропустить', 'skip', 'нет', 'готово', 'готов', 'все', 'всё']:
            save_property_to_database_from_data(message.from_user.id, user_data)
            return
        bot.send_message(message.chat.id, "Отправьте фото или напишите «готово» / «пропустить»")
        bot.register_next_step_handler(message, prop_step_photos, user_data)
        return

    if message.content_type == 'photo':
        if message.media_group_id:
            # Коллаж — буферизуем, не сохраняем объявление сейчас
            handle_media_group_photo(message, user_data)
            # Продолжаем слушать (для последующих фото той же группы)
            bot.register_next_step_handler(message, prop_step_photos, user_data)
        else:
            # Одиночное фото
            user_data['photos'].append(message.photo[-1])
            bot.send_message(
                message.chat.id,
                f"✅ Фото {len(user_data['photos'])} получено. Ещё или напишите *«готово»*",
                parse_mode="Markdown"
            )
            bot.register_next_step_handler(message, prop_step_photos, user_data)
        return

    bot.send_message(message.chat.id, "Отправьте фото или напишите «готово» / «пропустить»")
    bot.register_next_step_handler(message, prop_step_photos, user_data)


def save_property_to_database_from_data(chat_id, user_data):
    """Финальное сохранение объявления + фото в БД."""
    bot.send_chat_action(chat_id, 'typing')

    user_db_id = save_user_to_db(chat_id, "Пользователь", bio=f"TG ID: {chat_id}")
    if not user_db_id:
        bot.send_message(chat_id, "❌ Ошибка сохранения пользователя.")
        return

    property_id = save_property_to_db(
        user_db_id,
        user_data['price'],
        user_data['title'],
        user_data['description'],
        user_data['address'],
        user_data.get('floor', ''),
        user_data.get('rooms', ''),
        user_data.get('current_tenants', ''),
        user_data.get('potential_tenants', '')
    )
    if not property_id:
        bot.send_message(chat_id, "❌ Ошибка сохранения объявления.")
        return

    # Скачиваем фото, сохраняем на диск, записываем пути в prop_image
    photo_urls = []
    for photo_file in user_data.get('photos', []):
        result = download_and_save_photo(photo_file, chat_id, property_id)
        if result['success']:
            photo_urls.append(result['photo_url'])

    if photo_urls:
        save_property_images(property_id, photo_urls)

    media_group_user_data.pop(chat_id, None)

    summary = (
        f"✅ *Объявление сохранено!*\n\n"
        f"📌 {user_data['title']}\n"
        f"📍 {user_data['address']}\n"
        f"🏢 Этаж: {user_data.get('floor', '—')}\n"
        f"🚪 Комнат: {user_data.get('rooms', '—')}\n"
        f"👥 Сейчас сожителей: {user_data.get('current_tenants', '—')}\n"
        f"🤝 Ищу сожителей: {user_data.get('potential_tenants', '—')}\n"
        f"💰 Плата: {user_data['price']}\n"
        f"📷 Фото: {len(photo_urls)}\n\n"
        f"ID: #{property_id}"
    )

    if user_data.get('photos'):
        bot.send_photo(chat_id, user_data['photos'][0].file_id,
                       caption=summary, parse_mode="Markdown",
                       reply_markup=ReplyKeyboardRemove())
    else:
        bot.send_message(chat_id, summary, parse_mode="Markdown",
                         reply_markup=ReplyKeyboardRemove())

    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton("⭐ Добавить в избранное", callback_data=f"fav_{property_id}"))
    bot.send_message(chat_id, "Хотите добавить объявление в избранное?", reply_markup=kb)

    get_menu(chat_id)


# ─────────────────────────────────────────────
#  Команды
# ─────────────────────────────────────────────

@bot.message_handler(commands=['start'])
def get_start(message):
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("Подписаться ✔", url=URL_channel))
    markup.add(types.InlineKeyboardButton('Проверить подписку ✔', callback_data='check'))
    bot.send_message(
        message.chat.id,
        "🏡 *Добро пожаловать в Homeder!*\n\n"
        "Здесь вы можете:\n"
        "• 🏠 Разместить объявление о жилье\n"
        "• 👤 Создать профиль\n"
        "• 🔍 Найти соседей\n\n"
        "Для начала подпишитесь на канал:",
        parse_mode="Markdown",
        reply_markup=markup
    )


@bot.message_handler(commands=['menu'])
def cmd_menu(message):
    get_menu(message)


@bot.message_handler(commands=['help'])
def show_help(message):
    bot.send_message(
        message.chat.id,
        "📖 *Помощь по Homeder*\n\n"
        "*/start* — начать\n"
        "*/menu* — главное меню\n"
        "*/help* — эта справка\n\n"
        "*🏠 Мой дом* — создать или посмотреть объявление\n"
        "*👤 Мой профиль* — создать или редактировать профиль\n"
        "*⭐ Избранное* — ваши сохранённые объявления",
        parse_mode="Markdown"
    )


# ─────────────────────────────────────────────
#  Запуск
# ─────────────────────────────────────────────

if __name__ == '__main__':
    watcher_thread = threading.Thread(target=favorites_watcher, daemon=True)
    watcher_thread.start()

    from requests.exceptions import ReadTimeout
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except ReadTimeout as e:
            print(f"Timeout: {e}, reconnecting...")
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)
