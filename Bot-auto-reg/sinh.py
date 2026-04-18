########################################################## TG-bot by Vology #############################################################################
# Привет, мой дорогой друг. Если ты читаешь этот комментарий, то скорее всего ты работаешь над скриптом, котороый писал я.
# Уверен, во время работы над ним у тебя появятся вопросы... Много вопросов. 
# Если тебе потребуется помощь, пиши сюда TG: @onevology
# Удачи! <3

# Уважаемый заказчик, просьба не удалять данный комментарий. Он может ускорить процесс апдейта/починки программы
# Спасибо

# eng

# Hello, my dear friend. If you're reading this comment, then you're probably working on the script I wrote.
# I'm sure you'll have some questions while working on it... A lot of questions. 
# If you need help, write here TG: @onevology
# Good luck! <3

# Dear customer, please do not delete this comment. It can speed up the process of updating/fixing the program.
# Thank you
import asyncio
import os
import random
import threading
import telebot
import time
from datetime import datetime, timedelta
from telethon import TelegramClient, events
from configparser import ConfigParser
from typing import List, Dict, Optional, Tuple
from telethon.tl.functions.users import GetFullUserRequest
import telethon
import tracemalloc
import json
tracemalloc.start()
# Добавляем глобальную переменную для интервала между сессиями
account_delay = 10 * 60  # 10 минут по умолчанию

# I love you

# Конфигурация Telegram бота
time_to_stop = 100**100
bot_token = '7701414039:AAG-NEmha5l8us25r1b0ZbqwfcsKvXVMQnw'
admins = [968218637, 7226305438, 1743138840]  # Ваш ID
account_delay = 10 * 60
# Конфигурация рассыльщика
test_group = -1002612629127  # ID тестовой группы
test_mode = True  # True - отправка только в тестовый чат
base_delay = 60 * 60  # Базовый интервал между рассылками (1 час)

# Инициализация
bot = telebot.TeleBot(bot_token)
sessions_dir = "sessions/"  # Папка с сессионными файлами
proxies_dir = "proxies/"    # Папка с прокси
messages_dir = "messages/"  # Папка с текстами сообщений

# Глобальные переменные
active_clients: List[TelegramClient] = []
bot_threads: List[threading.Thread] = []
stop_flags: Dict[str, threading.Event] = {}
pending_responses: Dict[int, Tuple[datetime, str]] = {}  # Для отслеживания ожидающих ответов
user_states: Dict[int, Dict[str, str]] = {}  # Для хранения состояний пользователей
auth_sessions: Dict[int, Dict[str, str]] = {}  # Для хранения данных во время авторизации
session_messages: Dict[str, Dict[str, str]] = {}  # Для хранения индивидуальных сообщений сессий
sensitive_chats: List[int] = []  # Чувствительные чаты (где нельзя упоминать @username)
users_nahui = []
# Ключевые слова для анализа ответов
positive_keywords = ["да", "куплю", "буду", "нужно", "интересно", "интересует", "согласен", "хочу"]
negative_keywords = ["нет", "не буду", "не нужно", "не интересует", "отказываюсь", "не хочу"]

# Стандартные тексты сообщений
default_messages = {
    "initial_message": "Занимаюсь копирайтингом, кому требуются услуги — напишите в лс. 🚀",
    "sensitive_message": "Занимаюсь копирайтингом, кому требуются услуги — напишите мне. 🚀",
    "first_reply": "Спасибо за ваше сообщение! Я свяжусь с вами в ближайшее время.",
    "second_reply": "Можете уточнить, какие именно услуги вас интересуют?",
    "follow_up_question": "Вы еще заинтересованы в наших услугах?",
    "positive_response": "Отлично! Я свяжусь с вами для уточнения деталей.",
    "negative_response": "Жаль, что вы передумали. Если решите воспользоваться нашими услугами в будущем, буду рад помочь!"
}

# Создаем необходимые директории
os.makedirs(sessions_dir, exist_ok=True)
os.makedirs(proxies_dir, exist_ok=True)
os.makedirs(messages_dir, exist_ok=True)

# Инициализация конфига
config = ConfigParser()
if not os.path.exists('data'):
    os.makedirs('data')
if not os.path.exists('data/config.ini'):
    config.add_section('Main')
    config.set('Main', 'period', '1')
    config.set('Main', 'check_test', 'False')
    config.set('Main', 'id_test', '')
    with open('data/config.ini', 'w') as f:
        config.write(f)
else:
    config.read('data/config.ini')

def load_session_messages():
    if os.path.exists(os.path.join(sessions_dir, 'session_messages.ini')):
        session_config = ConfigParser()
        session_config.read(os.path.join(sessions_dir, 'session_messages.ini'), encoding="utf-8")
        
        # Очищаем текущие сообщения
        session_messages.clear()
        
        for section in session_config.sections():
            # Создаем словарь для этой сессии
            session_data = {}
            
            # Загружаем все доступные поля
            for key in ['normal', 'sensitive', 'first_reply', 'second_reply', 
                       'follow_up', 'positive', 'negative']:
                if session_config.has_option(section, key):
                    session_data[key] = session_config.get(section, key)
                else:
                    # Если поле отсутствует, используем значение из default_messages
                    session_data[key] = default_messages.get(f"{key}_message" if key in ['normal', 'sensitive'] else f"{key}_response" if key in ['positive', 'negative'] else key, "")
            
            # Сохраняем данные для этой сессии
            session_messages[section] = session_data
    
    # Добавляем дефолтные сообщения, если файла нет
    else:
        session_messages['default'] = default_messages
def load_session_messages2():
    if os.path.exists(os.path.join(sessions_dir, 'session_messages.ini')):
        session_config = ConfigParser()
        session_config.read(os.path.join(sessions_dir, 'session_messages.ini'), encoding="utf-8")
        
        # Очищаем текущие сообщения
        session_messages.clear()
        
        for section in session_config.sections():
            # Создаем словарь для этой сессии
            session_data = {}
            
            # Загружаем все доступные поля
            for key in ['normal', 'sensitive', 'first_reply', 'second_reply', 
                       'follow_up', 'positive', 'negative']:
                if session_config.has_option(section, key):
                    session_data[key] = session_config.get(section, key)
                else:
                    # Если поле отсутствует, используем значение из default_messages
                    session_data[key] = default_messages.get(f"{key}_message" if key in ['normal', 'sensitive'] else f"{key}_response" if key in ['positive', 'negative'] else key, "")
            
            # Сохраняем данные для этой сессии
            session_messages[section] = session_data
    
    # Добавляем дефолтные сообщения, если файла нет
    else:
        session_messages['default'] = default_messages
    return session_messages
def save_session_messages():
    session_config = ConfigParser()
    
    for session, messages in session_messages.items():
        session_config.add_section(session)
        
        # Сохраняем все поля, даже если они пустые
        session_config.set(session, 'normal', messages.get('normal', default_messages['initial_message']))
        session_config.set(session, 'sensitive', messages.get('sensitive', default_messages['sensitive_message']))
        session_config.set(session, 'first_reply', messages.get('first_reply', default_messages['first_reply']))
        session_config.set(session, 'second_reply', messages.get('second_reply', default_messages['second_reply']))
        session_config.set(session, 'follow_up', messages.get('follow_up', default_messages['follow_up_question']))
        session_config.set(session, 'positive', messages.get('positive', default_messages['positive_response']))
        session_config.set(session, 'negative', messages.get('negative', default_messages['negative_response']))
    
    with open(os.path.join(sessions_dir, 'session_messages.ini'), 'w', encoding="utf-8") as f:
        session_config.write(f)

