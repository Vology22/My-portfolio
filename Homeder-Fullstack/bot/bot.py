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
import base64
import json
from PIL import Image
import io

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))  #  @homeder_bot
URL_channel = 'https://t.me/homederSFEDU'
channel_id = -1003305629380
url_webapp = 'https://homeder.ru'
API_YANDEX_GEO = os.getenv('YANDEX_GEO_KEY', '')

# Конфигурация базы данных MySQL
DB_CONFIG = {
    'host': 'localhost',
    'database': 'homeder',
    'user': 'bot',
    'password': 'Mama1946!',
    'port': 3306
}

# Путь для сохранения фото локально
UPLOAD_PATH = 'uploads/'
os.makedirs(UPLOAD_PATH, exist_ok=True)

def create_connection():
    """Создание соединения с БД"""
    try:
        connection = mysql.connector.connect(**DB_CONFIG)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Ошибка подключения к MySQL: {e}")
        return None

def save_user_to_db(user_id, full_name, bio="", photo_url=""):
    """Сохранение или обновление пользователя в таблице users"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        try:
            # Проверяем, существует ли пользователь
            check_query = "SELECT user_id FROM users WHERE tg_id = %s"
            cursor.execute(check_query, (str(user_id),))
            existing_user = cursor.fetchone()
            
            if existing_user:
                # Обновляем существующего пользователя
                update_query = """
                UPDATE users 
                SET full_name = %s, bio = %s 
                WHERE tg_id = %s
                """
                cursor.execute(update_query, (full_name, bio, str(user_id)))
                user_db_id = existing_user[0]
            else:
                # Создаем нового пользователя
                insert_query = """
                INSERT INTO users (full_name, bio, tg_id) 
                VALUES (%s, %s, %s)
                """
                cursor.execute(insert_query, (full_name, bio, str(user_id)))
                user_db_id = cursor.lastrowid
            
            connection.commit()
            return user_db_id
            
        except Error as e:
            print(f"Ошибка сохранения пользователя: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def save_property_to_db(owner_db_id, price, title, description, district, address, 
                       type_home, square, tenants, time_of_stay):
    """Сохранение объявления о жилье в таблице properties"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        try:
            # ЗАКОММЕНТИРОВАНО: Пока сохраняем только базовые поля, остальные в description
            # TODO: Когда в БД добавятся поля, нужно будет раскомментировать и изменить запрос
            
            # Объединяем все дополнительные данные в описание
            full_description = f"""
{description}

📍 Район: {district}
🏠 Адрес: {address}
📐 Тип жилья: {type_home}
📏 Площадь: {square} м²
👥 Количество соседей: {tenants}
⏰ Срок проживания: {time_of_stay}
            """.strip()
            
            # ЗАКОММЕНТИРОВАНО: Расширенная версия с дополнительными полями
            # """
            # INSERT INTO properties (owner_id, price, title, description, city, district, address, type_home, square, tenants, time_of_stay)
            # VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            # """
            # 
            # cursor.execute(insert_query, (owner_db_id, price, title, description, "Ростов-на-Дону", district, address, type_home, square, tenants, time_of_stay))
            
            # Текущая версия - только основные поля
            insert_query = """
            INSERT INTO properties (owner_id, price, title, description)
            VALUES (%s, %s, %s, %s)
            """
            
            cursor.execute(insert_query, (owner_db_id, price, title, full_description))
            property_id = cursor.lastrowid
            
            connection.commit()
            return property_id
            
        except Error as e:
            print(f"Ошибка сохранения объявления: {e}")
            connection.rollback()
            return None
        finally:
            cursor.close()
            connection.close()
    return None

def save_property_images(property_id, photo_urls):
    """Сохранение фотографий объявления в таблице prop_image"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        try:
            for i, photo_url in enumerate(photo_urls):
                is_cover = 1 if i == 0 else 0  # Первая фото - обложка
                
                insert_query = """
                INSERT INTO prop_image (property, img_url, is_cover)
                VALUES (%s, %s, %s)
                """
                
                cursor.execute(insert_query, (property_id, photo_url, is_cover))
            
            connection.commit()
            return True
            
        except Error as e:
            print(f"Ошибка сохранения фотографий: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def save_to_favorites(user_db_id, property_id):
    """Добавление объявления в избранное"""
    connection = create_connection()
    if connection:
        cursor = connection.cursor()
        
        try:
            insert_query = """
            INSERT INTO favorites (user_id, prop_id)
            VALUES (%s, %s)
            ON DUPLICATE KEY UPDATE user_id = VALUES(user_id)
            """
            
            cursor.execute(insert_query, (user_db_id, property_id))
            connection.commit()
            return True
            
        except Error as e:
            print(f"Ошибка добавления в избранное: {e}")
            connection.rollback()
            return False
        finally:
            cursor.close()
            connection.close()
    return False

def download_and_save_photo(photo_file, user_id, property_id=None):
    """Скачивание фото и сохранение локально с генерацией URL"""
    try:
        # Получаем информацию о файле
        file_info = bot.get_file(photo_file.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Создаем уникальное имя файла
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        if property_id:
            filename = f"property_{property_id}_{timestamp}_{photo_file.file_unique_id}.jpg"
        else:
            filename = f"user_{user_id}_{timestamp}_{photo_file.file_unique_id}.jpg"
        
        # Полный путь для сохранения
        full_path = os.path.join(UPLOAD_PATH, filename)
        
        # Сохраняем файл
        with open(full_path, 'wb') as f:
            f.write(downloaded_file)
        
        # Генерируем URL
        photo_url = f"/uploads/{filename}"
        
        # Также создаем миниатюру
        create_thumbnail(downloaded_file, filename)
        
        return {
            'success': True,
            'photo_url': photo_url,
            'local_path': full_path,
            'thumbnail_url': f"/uploads/thumbs/{filename}"
        }
        
    except Exception as e:
        print(f"Ошибка сохранения фото: {e}")
        return {'success': False, 'error': str(e)}

def create_thumbnail(image_data, filename):
    """Создание миниатюры изображения"""
    try:
        thumb_path = os.path.join(UPLOAD_PATH, 'thumbs')
        os.makedirs(thumb_path, exist_ok=True)
        
        full_thumb_path = os.path.join(thumb_path, filename)
        
        image = Image.open(io.BytesIO(image_data))
        image.thumbnail((300, 300))
        image.save(full_thumb_path, 'JPEG', quality=85)
        
        return True
    except Exception as e:
        print(f"Ошибка создания миниатюры: {e}")
        return False

def webAppKeyboard(user_id):
    keyboard = types.InlineKeyboardMarkup()
    dynamic_url = f"{url_webapp}?tg_id={user_id}"
    web_app = types.WebAppInfo(dynamic_url)
    button = types.InlineKeyboardButton(text="Смотреть жильё", web_app=web_app)
    keyboard.add(button)
    return keyboard

def get_address_yandex(latitude, longitude):
    """Получение адреса через Яндекс.Карты"""
    YANDEX_API_KEY = API_YANDEX_GEO
    
    url = "https://geocode-maps.yandex.ru/1.x/"
    
    params = {
        'apikey': YANDEX_API_KEY,
        'geocode': f"{longitude},{latitude}",
        'format': 'json',
        'lang': 'ru_RU'
    }
    
    try:
        response = requests.get(url, params=params)
        data = response.json()
        
        if 'response' in data and 'GeoObjectCollection' in data['response']:
            features = data['response']['GeoObjectCollection']['featureMember']
            if features:
                address = features[0]['GeoObject']['metaDataProperty']['GeocoderMetaData']['text']
                return address
        return "Адрес не найден"
        
    except Exception as e:
        return f"Ошибка: {str(e)}"

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    bot.delete_message(call.from_user.id, call.message.id)
    if call.data == "check":
        user_in_channel = bot.get_chat_member(channel_id, call.from_user.id)
        if user_in_channel.status in ["member", "administrator", "creator"]:
            bot.send_message(call.from_user.id, "Подписка подтверждена!")
            get_menu(call)
        else:
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("Подписаться ✔", url=URL_channel)
            markup.add(button1)
            key_check = types.InlineKeyboardButton(text='Проверить подписку ✔', callback_data='check')
            markup.add(key_check)
            bot.send_message(call.from_user.id, f'Ты *НЕ* подписан',  parse_mode='MarkdownV2', reply_markup=markup)
    
    elif call.data == "my_home":
        bot.send_message(call.from_user.id, 'Начнем заполнение анкеты')
        bot.send_chat_action(chat_id=call.from_user.id, action="typing")
        time.sleep(3)
        keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
        ZHD = telebot.types.KeyboardButton(text="Железнодорожный") 
        KRY = telebot.types.KeyboardButton(text="Кировский")
        LNY = telebot.types.KeyboardButton(text="Ленинский")
        PTY = telebot.types.KeyboardButton(text="Пролетарский")  
        OKT = telebot.types.KeyboardButton(text="Октябрьский")
        PMY = telebot.types.KeyboardButton(text="Первомайский")  
        SVY = telebot.types.KeyboardButton(text="Советский")    
        VRY = telebot.types.KeyboardButton(text="Ворошиловский")  
        keyboard.add(ZHD, KRY, LNY, PTY, OKT, PMY, SVY, VRY)
        msg = bot.send_message(call.from_user.id, 'Выберите район', reply_markup=keyboard)
        bot.register_next_step_handler(msg, Adress)
    
    elif call.data == "profile":
        bot.send_message(call.from_user.id, 'Давайте заполним ваш профиль!')
        msg = bot.send_message(call.from_user.id, 'Введите ваше имя и фамилию:', reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, process_profile_name)

def process_profile_name(message):
    full_name = message.text
    msg = bot.send_message(message.from_user.id, 'Напишите коротко о себе (био):')
    bot.register_next_step_handler(msg, process_profile_bio, full_name)

def process_profile_bio(message, full_name):
    bio = message.text
    msg = bot.send_message(message.from_user.id, 'Отправьте ваше фото для профиля (необязательно):\n\n_Пропустите этот шаг, нажав /skip_', parse_mode="Markdown")
    bot.register_next_step_handler(msg, process_profile_photo, full_name, bio)

def process_profile_photo(message, full_name, bio):
    user_id = message.from_user.id
    photo_url = ""
    
    if message.content_type == 'photo' and not message.text == '/skip':
        # Сохраняем фото пользователя
        photo_file = message.photo[-1]
        photo_result = download_and_save_photo(photo_file, user_id)
        if photo_result['success']:
            photo_url = photo_result['photo_url']
    
    # Сохраняем пользователя в БД
    user_db_id = save_user_to_db(user_id, full_name, bio, photo_url)
    
    if user_db_id:
        response_text = '✅ Ваш профиль успешно сохранен!\n\n'
        response_text += f'👤 *Имя:* {full_name}\n'
        response_text += f'📝 *Био:* {bio}\n'
        
        if photo_url:
            response_text += '🖼 *Фото:* сохранено\n'
            bot.send_photo(message.from_user.id, message.photo[-1].file_id, 
                          caption=response_text, parse_mode="Markdown")
        else:
            response_text += '🖼 *Фото:* не добавлено\n'
            bot.send_message(message.from_user.id, response_text, parse_mode="Markdown")
    else:
        bot.send_message(message.from_user.id, '❌ Произошла ошибка при сохранении профиля.')
    
    get_menu(message)

def Adress(message):
    district = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_location = KeyboardButton("📍 Отправить местоположение", request_location=True)
    keyboard.add(btn_location)
    msg = bot.send_message(message.from_user.id, 'Напишите точный адрес или отправьте геопозицию', reply_markup=keyboard)
    bot.register_next_step_handler(msg, TypeHome, district)

def TypeHome(message, district):
    if message.content_type == 'location':
        address = get_address_yandex(message.location.latitude, message.location.longitude)
    elif message.content_type == 'text':
        address = message.text
    else:
        address = "Адрес не указан"
    
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    house = telebot.types.KeyboardButton(text="Частный дом")  
    flat = telebot.types.KeyboardButton(text="Квартира")   
    keyboard.add(house, flat)
    msg = bot.send_message(message.from_user.id, 'Тип жилья', reply_markup=keyboard)
    bot.register_next_step_handler(msg, Square, district, address)

def Square(message, district, address):
    typeHome = message.text
    msg = bot.send_message(message.from_user.id, 'Напишите площадь жилья в м²', reply_markup=ReplyKeyboardRemove())
    bot.register_next_step_handler(msg, Tenants, district, address, typeHome)

def Tenants(message, district, address, typeHome):
    square = message.text
    msg = bot.send_message(message.from_user.id, 'Количество соседей')
    bot.register_next_step_handler(msg, TimeOfStay, district, address, typeHome, square)

def TimeOfStay(message, district, address, typeHome, square):
    tenants = message.text
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    one_night = telebot.types.KeyboardButton(text="На одну ночь")
    one_week = telebot.types.KeyboardButton(text="На одну неделю")
    one_mounth = telebot.types.KeyboardButton(text="На один месяц")
    hz = telebot.types.KeyboardButton(text="Договор")
    keyboard.add(one_night, one_week, one_mounth, hz)
    msg = bot.send_message(message.from_user.id, 'Введите время, на которое готовы подселить к себе соседа', reply_markup=keyboard)
    bot.register_next_step_handler(msg, PropertyTitle, district, address, typeHome, square, tenants)

def PropertyTitle(message, district, address, typeHome, square, tenants):
    time_of_stay = message.text
    keyboard = telebot.types.ReplyKeyboardRemove()
    msg = bot.send_message(message.from_user.id, 'Придумайте название для вашего объявления (например: "Уютная квартира в центре"):', reply_markup=keyboard)
    bot.register_next_step_handler(msg, PropertyDescription, district, address, typeHome, square, tenants, time_of_stay)

def PropertyDescription(message, district, address, typeHome, square, tenants, time_of_stay):
    title = message.text
    msg = bot.send_message(message.from_user.id, 'Опишите ваше жилье подробнее:')
    bot.register_next_step_handler(msg, PropertyPrice, district, address, typeHome, square, tenants, time_of_stay, title)

def PropertyPrice(message, district, address, typeHome, square, tenants, time_of_stay, title):
    description = message.text
    msg = bot.send_message(message.from_user.id, 'Введите плату\n\n_P\.S\.Это необязательно должны быть деньги_', reply_markup=ReplyKeyboardRemove(), parse_mode="MarkdownV2")
    bot.register_next_step_handler(msg, PropertyPhotos, district, address, typeHome, square, tenants, time_of_stay, title, description)

def PropertyPhotos(message, district, address, typeHome, square, tenants, time_of_stay, title, description):
    price_text = message.text
    
    try:
        if price_text.lower() in ['бесплатно', 'free', '0', 'ноль']:
            price = 0
        else:
            price = int(''.join(filter(str.isdigit, price_text)))
    except:
        price = 0
    
    user_id = message.from_user.id
    msg = bot.send_message(user_id, 
                          'Теперь отправьте фотографии вашего дома (можно несколько фото подряд).\nПосле всех фото напишите "Готово"')
    
    user_data = {
        'user_id': user_id,
        'district': district,
        'address': address,
        'typeHome': typeHome,
        'square': square,
        'tenants': tenants,
        'time_of_stay': time_of_stay,
        'title': title,
        'description': description,
        'price': price,
        'photos': []
    }
    
    bot.register_next_step_handler(msg, collect_property_photos, user_data)

def collect_property_photos(message, user_data):
    """Сбор фотографий для объявления"""
    if message.content_type == 'photo':
        photo_file = message.photo[-1]
        user_data['photos'].append(photo_file)
        
        bot.send_message(message.from_user.id, 
                        f'✅ Фото {len(user_data["photos"])} получено. Отправьте еще фото или напишите "Готово"')
        
        bot.register_next_step_handler(message, collect_property_photos, user_data)
    
    elif message.content_type == 'text' and message.text.lower() in ['готово', 'готов', 'все', 'закончить']:
        if len(user_data['photos']) == 0:
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            yes_btn = KeyboardButton("✅ Да, без фото")
            no_btn = KeyboardButton("🔙 Назад, добавлю фото")
            markup.add(yes_btn, no_btn)
            
            msg = bot.send_message(message.from_user.id, 
                                  'Вы не отправили ни одного фото. Продолжить без фото?', 
                                  reply_markup=markup)
            bot.register_next_step_handler(msg, confirm_no_photos, user_data)
            return
        
        save_property_to_database(message, user_data)
    
    else:
        bot.send_message(message.from_user.id, 'Пожалуйста, отправьте фото или напишите "Готово"')
        bot.register_next_step_handler(message, collect_property_photos, user_data)

def confirm_no_photos(message, user_data):
    if message.text == "✅ Да, без фото":
        save_property_to_database(message, user_data)
    else:
        msg = bot.send_message(message.from_user.id, 
                              'Отправьте фотографии вашего дома (можно несколько фото подряд).\nПосле всех фото напишите "Готово"',
                              reply_markup=ReplyKeyboardRemove())
        bot.register_next_step_handler(msg, collect_property_photos, user_data)

def save_property_to_database(message, user_data):
    """Сохранение всего объявления в БД"""
    bot.send_chat_action(message.from_user.id, 'typing')
    
    # 1. Сохраняем пользователя в БД
    user_db_id = save_user_to_db(
        user_data['user_id'],
        message.from_user.full_name or "Пользователь",
        bio=f"TG: @{message.from_user.username}" if message.from_user.username else "Пользователь Telegram"
    )
    
    if not user_db_id:
        bot.send_message(message.from_user.id, '❌ Ошибка: не удалось сохранить данные пользователя')
        get_menu(message)
        return
    
    # 2. Сохраняем объявление в таблицу properties
    property_id = save_property_to_db(
        user_db_id,
        user_data['price'],
        user_data['title'],
        user_data['description'],
        user_data['district'],
        user_data['address'],
        user_data['typeHome'],
        user_data['square'],
        user_data['tenants'],
        user_data['time_of_stay']
    )
    
    if not property_id:
        bot.send_message(message.from_user.id, '❌ Ошибка: не удалось сохранить объявление')
        get_menu(message)
        return
    
    # 3. Сохраняем фотографии в таблицу prop_image
    photo_urls = []
    if user_data['photos']:
        for i, photo_file in enumerate(user_data['photos']):
            photo_result = download_and_save_photo(photo_file, user_data['user_id'], property_id)
            if photo_result['success']:
                photo_urls.append(photo_result['photo_url'])
        
        if photo_urls:
            # Фотографии сохраняются в таблицу prop_image
            save_property_images(property_id, photo_urls)
    
    # 4. Отправляем подтверждение пользователю
    summary = (
        f'✅ Объявление успешно сохранено!\n\n'
        f'🏠 *Адрес:* {user_data["address"]}\n'
        f'📏 *Площадь:* {user_data["square"]} м²\n'
        f'💰 *Плата:* {user_data["price"] if user_data["price"] > 0 else "Бесплатно"} руб.\n'
        f'📷 *Фотографий:* {len(photo_urls)} добавлено\n\n'
        f'ID объявления: #{property_id}'
    )
    
    if user_data['photos']:
        bot.send_photo(message.from_user.id, 
                      user_data['photos'][0].file_id,
                      caption=summary,
                      parse_mode="Markdown")
    else:
        bot.send_message(message.from_user.id, summary, parse_mode="Markdown")
    
    # 5. Предлагаем добавить в избранное
    keyboard = types.InlineKeyboardMarkup()
    fav_button = types.InlineKeyboardButton(
        text="⭐ Добавить в избранное", 
        callback_data=f"fav_{property_id}"
    )
    keyboard.add(fav_button)
    
    bot.send_message(message.from_user.id, 
                    'Хотите добавить это объявление в избранное?',
                    reply_markup=keyboard)
    
    get_menu(message)

@bot.callback_query_handler(func=lambda call: call.data.startswith('fav_'))
def add_to_favorites(call):
    try:
        property_id = int(call.data.split('_')[1])
        user_db_id = save_user_to_db(call.from_user.id, call.from_user.full_name or "Пользователь")
        
        if user_db_id and save_to_favorites(user_db_id, property_id):
            bot.answer_callback_query(call.id, "✅ Добавлено в избранное!")
        else:
            bot.answer_callback_query(call.id, "❌ Ошибка добавления в избранное")
    except Exception as e:
        print(f"Ошибка добавления в избранное: {e}")
        bot.answer_callback_query(call.id, "❌ Произошла ошибка")

@bot.message_handler(commands=['start'])
def get_start(message):
    print(f"\nСтарт! Пользователь: {message.from_user.id}")
    
    # Создаем папку для загрузок
    os.makedirs(UPLOAD_PATH, exist_ok=True)
    os.makedirs(os.path.join(UPLOAD_PATH, 'thumbs'), exist_ok=True)
    
    keyboard_theme = telebot.types.InlineKeyboardMarkup()
    sub = types.InlineKeyboardButton("Подписаться ✔", url=URL_channel)
    key_check = types.InlineKeyboardButton(text='Проверить подписку ✔', callback_data='check')
    keyboard_theme.add(sub, key_check)
    
    bot.send_chat_action(chat_id=message.from_user.id, action="typing")
    time.sleep(1)
    
    welcome_text = (
        "🏡 *Добро пожаловать в Homeder!*\n\n"
        "Здесь вы можете:\n"
        "• 🏠 Разместить объявление о жилье\n"
        "• 👤 Создать свой профиль\n"
        "• 🔍 Найти соседей или жилье\n\n"
        "Для начала работы подпишитесь на наш канал:"
    )
    
    bot.send_message(message.from_user.id, welcome_text, 
                    parse_mode="Markdown", reply_markup=keyboard_theme)

@bot.message_handler(commands=['menu']) # menu
def get_menu(message):
    keyboard_menu = webAppKeyboard(message.from_user.id)
    my_home = types.InlineKeyboardButton(text="🏠 Мой дом", callback_data='my_home')   
    my_profile = types.InlineKeyboardButton(text="👤 Мой профиль", callback_data='profile')  
    keyboard_menu.add(my_home, my_profile)
    bot.send_message(message.from_user.id, '📋 *Главное меню:*', parse_mode="Markdown", reply_markup=keyboard_menu)

@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = (
        "📖 *Помощь по боту Homeder*\n\n"
        "*/start* - Начать работу с ботом\n"
        "*/menu* - Открыть главное меню\n"
        "*/help* - Показать это сообщение\n\n"
        "*Как разместить объявление:*\n"
        "1. Нажмите '🏠 Мой дом'\n"
        "2. Заполните информацию о жилье\n"
        "3. Добавьте фотографии\n"
        "4. Получите ID объявления\n\n"
        "*Как создать профиль:*\n"
        "1. Нажмите '👤 Мой профиль'\n"
        "2. Введите имя и фамилию\n"
        "3. Добавьте описание о себе\n"
        "4. Загрузите фото (опционально)"
    )
    bot.send_message(message.from_user.id, help_text, parse_mode="Markdown")
import time
from requests.exceptions import ReadTimeout
if __name__ == '__main__':
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=60)
        except ReadTimeout as e:
            print(f"Timeout error: {e}")
            print("Reconnecting in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"Other error: {e}")
            time.sleep(5)