# Загрузка чувствительных чатов
def load_sensitive_chats():
    global sensitive_chats
    if os.path.exists(os.path.join(messages_dir, 'sensitive_chats.txt')):
        with open(os.path.join(messages_dir, 'sensitive_chats.txt'), 'r') as f:
            sensitive_chats = [int(line.strip()) for line in f.readlines() if line.strip()]

def save_sensitive_chats():
    with open(os.path.join(messages_dir, 'sensitive_chats.txt'), 'w') as f:
        for chat_id in sensitive_chats:
            f.write(f"{chat_id}\n")

# Загрузка данных при старте
load_session_messages()
load_sensitive_chats()

# Загрузка/сохранение текстов сообщений
def load_messages():
    messages = default_messages.copy()
    if os.path.exists(os.path.join(messages_dir, 'messages.ini')):
        msg_config = ConfigParser()
        msg_config.read(os.path.join(messages_dir, 'messages.ini'), encoding="utf-8")
        if 'Messages' in msg_config:
            for key in messages.keys():
                if key in msg_config['Messages']:
                    messages[key] = msg_config['Messages'][key]
    return messages

def save_messages(messages):
    msg_config = ConfigParser()
    msg_config['Messages'] = messages
    with open(os.path.join(messages_dir, 'messages.ini'), 'w', encoding="utf-8") as f:
        msg_config.write(f)

messages_config = load_messages()

def load_config():
    config.read('data/config.ini')
    return {
        'period': int(config.get('Main', 'period')),
        'check_test': config.get('Main', 'check_test') == "True",
        'id_test': config.get('Main', 'id_test')
    }

def save_config(data):
    config.set('Main', 'period', str(data['period']))
    config.set('Main', 'id_test', data['id_test'])
    config.set('Main', 'check_test', str(data['check_test']))
    with open('data/config.ini', 'w') as f:
        config.write(f)
# Добавляем глобальную переменную для хранения пользователей с запущенным сценарием
session_users: Dict[str, List[int]] = {}

# Функция для загрузки сохраненных пользователей
def load_session_users():
    global session_users
    if os.path.exists(os.path.join(sessions_dir, 'session_users.json')):
        try:
            with open(os.path.join(sessions_dir, 'session_users.json'), 'r') as f:
                session_users = json.load(f)
                # Преобразуем ключи в int (так как JSON сохраняет ключи как строки)
                session_users = {k: [int(i) for i in v] for k, v in session_users.items()}
        except Exception as e:
            print(f"Ошибка при загрузке session_users: {e}")
            session_users = {}

# Функция для сохранения пользователей
def save_session_users():
    try:
        with open(os.path.join(sessions_dir, 'session_users.json'), 'w') as f:
            json.dump(session_users, f)
    except Exception as e:
        print(f"Ошибка при сохранении session_users: {e}")
# Добавляем команду для очистки списка пользователей
@bot.message_handler(commands=['clear_session_users'])
def clear_session_users(message):
    if message.from_user.id not in admins:
        return
    
    global session_users
    session_files = [f.replace('.session', '') for f in os.listdir(sessions_dir) 
                   if f.endswith('.session')]
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    for session in session_files:
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text=f"🧹 Очистить {session}",
                callback_data=f'clear_users_{session}'
            )
        )
    
    bot.send_message(
        message.chat.id,
        "Выберите сессию для очистки списка пользователей:",
        reply_markup=keyboard
    )

@bot.callback_query_handler(func=lambda call: call.data.startswith('clear_users_'))
def clear_users_callback(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
        return
    
    session = call.data.split('_')[2]
    if session in session_users:
        session_users[session] = []
        save_session_users()
        bot.answer_callback_query(call.id, f"✅ Список пользователей для {session} очищен")
    else:
        bot.answer_callback_query(call.id, f"❌ Сессия {session} не найдена")

# Загружаем при старте
load_session_users()
async def create_client(session_file):
    """Создает и настраивает клиент для сессионного файла"""
    session_path = os.path.join(sessions_dir, session_file)
    phone_number = session_file.replace('.session', '')
    api_file = os.path.join(sessions_dir, f"{phone_number}.txt")
    
    if not os.path.exists(api_file):
        print(f"[{session_file}] Файл с API данными не найден!")
        return None
    
    with open(api_file, "r") as f:
        api_data = f.read().split("::")
        if len(api_data) != 2:
            print(f"[{session_file}] Неверный формат API данных!")
            return None
        
        api_id = int(api_data[0])
        api_hash = api_data[1]
    
    client = TelegramClient(session_path, api_id, api_hash)
    print(session_path)
    # Добавляем обработчик сообщений
    @client.on(events.NewMessage(incoming=True, func=lambda e: e.is_private))
    async def handle_new_message(event):
        global users_nahui
        try:
            
            sender = await event.get_sender()
            user_id = sender.id
            if user_id in users_nahui:
                return
            users_nahui.append(user_id)
            message_text = event.message.text
            session_file = client.session.filename.replace('.session', '')
            
            print(f"[{session_file}] Получено сообщение от {sender.first_name}: {message_text}")
            
            # Проверяем, есть ли пользователь в списке для этой сессии
            if session_file in session_users and user_id in session_users[session_file]:
                print(f"[{session_file}] Пользователь {user_id} уже в списке, пропускаем сценарий")
                return
                
            # Добавляем пользователя в список
            if session_file not in session_users:
                session_users[session_file] = []
            session_users[session_file].append(user_id)
            save_session_users()
            
            # Получаем сообщения для этой сессии
            replyis = load_session_messages2()
            name_key = client.session.filename.replace("sessions/", "").replace(".session", "")
            
            # Проверяем ключевые слова в ответе
            if any(word.lower() in message_text.lower() for word in positive_keywords):
                await event.reply(replyis[name_key]["positive"])
                for id_admin in admins:
                    user = await client.get_entity(user_id)
                    username = user.username if user.username else f"id{user_id}"
                    bot.send_message(id_admin, f"@{username} ответил положительно!")
                return
            elif any(word.lower() in message_text.lower() for word in negative_keywords):
                await event.reply(replyis[name_key]["negative"])
                return
            
            # Отправляем первое сообщение через 5 минут
            asyncio.create_task(
                delayed_reply(client, event, replyis[name_key]["first_reply"], delay=5*60)
            )
            
            # Отправляем второе сообщение через 5 минут и 5 секунд
            asyncio.create_task(
                delayed_reply(client, event, replyis[name_key]["second_reply"], delay=5*60 + 5)
            )
            
            # Запланировать контрольный вопрос через 2 дня
            asyncio.create_task(
                delayed_reply(client, event, replyis[name_key]["follow_up"], delay=2*24*60*60)
            )
            
        except Exception as e:
            print(f"[{session_file}] Ошибка в обработчике сообщений: {e}")


    try:
        # Подключаем клиент и запускаем обработчики
        await client.connect()
        if not await client.is_user_authorized():
            print(f"[{session_file}] Клиент не авторизован!")
            return None
        
        # Добавляем клиент в список активных
        active_clients.append(client)
        return client
    except Exception as e:
        print(f"[{session_file}] Ошибка при подключении клиента: {e}")
        return None

async def delayed_reply(client, event, message, delay):
    """Отправляет отложенное сообщение"""
    await asyncio.sleep(delay)
    try:
        await event.reply(message)
        print(f"Отправлено отложенное сообщение: {message}")
    except Exception as e:
        print(f"Ошибка при отправке отложенного сообщения: {e}")
@bot.message_handler(commands=['set_delay'])
def set_delay_command(message):
    if message.from_user.id not in admins:
        return
    
    msg = bot.send_message(message.chat.id, "Введите интервал между аккаунтами в минутах:")
    bot.register_next_step_handler(msg, process_delay_input)

def process_delay_input(message):
    global account_delay
    try:
        minutes = int(message.text)
        if minutes < 1:
            raise ValueError
        account_delay = minutes * 60
        bot.send_message(message.chat.id, f"✅ Интервал между аккаунтами установлен: {minutes} минут")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат. Введите число минут (целое число больше 0)")
async def send_messages(client, session_file):
    """Отправка сообщений от имени клиента"""
    stop_flag = stop_flags.get(session_file)
    if stop_flag and stop_flag.is_set():
        return
    
    phone_number = session_file.replace('.session', '')
    dialogs = await client.get_dialogs()
    sended = 0
    not_sended = 0
    

    
    for dialog in dialogs:
        if stop_flag and stop_flag.is_set():
            break
            
        if test_mode and dialog.id != test_group:
            continue
                
        if dialog.is_group or (dialog.is_channel and not dialog.entity.broadcast):
            try:
                # Выбираем сообщение в зависимости от типа чата
                replyis = load_session_messages2()
                print(client.session.filename)
                name_key = client.session.filename.replace("sessions/", "").replace(".session", "")
                if dialog.id in sensitive_chats:
                    message_text = replyis[name_key]["sensitive"]
                else:
                    message_text = replyis[name_key]["normal"]
                
                await client.send_message(dialog.id, message_text)
                print(f"[{session_file}] Сообщение отправлено в {dialog.name} (ID: {dialog.id})")
                sended += 1
                await asyncio.sleep(1 + random.random())
            except Exception as e:
                print(f"[{session_file}] Ошибка при отправке: {str(e)}")
                not_sended += 1
                
                if "FLOOD_WAIT" in str(e):
                    import re
                    match = re.search(r'FLOOD_WAIT_(\d+)', str(e))
                    wait_time = int(match.group(1)) + 5 if match else 60
                    print(f"[{session_file}] Флуд, ждем {wait_time} секунд")
                    await asyncio.sleep(wait_time)

async def run_client(client, session_file, period):
    """Запускает цикл рассылки для одного клиента"""
    stop_flags[session_file] = threading.Event()
    global time_to_stop
    
    try:
        await asyncio.sleep(random.randint(1200, 7200))
        await client.start()
        
        while True:
            if stop_flags[session_file].is_set():
                break

            print(f"[{session_file}] Запуск рассылки...")
            await send_messages(client, session_file)
            
            if stop_flags[session_file].is_set():
                break
                
            delay = base_delay * period + random.randint(0, 60*60)
            print(f"[{session_file}] Ожидание {delay//3600} ч {(delay%3600)//60} мин до следующей рассылки")
            for _ in range(delay):
                if stop_flags[session_file].is_set() or time_to_stop == 0:
                    break
                await asyncio.sleep(1)
    except Exception as e:
        print(f"[{session_file}] Ошибка в цикле рассылки: {e}")
    finally:
        try:
            if client.is_connected():
                await client.disconnect()
        except Exception:
            pass
        if session_file in stop_flags:
            del stop_flags[session_file]
        if client in active_clients:
            active_clients.remove(client)

def run_bot_in_thread(session_file, period):
    """Запускает бота в отдельном потоке"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        client = loop.run_until_complete(create_client(session_file))
        if not client:
            return
            
        loop.create_task(run_client(client, session_file, period))
        loop.run_forever()
    except Exception as e:
        print(f"[{session_file}] Ошибка в потоке: {e}")
    finally:
        loop.close()

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "⛔ Доступ запрещен")
        return
    
    bot.send_message(
        message.chat.id,
        "👨‍💻 Админ-панель управления ботом\n\n"
        "Используйте команды:\n"
        "/panel - открыть панель управления\n"
        "/status - статус бота\n"
        "/start_bot - запустить бота\n"
        "/stop_bot - остановить бота\n"
        "/add_session - добавить новую сессию\n"
        "/edit_texts - редактировать тексты сообщений\n"
        "/edit_keywords - редактировать ключевые слова\n"
        "/sensitive_chats - управление чувствительными чатами\n"
        "/edit_session_messages - редактировать сообщения сессий"
    )

def create_panel_keyboard():
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        telebot.types.InlineKeyboardButton('⚙️ Настройки', callback_data='settings'),
        telebot.types.InlineKeyboardButton('🔄 Статус', callback_data='status')
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton('▶️ Запустить', callback_data='start_bot'),
        telebot.types.InlineKeyboardButton('🛑 Остановить', callback_data='stop_bot')
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton('➕ Добавить сессию', callback_data='add_session'),
        telebot.types.InlineKeyboardButton('🗑 Удалить сессию', callback_data='delete_session')
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton('📝 Тексты', callback_data='edit_texts'),
        telebot.types.InlineKeyboardButton('✏️ Сообщения сессий', callback_data='edit_session_messages')
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton('🔑 Ключ. слова', callback_data='edit_keywords'),
        telebot.types.InlineKeyboardButton('🔒 Чувств. чаты', callback_data='sensitive_chats')
    )
    return keyboard

@bot.message_handler(commands=['panel'])
def panel(message):
    if message.from_user.id not in admins:
        bot.send_message(message.chat.id, "⛔ Доступ запрещен")
        return
    
    bot.send_message(
        message.chat.id,
        "📊 Панель управления ботом",
        reply_markup=create_panel_keyboard()
    )

@bot.message_handler(commands=['status'])
def status_command(message):
    if message.from_user.id not in admins:
        return
    send_status_message(message.chat.id)

def send_status_message(chat_id):
    cfg = load_config()
    
    all_session_files = [f.replace('.session', '') for f in os.listdir(sessions_dir) 
                       if f.endswith('.session')]
    
    active_sessions = [t.name for t in bot_threads if t.is_alive()]
    
    proxy_files = os.listdir(proxies_dir)
    
    status_text = (
        f"📊 Статус бота:\n"
        f"• Всего сессий: {len(all_session_files)}\n"
        f"• Активных сессий: {len(active_sessions)}\n"
        f"• Запущенные сессии: {', '.join(active_sessions) if active_sessions else 'нет'}\n\n"
        f"⚙️ Текущие настройки:\n"
        f"• Файлы прокси: {len(proxy_files)} шт\n"
        f"• Период: {cfg['period']} час(ов)\n"
        f"• Тестовый режим: {'Вкл' if cfg['check_test'] else 'Выкл'}\n"
        f"• ID тестового чата: {cfg['id_test']}\n"
        f"• Чувствительных чатов: {len(sensitive_chats)}"
    )
    
    bot.send_message(chat_id, status_text)

@bot.callback_query_handler(func=lambda call: call.data == 'status')
def status_callback(call):
    try:
        if call.from_user.id not in admins:
            bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
            return
        
        try:
            bot.delete_message(call.message.chat.id, call.message.message_id)
        except Exception as e:
            print(f"Ошибка при удалении сообщения: {e}")
        
        send_status_message(call.message.chat.id)
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Ошибка в обработчике статуса: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ Ошибка при получении статуса")
        except:
            pass

def process_phone_number(message):
    try:
        phone_number = message.text.strip()
        if not phone_number.startswith('+'):
            bot.send_message(message.chat.id, "❌ Номер должен начинаться с '+' (международный формат). Попробуйте снова.")
            return
        
        user_id = message.from_user.id
        auth_sessions[user_id] = {
            'phone_number': phone_number,
            'step': 'api_id'
        }
        
        msg = bot.send_message(message.chat.id, "Введите API ID:")
        bot.register_next_step_handler(msg, process_api_id)
    except Exception as e:
        print(f"Ошибка в process_phone_number: {e}")
        bot.send_message(message.chat.id, "❌ Произошла ошибка. Попробуйте снова.")

def process_api_id(message):
    user_id = message.from_user.id
    if user_id not in auth_sessions:
        bot.send_message(message.chat.id, "❌ Сессия авторизации не найдена. Начните заново.")
        return
    
    try:
        api_id = int(message.text.strip())
    except ValueError:
        bot.send_message(message.chat.id, "❌ API ID должен быть числом. Попробуйте снова.")
        return
    
    auth_sessions[user_id]['api_id'] = api_id
    auth_sessions[user_id]['step'] = 'api_hash'
    
    msg = bot.send_message(message.chat.id, "Введите API HASH:")
    bot.register_next_step_handler(msg, process_api_hash)
def process_api_hash(message):
    user_id = message.from_user.id
    if user_id not in auth_sessions:
        bot.send_message(message.chat.id, "❌ Сессия авторизации не найдена. Начните заново.")
        return
    
    api_hash = message.text.strip()
    if len(api_hash) < 10:
        bot.send_message(message.chat.id, "❌ API HASH слишком короткий. Попробуйте снова.")
        return
    
    auth_sessions[user_id]['api_hash'] = api_hash
    
    # Сохраняем API данные в файл
    phone_number = auth_sessions[user_id]['phone_number']
    api_file = os.path.join(sessions_dir, f"{phone_number}.txt")
    
    with open(api_file, 'w') as f:
        f.write(f"{auth_sessions[user_id]['api_id']}::{api_hash}")
    
    # Запрашиваем сообщения для этой сессии
    msg = bot.send_message(message.chat.id, "Введите стандартное сообщение для этой сессии:")
    bot.register_next_step_handler(msg, process_normal_message, phone_number)

def process_normal_message(message, phone_number):
    normal_message = message.text
    msg = bot.send_message(message.chat.id, "Введите сообщение для чувствительных чатов (без @username):")
    bot.register_next_step_handler(msg, process_sensitive_message, phone_number, normal_message)

def process_sensitive_message(message, phone_number, normal_message):
    sensitive_message = message.text
    
    # Запрашиваем первое сообщение для лс
    msg = bot.send_message(
        message.chat.id,
        "Введите текст первого ответа в личные сообщения (отправляется через 5 минут):"
    )
    bot.register_next_step_handler(
        msg, 
        process_first_reply_message, 
        phone_number, 
        normal_message, 
        sensitive_message
    )

def process_first_reply_message(message, phone_number, normal_message, sensitive_message):
    first_reply = message.text
    
    # Запрашиваем второе сообщение для лс
    msg = bot.send_message(
        message.chat.id,
        "Введите текст второго ответа в личные сообщения (отправляется через 5 минут 5 секунд):"
    )
    bot.register_next_step_handler(
        msg, 
        process_second_reply_message, 
        phone_number, 
        normal_message, 
        sensitive_message,
        first_reply
    )
def process_second_reply_message(message, phone_number, normal_message, sensitive_message, first_reply):
    second_reply = message.text
    
    # Запрашиваем контрольный вопрос
    msg = bot.send_message(
        message.chat.id,
        "Введите текст контрольного вопроса (отправляется через 2 дня):"
    )
    bot.register_next_step_handler(
        msg, 
        process_follow_up_message, 
        phone_number, 
        normal_message, 
        sensitive_message,
        first_reply,
        second_reply
    )

def process_follow_up_message(message, phone_number, normal_message, sensitive_message, first_reply, second_reply):
    follow_up = message.text
    
    # Запрашиваем ответ на положительный ответ
    msg = bot.send_message(
        message.chat.id,
        "Введите текст ответа на положительный ответ пользователя:"
    )
    bot.register_next_step_handler(
        msg, 
        process_positive_response_message, 
        phone_number, 
        normal_message, 
        sensitive_message,
        first_reply,
        second_reply,
        follow_up
    )


def process_positive_response_message(message, phone_number, normal_message, sensitive_message, first_reply, second_reply, follow_up):
    positive_response = message.text
    
    # Запрашиваем ответ на отрицательный ответ
    msg = bot.send_message(
        message.chat.id,
        "Введите текст ответа на отрицательный ответ пользователя:"
    )
    bot.register_next_step_handler(
        msg, 
        process_negative_response_message, 
        phone_number, 
        normal_message, 
        sensitive_message,
        first_reply,
        second_reply,
        follow_up,
        positive_response
    )

def process_negative_response_message(message, phone_number, normal_message, sensitive_message, first_reply, second_reply, follow_up, positive_response):
    negative_response = message.text
    
    # Сохраняем все сообщения для сессии
    session_messages[phone_number] = {
        'normal': normal_message,
        'sensitive': sensitive_message,
        'first_reply': first_reply,
        'second_reply': second_reply,
        'follow_up': follow_up,
        'positive': positive_response,
        'negative': negative_response
    }
    save_session_messages()
    
    # Запускаем авторизацию
    threading.Thread(
        target=run_auth_session, 
        args=(
            message.from_user.id, 
            phone_number, 
            auth_sessions[message.from_user.id]['api_id'], 
            auth_sessions[message.from_user.id]['api_hash']
        ),
        daemon=True
    ).start()
    
    bot.send_message(
        message.chat.id,
        f"✅ Сессия {phone_number} добавлена! Идет процесс авторизации...",
        reply_markup=create_panel_keyboard()
    )

def run_auth_session(user_id, phone_number, api_id, api_hash):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(authorize_session(user_id, phone_number, api_id, api_hash))
    loop.close()

async def authorize_session(user_id, phone_number, api_id, api_hash):
    session_path = os.path.join(sessions_dir, f"{phone_number}.session")
    client = TelegramClient(session_path, api_id, api_hash)
    
    try:
        await client.connect()
        
        if not await client.is_user_authorized():
            bot.send_message(user_id, "🔐 Начинаем процесс авторизации...")
            
            try:
                # Запрос кода подтверждения
                sent_code = await client.send_code_request(phone_number)
                bot.send_message(user_id, "📲 Код подтверждения отправлен. Введите код в формате: 1 2 3 4 5")
                
                # Ожидаем код
                code = await wait_for_user_input(user_id, 120)
                if not code:
                    bot.send_message(user_id, "❌ Время ожидания кода истекло. Попробуйте снова.")
                    return False
                
                code = code.replace(" ", "")
                
                try:
                    await client.sign_in(phone_number, code)
                    bot.send_message(user_id, "✅ Авторизация успешна! Сессия сохранена.")
                    return True
                    
                except telethon.errors.SessionPasswordNeededError:
                    bot.send_message(user_id, "🔐 Требуется двухфакторная аутентификация. Введите пароль:")
                    
                    # Ожидаем пароль
                    password = await wait_for_user_input(user_id, 120)
                    if not password:
                        bot.send_message(user_id, "❌ Время ожидания пароля истекло. Попробуйте снова.")
                        return False
                    
                    try:
                        await client.sign_in(password=password)
                        bot.send_message(user_id, "✅ Авторизация с паролем успешна! Сессия сохранена.")
                        return True
                    except Exception as e:
                        bot.send_message(user_id, f"❌ Ошибка при вводе пароля: {str(e)}")
                        return False
                        
                except Exception as e:
                    bot.send_message(user_id, f"❌ Ошибка при вводе кода: {str(e)}")
                    return False
                    
            except Exception as e:
                bot.send_message(user_id, f"❌ Ошибка при запросе кода: {str(e)}")
                return False
        else:
            bot.send_message(user_id, "ℹ️ Сессия уже авторизована.")
            return True
            
    except Exception as e:
        bot.send_message(user_id, f"❌ Критическая ошибка при авторизации: {str(e)}")
        return False
        
    finally:
        await client.disconnect()
        if user_id in auth_sessions:
            del auth_sessions[user_id]

user_responses = {}  # Глобальный словарь для хранения ответов пользователей

async def wait_for_user_input(user_id, timeout):
    """Функция ожидания ввода пользователя с таймаутом"""
    user_responses[user_id] = None
    end_time = time.time() + timeout
    
    while time.time() < end_time:
        if user_responses[user_id] is not None:
            response = user_responses[user_id]
            del user_responses[user_id]
            return response
        await asyncio.sleep(0.5)
    
    if user_id in user_responses:
        del user_responses[user_id]
    return None

# Добавляем обработчик всех сообщений
@bot.message_handler(func=lambda m: True)
def handle_all_messages(message):
    """Обработчик всех сообщений для перехвата ответов"""
    if message.from_user.id in user_responses:
        user_responses[message.from_user.id] = message.text


@bot.callback_query_handler(func=lambda call: call.data == 'add_session')
def add_session_callback(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
        return
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="Введите номер телефона (в международном формате, например +79123456789):"
        )
        bot.register_next_step_handler(call.message, process_phone_number)
    except Exception as e:
        print(f"Ошибка при обработке callback: {e}")
        msg = bot.send_message(
            call.message.chat.id,
            "Введите номер телефона (в международном формате, например +79123456789):"
        )
        bot.register_next_step_handler(msg, process_phone_number)
    finally:
        bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data == 'delete_session')
def delete_session_callback(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
        return
    
    session_files = [f.replace('.session', '') for f in os.listdir(sessions_dir) 
                   if f.endswith('.session')]
    
    if not session_files:
        bot.answer_callback_query(call.id, "❌ Нет сессий для удаления")
        return
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    for session in session_files:
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text=f"❌ {session}",
                callback_data=f'confirm_delete_{session}'
            )
        )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data='back_to_panel'
        )
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🗑 Выберите сессию для удаления:",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")
        bot.send_message(
            call.message.chat.id,
            "🗑 Выберите сессию для удаления:",
            reply_markup=keyboard
        )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('confirm_delete_'))
def confirm_delete_session(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
        return
    
    phone_number = call.data.split('_')[2]
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text=f"✅ Да, удалить {phone_number}",
            callback_data=f'do_delete_{phone_number}'
        ),
        telebot.types.InlineKeyboardButton(
            text="❌ Нет, отмена",
            callback_data='delete_session'
        )
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=f"Вы уверены, что хотите удалить сессию {phone_number}?",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")
        bot.send_message(
            call.message.chat.id,
            f"Вы уверены, что хотите удалить сессию {phone_number}?",
            reply_markup=keyboard
        )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('do_delete_'))
def do_delete_session(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
        return
    
    phone_number = call.data.split('_')[2]
    
    session_file = os.path.join(sessions_dir, f"{phone_number}.session")
    api_file = os.path.join(sessions_dir, f"{phone_number}.txt")
    
    try:
        if os.path.exists(session_file):
            os.remove(session_file)
        if os.path.exists(api_file):
            os.remove(api_file)
        
        # Удаляем сообщения для этой сессии
        if phone_number in session_messages:
            del session_messages[phone_number]
            save_session_messages()
        
        bot.answer_callback_query(call.id, f"✅ Сессия {phone_number} удалена")
        delete_session_callback(call)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Ошибка при удалении: {e}")

# Добавляем кнопку в панель настроек
def show_settings(message):
    try:
        cfg = load_config()
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text=f"Тестовый режим: {'✅ Вкл' if cfg['check_test'] else '❌ Выкл'}",
                callback_data='toggle_test_mode'
            )
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text=f"Период рассылки: {cfg['period']} час(ов)",
                callback_data='change_period'
            )
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text=f"Интервал между сессиями: {account_delay//60} мин",
                callback_data='change_session_delay'
            )
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text=f"ID тестового чата: {cfg['id_test']}",
                callback_data='change_test_id'
            )
        )
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text="🔙 Назад в панель",
                callback_data='back_to_panel'
            )
        )
        
        text = "⚙️ Настройки бота:\n\nВыберите параметр для изменения:"
        
    
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Error showing settings: {e}")
# Добавляем обработчик для изменения интервала
@bot.callback_query_handler(func=lambda call: call.data == 'change_session_delay')
def change_session_delay_callback(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
        return
    
    msg = bot.send_message(
        call.message.chat.id,
        f"Текущий интервал между сессиями: {account_delay//60} минут\n"
        "Введите новое значение в минутах (от 1 до 60):",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_new_delay, call.message.message_id)
def process_new_delay(message, original_message_id):
    global account_delay
    try:
        minutes = int(message.text)
        if 1 <= minutes <= 60:
            account_delay = minutes * 60
            bot.send_message(
                message.chat.id,
                f"✅ Интервал между сессиями установлен: {minutes} минут"
            )
            try:
                bot.delete_message(message.chat.id, original_message_id)
            except:
                pass
        else:
            bot.send_message(
                message.chat.id,
                "❌ Значение должно быть от 1 до 60 минут. Попробуйте снова."
            )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Неверный формат. Введите целое число от 1 до 60."
        )

def show_edit_texts_menu(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="✉️ Начальное сообщение",
            callback_data='edit_text_initial_message'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="📩 Первый ответ (5 мин)",
            callback_data='edit_text_first_reply'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="📨 Второй ответ (5 мин 5 сек)",
            callback_data='edit_text_second_reply'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="❓ Контрольный вопрос (2 дня)",
            callback_data='edit_text_follow_up_question'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="✅ Ответ на положительный ответ",
            callback_data='edit_text_positive_response'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="❌ Ответ на отрицательный ответ",
            callback_data='edit_text_negative_response'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data='back_to_panel'
        )
    )
    
    text = "📝 Редактирование текстов сообщений:\n\nВыберите текст для редактирования:"
    
    if hasattr(message, 'message_id'):
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=text,
            reply_markup=keyboard
        )
    else:
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboard
        )

def show_edit_keywords_menu(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="➕ Положительные ключевые слова",
            callback_data='edit_positive_keywords'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="➖ Отрицательные ключевые слова",
            callback_data='edit_negative_keywords'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data='back_to_panel'
        )
    )
    
    text = (
        "🔑 Редактирование ключевых слов:\n\n"
        f"Текущие положительные слова: {', '.join(positive_keywords)}\n"
        f"Текущие отрицательные слова: {', '.join(negative_keywords)}\n\n"
        "Выберите тип ключевых слов для редактирования:"
    )
    
    if hasattr(message, 'message_id'):
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=text,
            reply_markup=keyboard
        )
    else:
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboard
        )

def show_sensitive_chats_menu(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="➕ Добавить чат",
            callback_data='add_sensitive_chat'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="🗑 Удалить чат",
            callback_data='remove_sensitive_chat'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="📋 Список чатов",
            callback_data='list_sensitive_chats'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data='back_to_panel'
        )
    )
    
    text = "🔒 Управление чувствительными чатами:\n\nВыберите действие:"
    
    if hasattr(message, 'message_id'):
        bot.edit_message_text(
            chat_id=message.chat.id,
            message_id=message.message_id,
            text=text,
            reply_markup=keyboard
        )
    else:
        bot.send_message(
            message.chat.id,
            text,
            reply_markup=keyboard
        )
@bot.message_handler(commands=['set_delay'])
def set_delay_command(message):
    if message.from_user.id not in admins:
        return
    
    msg = bot.send_message(message.chat.id, "Введите интервал между аккаунтами в минутах:")
    bot.register_next_step_handler(msg, process_delay_input)

def process_delay_input(message):
    global account_delay
    try:
        minutes = int(message.text)
        if minutes < 1:
            raise ValueError
        account_delay = minutes * 60
        bot.send_message(message.chat.id, f"✅ Интервал между аккаунтами установлен: {minutes} минут")
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверный формат. Введите число минут (целое число больше 0)")

@bot.callback_query_handler(func=lambda call: call.data == 'edit_session_messages')
def edit_session_messages_callback(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
        return
    
    session_files = [f.replace('.session', '') for f in os.listdir(sessions_dir) 
                   if f.endswith('.session')]
    
    if not session_files:
        bot.answer_callback_query(call.id, "❌ Нет доступных сессий")
        return
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    for session in session_files:
        keyboard.add(
            telebot.types.InlineKeyboardButton(
                text=f"✏️ {session}",
                callback_data=f'edit_session_{session}'
            )
        )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data='back_to_panel'
        )
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="📝 Выберите сессию для редактирования сообщений:",
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")
        bot.send_message(
            call.message.chat.id,
            "📝 Выберите сессию для редактирования сообщений:",
            reply_markup=keyboard
        )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_session_'))
def edit_specific_session_callback(call):
    if call.from_user.id not in admins:
        bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
        return
    
    phone_number = call.data.split('_')[2]
    session_data = session_messages.get(phone_number, {
        'normal': default_messages['initial_message'],
        'sensitive': default_messages['sensitive_message'],
        'first_reply': default_messages['first_reply'],
        'second_reply': default_messages['second_reply'],
        'follow_up': default_messages['follow_up_question'],
        'positive': default_messages['positive_response'],
        'negative': default_messages['negative_response']
    })
    
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="✉️ Обычное сообщение",
            callback_data=f'edit_sess_normal_{phone_number}'
        ),
        telebot.types.InlineKeyboardButton(
            text="🔒 Чувствительное сообщение",
            callback_data=f'edit_sess_sensitive_{phone_number}'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="📩 Первый ответ (5 мин)",
            callback_data=f'edit_sess_first_reply_{phone_number}'
        ),
        telebot.types.InlineKeyboardButton(
            text="📨 Второй ответ (5:05)",
            callback_data=f'edit_sess_second_reply_{phone_number}'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="❓ Контрольный вопрос (2 дня)",
            callback_data=f'edit_sess_follow_up_{phone_number}'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="✅ Положительный ответ",
            callback_data=f'edit_sess_positive_{phone_number}'
        ),
        telebot.types.InlineKeyboardButton(
            text="❌ Отрицательный ответ",
            callback_data=f'edit_sess_negative_{phone_number}'
        )
    )
    keyboard.add(
        telebot.types.InlineKeyboardButton(
            text="🔙 Назад",
            callback_data='edit_session_messages'
        )
    )
    
    text = (
        f"📝 Редактирование сообщений для сессии {phone_number}:\n\n"
        f"• Обычное сообщение:\n{session_data['normal']}\n\n"
        f"• Чувствительное сообщение:\n{session_data['sensitive']}\n\n"
        f"• Первый ответ (5 мин):\n{session_data['first_reply']}\n\n"
        f"• Второй ответ (5:05):\n{session_data['second_reply']}\n\n"
        f"• Контрольный вопрос (2 дня):\n{session_data['follow_up']}\n\n"
        f"• Положительный ответ:\n{session_data['positive']}\n\n"
        f"• Отрицательный ответ:\n{session_data['negative']}"
    )
    
    try:
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text=text,
            reply_markup=keyboard
        )
    except Exception as e:
        print(f"Ошибка при редактировании сообщения: {e}")
        bot.send_message(
            call.message.chat.id,
            text,
            reply_markup=keyboard
        )
    
    bot.answer_callback_query(call.id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_sess_normal_'))
def edit_session_normal_callback(call):
    phone_number = call.data.split('_')[3]
    current_text = session_messages.get(phone_number, {}).get('normal', default_messages['initial_message'])
    
    msg = bot.send_message(
        call.message.chat.id,
        f"Текущее обычное сообщение для сессии {phone_number}:\n{current_text}\n\nВведите новое сообщение:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_session_message_update, phone_number, 'normal', call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_sess_sensitive_'))
def edit_session_sensitive_callback(call):
    phone_number = call.data.split('_')[3]
    current_text = session_messages.get(phone_number, {}).get('sensitive', default_messages['sensitive_message'])
    
    msg = bot.send_message(
        call.message.chat.id,
        f"Текущее чувствительное сообщение для сессии {phone_number}:\n{current_text}\n\nВведите новое сообщение:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_session_message_update, phone_number, 'sensitive', call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_sess_first_reply_'))
def edit_session_first_reply_callback(call):
    phone_number = call.data.split('_')[3]
    current_text = session_messages.get(phone_number, {}).get('first_reply', default_messages['first_reply'])
    
    msg = bot.send_message(
        call.message.chat.id,
        f"Текущий первый ответ для сессии {phone_number}:\n{current_text}\n\nВведите новый текст:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_session_message_update, phone_number, 'first_reply', call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_sess_second_reply_'))
def edit_session_second_reply_callback(call):
    phone_number = call.data.split('_')[3]
    current_text = session_messages.get(phone_number, {}).get('second_reply', default_messages['second_reply'])
    
    msg = bot.send_message(
        call.message.chat.id,
        f"Текущий второй ответ для сессии {phone_number}:\n{current_text}\n\nВведите новый текст:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_session_message_update, phone_number, 'second_reply', call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_sess_follow_up_'))
def edit_session_follow_up_callback(call):
    phone_number = call.data.split('_')[3]
    current_text = session_messages.get(phone_number, {}).get('follow_up', default_messages['follow_up_question'])
    
    msg = bot.send_message(
        call.message.chat.id,
        f"Текущий контрольный вопрос для сессии {phone_number}:\n{current_text}\n\nВведите новый текст:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_session_message_update, phone_number, 'follow_up', call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_sess_positive_'))
def edit_session_positive_callback(call):
    phone_number = call.data.split('_')[3]
    current_text = session_messages.get(phone_number, {}).get('positive', default_messages['positive_response'])
    
    msg = bot.send_message(
        call.message.chat.id,
        f"Текущий ответ на положительный ответ для сессии {phone_number}:\n{current_text}\n\nВведите новый текст:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_session_message_update, phone_number, 'positive', call.message.message_id)

@bot.callback_query_handler(func=lambda call: call.data.startswith('edit_sess_negative_'))
def edit_session_negative_callback(call):
    phone_number = call.data.split('_')[3]
    current_text = session_messages.get(phone_number, {}).get('negative', default_messages['negative_response'])
    
    msg = bot.send_message(
        call.message.chat.id,
        f"Текущий ответ на отрицательный ответ для сессии {phone_number}:\n{current_text}\n\nВведите новый текст:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_session_message_update, phone_number, 'negative', call.message.message_id)

def process_session_message_update(message, phone_number, message_type, original_message_id):
    new_text = message.text
    
    if phone_number not in session_messages:
        session_messages[phone_number] = {}
    
    session_messages[phone_number][message_type] = new_text
    save_session_messages()
    
    try:
        bot.delete_message(message.chat.id, message.message_id)
        bot.delete_message(message.chat.id, original_message_id)
    except:
        pass
    
    bot.send_message(
        message.chat.id,
        f"✅ {message_type} сообщение для сессии {phone_number} обновлено!",
        reply_markup=create_panel_keyboard()
    )

def ask_for_new_text(message, text_key):
    current_text = messages_config.get(text_key, "")
    msg = bot.send_message(
        message.chat.id,
        f"Текущий текст ({text_key}):\n{current_text}\n\nВведите новый текст:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_new_text, text_key, message.message_id)

def process_new_text(message, text_key, original_message_id):
    global messages_config
    
    new_text = message.text
    messages_config[text_key] = new_text
    save_messages(messages_config)
    
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    
    bot.send_message(
        message.chat.id,
        f"✅ Текст '{text_key}' успешно обновлен!",
        reply_markup=create_panel_keyboard()
    )

def ask_for_new_keywords(message, keyword_type):
    current_keywords = positive_keywords if keyword_type == 'positive' else negative_keywords
    msg = bot.send_message(
        message.chat.id,
        f"Текущие {keyword_type} ключевые слова:\n{', '.join(current_keywords)}\n\n"
        f"Введите новые {keyword_type} ключевые слова через запятую:",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_new_keywords, keyword_type, message.message_id)

def process_new_keywords(message, keyword_type, original_message_id):
    global positive_keywords, negative_keywords
    
    new_keywords = [kw.strip().lower() for kw in message.text.split(',') if kw.strip()]
    
    if keyword_type == 'positive':
        positive_keywords = new_keywords
    else:
        negative_keywords = new_keywords
    
    with open(os.path.join(messages_dir, f'{keyword_type}_keywords.txt'), 'w') as f:
        f.write(','.join(new_keywords))
    
    try:
        bot.delete_message(message.chat.id, message.message_id)
    except:
        pass
    
    bot.send_message(
        message.chat.id,
        f"✅ {keyword_type.capitalize()} ключевые слова успешно обновлены!",
        reply_markup=create_panel_keyboard()
    )

def ask_for_chat_id(message, action):
    msg = bot.send_message(
        message.chat.id,
        "Введите ID чата (число, начинается с -100 для групп/каналов):",
        reply_markup=telebot.types.ForceReply()
    )
    bot.register_next_step_handler(msg, process_chat_id, action, message.message_id)

def process_chat_id(message, action, original_message_id):
    try:
        chat_id = int(message.text.strip())
        
        if action == 'add':
            if chat_id not in sensitive_chats:
                sensitive_chats.append(chat_id)
                save_sensitive_chats()
                bot.send_message(
                    message.chat.id,
                    f"✅ Чат {chat_id} добавлен в чувствительные!",
                    reply_markup=create_panel_keyboard()
                )
            else:
                bot.send_message(
                    message.chat.id,
                    f"⚠️ Чат {chat_id} уже в списке чувствительных!",
                    reply_markup=create_panel_keyboard()
                )
        elif action == 'remove':
            if chat_id in sensitive_chats:
                sensitive_chats.remove(chat_id)
                save_sensitive_chats()
                bot.send_message(
                    message.chat.id,
                    f"✅ Чат {chat_id} удален из чувствительных!",
                    reply_markup=create_panel_keyboard()
                )
            else:
                bot.send_message(
                    message.chat.id,
                    f"⚠️ Чат {chat_id} не найден в списке чувствительных!",
                    reply_markup=create_panel_keyboard()
                )
    except ValueError:
        bot.send_message(
            message.chat.id,
            "❌ Неверный формат ID чата! Должно быть число (например -100123456789).",
            reply_markup=create_panel_keyboard()
        )
    except Exception as e:
        bot.send_message(
            message.chat.id,
            f"❌ Ошибка: {str(e)}",
            reply_markup=create_panel_keyboard()
        )

def list_sensitive_chats(chat_id):
    if not sensitive_chats:
        bot.send_message(
            chat_id,
            "Список чувствительных чатов пуст.",
            reply_markup=create_panel_keyboard()
        )
        return
    
    text = "📋 Список чувствительных чатов:\n\n" + "\n".join(str(chat_id) for chat_id in sensitive_chats)
    bot.send_message(
        chat_id,
        text,
        reply_markup=create_panel_keyboard()
    )

def toggle_test_mode(call):
    cfg = load_config()
    cfg['check_test'] = not cfg['check_test']
    save_config(cfg)
    show_settings(call.message)

def ask_for_new_value(message, setting_key, prompt_text):
    msg = bot.send_message(message.chat.id, prompt_text)
    bot.register_next_step_handler(msg, process_new_value, setting_key, message.message_id)

def process_new_value(message, setting_key, original_message_id):
    cfg = load_config()
    
    try:
        if setting_key == 'period':
            new_value = int(message.text)
            if 1 <= new_value <= 6:
                cfg['period'] = new_value
            else:
                raise ValueError
        else:
            cfg[setting_key] = message.text
        
        save_config(cfg)
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except:
            pass
        show_settings(bot.send_message(message.chat.id, "✅ Настройки обновлены!"))
    except ValueError:
        bot.send_message(message.chat.id, "❌ Неверное значение! Попробуйте снова.")
        show_settings(bot.send_message(message.chat.id, "Попробуйте еще раз:"))
flag_start = False
# Модифицируем функцию start_bot для учета интервала
def start_bot(chat_id):
    global bot_threads, test_mode, account_delay, time_to_stop, flag_start, users_nahui
    
    active_threads = [t for t in bot_threads if t.is_alive()]
    if active_threads:
        bot.send_message(chat_id, f"⚠️ Бот уже работает! Сначала остановите его.")
        return
    
    session_files = [f for f in os.listdir(sessions_dir) 
                   if f.endswith('.session') and not f.endswith('.session-journal')]
    
    if not session_files:
        bot.send_message(chat_id, "❌ Нет сессионных файлов! Добавьте сессию через /add_session")
        return
    
    cfg = load_config()
    test_mode = cfg['check_test']
    
    # Сброс состояния перед запуском
    bot_threads = []
    users_nahui = []
    time_to_stop = 1
    flag_start = False

    for i, session_file in enumerate(session_files):
        thread = threading.Thread(
            target=run_bot_in_thread,
            args=(session_file, cfg['period']),
            name=session_file.replace('.session', ''),
            daemon=True
        )
        bot_threads.append(thread)
        thread.start()
        
        if i < len(session_files) - 1:
            time.sleep(account_delay)
    
    bot.send_message(
        chat_id, 
        f"✅ Бот успешно запущен для {len(session_files)} сессий с интервалом {account_delay//60} минут!"
    )


def stop_bot(chat_id):
    global bot_threads, active_clients, time_to_stop, flag_start
    # Устанавливаем флаги остановки для всех активных сессий
    for session_file, flag in list(stop_flags.items()):
        flag.set()
    # Сбрасываем time_to_stop до минимума чтобы цикл ожидания прервался
    time_to_stop = 0
    # Разрешаем повторный запуск
    flag_start = True
    # Ждём завершения всех потоков (не более 10 сек каждый)
    for t in bot_threads:
        t.join(timeout=10)
    bot_threads.clear()
    active_clients.clear()
    bot.send_message(chat_id, "🛑 Все сессии бота остановлены!")

@bot.message_handler(commands=['edit_texts'])
def edit_texts_command(message):
    if message.from_user.id not in admins:
        return
    show_edit_texts_menu(message)

@bot.message_handler(commands=['edit_keywords'])
def edit_keywords_command(message):
    if message.from_user.id not in admins:
        return
    show_edit_keywords_menu(message)

@bot.message_handler(commands=['sensitive_chats'])
def sensitive_chats_command(message):
    if message.from_user.id not in admins:
        return
    show_sensitive_chats_menu(message)

@bot.message_handler(commands=['edit_session_messages'])
def edit_session_messages_command(message):
    if message.from_user.id not in admins:
        return
    edit_session_messages_callback(message)

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in admins:
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        file_ext = message.document.file_name.split('.')[-1].lower()
        
        if file_ext == 'txt':
            file_path = os.path.join(proxies_dir, message.document.file_name)
            with open(file_path, 'wb') as new_file:
                new_file.write(bot.download_file(file_info.file_path))
            bot.reply_to(message, f"✅ Файл прокси {message.document.file_name} добавлен!")
        else:
            bot.reply_to(message, "❌ Неподдерживаемый формат файла. Отправьте .txt файл с прокси")
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при обработке файла: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    try:
        if call.from_user.id not in admins:
            bot.answer_callback_query(call.id, "⛔ Доступ запрещен")
            return
        
        if call.data == 'settings':
            show_settings(call.message)
        elif call.data == 'start_bot':
            start_bot(call.message.chat.id)
        elif call.data == 'stop_bot':
            stop_bot(call.message.chat.id)
        elif call.data == 'toggle_test_mode':
            toggle_test_mode(call)
        elif call.data == 'change_period':
            ask_for_new_value(call.message, 'period', "Введите новый период (в часах, от 1 до 6):")
        elif call.data == 'change_test_id':
            ask_for_new_value(call.message, 'id_test', "Введите ID тестового чата:")
        elif call.data == 'back_to_panel':
            bot.edit_message_text(
                chat_id=call.message.chat.id,
                message_id=call.message.message_id,
                text="📊 Панель управления ботом",
                reply_markup=create_panel_keyboard()
            )
        elif call.data == 'edit_texts':
            show_edit_texts_menu(call.message)
        elif call.data == 'edit_keywords':
            show_edit_keywords_menu(call.message)
        elif call.data == 'sensitive_chats':
            show_sensitive_chats_menu(call.message)
        elif call.data == 'edit_session_messages':
            edit_session_messages_callback(call)
        elif call.data.startswith('edit_text_'):
            if len(call.data.split('_')) == 4:
                text_key = call.data.split('_')[2]+"_" + call.data.split('_')[3]
            elif len(call.data.split('_')) == 5:
                text_key = call.data.split('_')[2]+"_" + call.data.split('_')[3] + "_" + call.data.split('_')[4]
            ask_for_new_text(call.message, text_key)
        elif call.data == 'back_to_texts':
            show_edit_texts_menu(call.message)
        elif call.data == 'edit_positive_keywords':
            ask_for_new_keywords(call.message, 'positive')
        elif call.data == 'edit_negative_keywords':
            ask_for_new_keywords(call.message, 'negative')
        elif call.data == 'add_session':
            add_session_callback(call)
        elif call.data == 'delete_session':
            delete_session_callback(call)
        elif call.data == 'add_sensitive_chat':
            ask_for_chat_id(call.message, 'add')
        elif call.data == 'remove_sensitive_chat':
            ask_for_chat_id(call.message, 'remove')
        elif call.data == 'list_sensitive_chats':
            list_sensitive_chats(call.message.chat.id)
        elif call.data.startswith('edit_sess_normal_'):
            edit_session_normal_callback(call)
        elif call.data.startswith('edit_sess_sensitive_'):
            edit_session_sensitive_callback(call)
        elif call.data.startswith('edit_sess_first_reply_'):
            edit_session_first_reply_callback(call)
        elif call.data.startswith('edit_sess_second_reply_'):
            edit_session_second_reply_callback(call)
        elif call.data.startswith('edit_sess_follow_up_'):
            edit_session_follow_up_callback(call)
        elif call.data.startswith('edit_sess_positive_'):
            edit_session_positive_callback(call)
        elif call.data.startswith('edit_sess_negative_'):
            edit_session_negative_callback(call)
        elif call.data.startswith('edit_session_'):
            edit_specific_session_callback(call)
        
        bot.answer_callback_query(call.id)
    except Exception as e:
        print(f"Error in callback: {e}")
        try:
            bot.answer_callback_query(call.id, "⚠️ Произошла ошибка")
        except:
            pass
if __name__ == '__main__':
    # Загружаем сообщения для сессий
    load_session_messages()
    
    # Проверяем, что сообщения загружены правильно
    for session, messages in session_messages.items():
        print(f"Сообщения для сессии {session}:")
        for key, value in messages.items():
            print(f"{key}: {value[:50]}...")  # Выводим первые 50 символов каждого сообщения
    
    # Остальной код запуска бота...
    try:
        if os.path.exists(os.path.join(messages_dir, 'positive_keywords.txt')):
            with open(os.path.join(messages_dir, 'positive_keywords.txt')) as f:
                positive_keywords = [kw.strip().lower() for kw in f.read().split(',') if kw.strip()]
    except Exception as e:
        print(f"Ошибка при загрузке положительных ключевых слов: {e}")
    
    try:
        if os.path.exists(os.path.join(messages_dir, 'negative_keywords.txt')):
            with open(os.path.join(messages_dir, 'negative_keywords.txt')) as f:
                negative_keywords = [kw.strip().lower() for kw in f.read().split(',') if kw.strip()]
    except Exception as e:
        print(f"Ошибка при загрузке отрицательных ключевых слов: {e}")
    
    print("Бот запущен...")
    bot.infinity_polling()