import os
import json
import time
from datetime import datetime
import threading
import telebot
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
import asyncio

# Конфигурация
TOKEN = "7702716200:AAG2bzrveHbu9peU8xc-Tpac6i-sV225jtE"
ADMIN_IDS = [6054849445, 5747767617, 968218637]  # ID администраторов
PROXY_FILE = "proxy.txt"
SESSIONS_DIR = "sessions"
MAX_CHATS = 5  # Максимальное количество чатов
id_chat_logger = -1002889244873
client_log = TelegramClient("16172013854", 2040, "b18441a1ff607e10a989891a5462e627")
#async def gksj():
    #await client_log.connect()
    #await client_log(JoinChannelRequest("https://t.me/shhsshdc"))

# Инициализация бота
bot = telebot.TeleBot(TOKEN)

# Загрузка прокси
def load_proxies():
    proxies = []
    if os.path.exists(PROXY_FILE):
        with open(PROXY_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if line:
                    parts = line.split(":")
                    if len(parts) == 4:
                        proxy = {
                            "proxy_type": "socks5",
                            "addr": parts[0],
                            "port": int(parts[1]),
                            "username": parts[2],
                            "password": parts[3],
                            "rdns": True
                        }
                        proxies.append(proxy)
    return proxies

proxies = load_proxies()
proxy_index = 0

# Загрузка сессий
def load_sessions():
    sessions = []
    for filename in os.listdir(SESSIONS_DIR):
        if filename.endswith(".session"):
            session_file = os.path.join(SESSIONS_DIR, filename)
            json_file = os.path.join(SESSIONS_DIR, filename.replace(".session", ".json"))
            if os.path.exists(json_file):
                with open(json_file, "r") as f:
                    session_data = json.load(f)
                if session_data.get("api_id", "") == "" or session_data.get("api_id", "") == None:
                    sessions.append({
                        "session_file": session_file,
                        "phone": session_data.get("phone", ""),
                        "api_id": session_data.get("app_id", ""),
                        "api_hash": session_data.get("app_hash", ""),
                        "proxy": None  # Будет назначено позже
                    })
                else:
                    sessions.append({
                        "session_file": session_file,
                        "phone": session_data.get("phone", ""),
                        "api_id": session_data.get("api_id", ""),
                        "api_hash": session_data.get("api_hash", ""),
                        "proxy": None  # Будет назначено позже
                    })
    return sessions

sessions = load_sessions()

# Назначение прокси сессиям
for i, session in enumerate(sessions):
    if proxies:
        session["proxy"] = proxies[i % len(proxies)]

# Структура для хранения данных чатов
chats = {}
for i in range(1, MAX_CHATS + 1):
    chat_id = f"chat_{i}"
    schedule_file = f"schedule_{i}.json"
    chats[chat_id] = {
        "id": i,
        "name": f"Чат {i}",
        "active": False,
        "schedule_file": schedule_file,
        "messages": [],
        "sent_messages": {},
        "last_message_time": None,
        "waiting_for_schedule": False  # Флаг ожидания файла расписания
    }

# Очередь сообщений
message_queue = []
schedule_running = False

# Функция для проверки соответствия даты
def is_correct_date(msg_date):
    if not msg_date:
        return True  # Если дата не указана, считаем что подходит
    
    try:
        msg_date = datetime.strptime(msg_date, "%d.%m.%Y").date()
        current_date = datetime.now().date()
        return msg_date == current_date
    except ValueError:
        return False  # Некорректный формат даты

# Функция для отправки сообщения через Telethon
async def send_telegram_message(session_info, chat_id, text, reply_to=None):
    print(f"Попытка отправки от {session_info['phone']} в чат {chat_id}")
    try:
        client = TelegramClient(
            session_info["session_file"],
            int(session_info["api_id"]),
            session_info["api_hash"],
            proxy=session_info["proxy"]
        )
    except Exception as e:
        asyncio.run(error_log_tg(f"Ошибка инициализации клиента: {e}"))
    
    try:
        await client.connect()
        if not await client.is_user_authorized():
            print(f"Сессия {session_info['phone']} не авторизована")
            return False
        
        try:

            # Пытаемся получить entity чата
            try:
                await client(JoinChannelRequest("https://t.me/wildberries_talk"))
            except Exception as e:
                print(e)
            try:
                await client(JoinChannelRequest("https://t.me/wb_supply"))
            except Exception as e:
                print(e)
            try:
                await client(JoinChannelRequest("https://t.me/wildberries_contact"))
            except Exception as e:
                print(e)
            try:
                await client(JoinChannelRequest("https://t.me/wildberries_business"))
            except Exception as e:
                print(e)
            try:
                await client(JoinChannelRequest("https://t.me/wildberries_experience"))
            except Exception as e:
                print(e)
            try:
                entity = await client.get_input_entity(chat_id)
            except ValueError:
                print(f"Чат {chat_id} не найден. Пробуем получить через get_entity...")
                entity = await client.get_entity(chat_id)
            
            # Проверяем, является ли пользователь участником чата
            try:
                await client.get_permissions(entity)
            except (ValueError, TypeError) as e:
                print(f"Сессия {session_info['phone']} не в чате {chat_id}. Пытаемся присоединиться...")
                if hasattr(entity, 'username'):
                    await client(JoinChannelRequest(entity))
                print(f"Сессия {session_info['phone']} успешно присоединилась к чату")
            
            # Если указан reply_to, получаем сообщение для ответа
            reply_to_msg = None
            if reply_to is not None:
                try:
                    reply_to_msg = await client.get_messages(entity, ids=reply_to)
                except Exception as e:
                    print(f"Не удалось найти сообщение для ответа: {e}")
                    asyncio.run(error_log_tg(f"Ошибка ответа. Сообщение будет отправлено, но не как ответ юзеру: {e}"))
            
            # Отправляем сообщение
            try:
                 msg_id = await client.send_message(entity, text, reply_to=reply_to_msg)
            except Exception as e:
                    asyncio.run(error_log_tg(e))
            msg_id = msg_id.id
            
            print(f"✅ Сообщение отправлено от {session_info['phone']}")
            return msg_id
            
        except Exception as e:
            print(f"❌ Ошибка при отправке от {session_info['phone']}: {type(e).__name__}: {str(e)} chatID: {chat_id}")
            return False
    finally:
        await client.disconnect()
async def error_log_tg(error):
    print("Отправляем ошибку")
    global client_log
    try:
        if not client_log.is_connected():
            await client_log.connect()
        
        # Проверяем, авторизован ли клиент
        if not await client_log.is_user_authorized():
            await client_log.start()  # Если сессия не авторизована, запускаем её
        
        # Пытаемся отправить сообщение
        await client_log.send_message(id_chat_logger, error)
    except Exception as e:
        print(f"❌ Ошибка при отправке лога в Telegram: {e}")
        # Пытаемся переподключиться и отправить снова
        try:
            await client_log.disconnect()
            await client_log.connect()
            await client_log.send_message(id_chat_logger, f"⚠️ Переподключение... Ошибка: {error}")
        except Exception as e2:
            print(f"❌ Критическая ошибка: {e2}")
    finally:
        # Не отключаем клиент, чтобы он оставался активным
        pass

# Функция для обработки расписания
def process_schedule():
    global schedule_running
    #asyncio.run(gksj())
    while schedule_running:
        now = datetime.now().strftime("%H:%M")
        #print(chats)
        for chat_id, chat_data in chats.items():
            if not chat_data["active"]:
                continue
                
            for msg in chat_data["messages"]:
                # Проверяем совпадение времени и даты (если указана)
                if (msg["time"] == now and 
                    not msg.get("sent", False) and 
                    is_correct_date(msg.get("date"))):
                    
                    session = next((s for s in sessions if s["phone"] == msg["login"]), None)
                    
                    if session:
                        # Получаем message_id сообщения для ответа 
                        reply_to = None
                        if msg.get("response_to") is not None:
                            reply_to = chat_data["sent_messages"].get(msg["response_to"])
                            print(f"Пытаемся ответить на сообщение {msg['response_to']} (message_id: {reply_to})")
                        
                        try:
                            
                            # Используем chat_id из сообщения, а не внутренний chat_id бота
                            target_chat_id = msg.get("chat_id")
                            if not target_chat_id:
                                asyncio.run(error_log_tg(f"❌ Не указан chat_id в сообщении {msg.get('message_number', '?')}"))
                                continue
                                
                            message = asyncio.run(
                                send_telegram_message(
                                    session,
                                    target_chat_id,  # Используем chat_id из JSON
                                    msg["text"],
                                    reply_to
                                )
                            )
                            
                            if message:  # Если сообщение отправлено успешно
                                msg["sent"] = True
                                if "message_number" in msg:  # Сохраняем message_id для будущих ответов
                                    chat_data["sent_messages"][msg["message_number"]] = message
                                chat_data["last_message_time"] = datetime.now().strftime("%H:%M:%S")
                                print(f"Сообщение {msg.get('message_number', '?')} отправлено в чат {target_chat_id}")
                        except Exception as e:
                            asyncio.run(error_log_tg(f"Ошибка при отправке: {e}"))
                    else:
                        asyncio.run(error_log_tg(f"Сессия для {msg['login']} не найдена"))
                        msg["sent"] = True
        
        time.sleep(30)


# Функция для загрузки расписания чата
def load_chat_schedule(chat_id):
    chat_data = chats.get(chat_id)
    if not chat_data:
        return False
    
    schedule_file = chat_data["schedule_file"]
    if not os.path.exists(schedule_file):
        return False
    
    try:
        with open(schedule_file, "r", encoding="utf-8") as f:
            content = f.read()
            if content.strip():
                data = json.loads(content)
                chat_data["messages"] = data if isinstance(data, list) else [data]
                return True
    except Exception as e:
        print(f"Ошибка загрузки расписания для {chat_id}: {str(e)}")
    
    return False

# Функция для сохранения расписания чата
def save_chat_schedule(chat_id, messages):
    chat_data = chats.get(chat_id)
    if not chat_data:
        return False
    
    schedule_file = chat_data["schedule_file"]
    try:
        with open(schedule_file, "w", encoding="utf-8") as f:
            json.dump(messages, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Ошибка сохранения расписания для {chat_id}: {str(e)}")
        return False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этому боту.")
        return
    
    help_text = """
👋 Привет! Это бот для управления отправкой сообщений в чаты.

Доступные команды:
/status - статус всех чатов
/chat_status N - статус конкретного чата (1-5)
/start_chat N - запустить чат
/stop_chat N - остановить чат
/update_schedule - обновить расписание для чата
/get_schedule N - получить текущее расписание чата
/start_all - запустить все чаты
/stop_all - остановить все чаты
"""
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['status'])
def send_status(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    status_text = "📊 Статус всех чатов:\n\n"
    for chat_id, chat_data in chats.items():
        status = "🟢" if chat_data["active"] else "🔴"
        last_msg = chat_data["last_message_time"] or "никогда"
        status_text += (
            f"{chat_data['name']} ({chat_data['id']}): {status}\n"
            f"• Сообщений в очереди: {len(chat_data['messages'])}\n"
            f"• Последнее сообщение: {last_msg}\n\n"
        )
    
    status_text += (
        f"Всего сессий: {len(sessions)}\n"
        f"Всего прокси: {len(proxies)}\n"
        f"Расписание: {'🟢 активно' if schedule_running else '🔴 не активно'}"
    )
    
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['chat_status'])
def chat_status(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    try:
        _, chat_num = message.text.split()
        chat_num = int(chat_num)
        if chat_num < 1 or chat_num > MAX_CHATS:
            raise ValueError
    except:
        bot.reply_to(message, f"❌ Укажите номер чата от 1 до {MAX_CHATS}")
        return
    
    chat_id = f"chat_{chat_num}"
    chat_data = chats[chat_id]
    
    status = "🟢 активен" if chat_data["active"] else "🔴 не активен"
    last_msg = chat_data["last_message_time"] or "никогда"
    
    status_text = (
        f"📊 Статус {chat_data['name']}:\n"
        f"• Статус: {status}\n"
        f"• Сообщений в очереди: {len(chat_data['messages'])}\n"
        f"• Последнее сообщение: {last_msg}\n"
        f"• Файл расписания: {chat_data['schedule_file']}"
    )
    
    bot.reply_to(message, status_text)

@bot.message_handler(commands=['start_chat'])
def start_chat(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    try:
        _, chat_num = message.text.split()
        chat_num = int(chat_num)
        if chat_num < 1 or chat_num > MAX_CHATS:
            raise ValueError
    except:
        bot.reply_to(message, f"❌ Укажите номер чата от 1 до {MAX_CHATS}")
        return
    
    chat_id = f"chat_{chat_num}"
    chat_data = chats[chat_id]
    
    if chat_data["active"]:
        bot.reply_to(message, f"ℹ️ {chat_data['name']} уже активен.")
        return
    
    # Загружаем расписание перед запуском
    if load_chat_schedule(chat_id):
        chat_data["active"] = True
        bot.reply_to(message, f"✅ {chat_data['name']} запущен.")
    else:
        bot.reply_to(message, f"❌ Не удалось загрузить расписание для {chat_data['name']}.")

@bot.message_handler(commands=['stop_chat'])
def stop_chat(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    try:
        _, chat_num = message.text.split()
        chat_num = int(chat_num)
        if chat_num < 1 or chat_num > MAX_CHATS:
            raise ValueError
    except:
        bot.reply_to(message, f"❌ Укажите номер чата от 1 до {MAX_CHATS}")
        return
    
    chat_id = f"chat_{chat_num}"
    chat_data = chats[chat_id]
    
    if not chat_data["active"]:
        bot.reply_to(message, f"ℹ️ {chat_data['name']} уже остановлен.")
        return
    
    chat_data["active"] = False
    bot.reply_to(message, f"✅ {chat_data['name']} остановлен.")

@bot.message_handler(commands=['update_schedule'])
def update_schedule_command(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    # Запрашиваем номер чата
    msg = bot.reply_to(message, "📝 Введите номер чата (1-5) для обновления расписания:")
    bot.register_next_step_handler(msg, process_chat_number_for_schedule)

def process_chat_number_for_schedule(message):
    try:
        chat_num = int(message.text)
        if chat_num < 1 or chat_num > MAX_CHATS:
            raise ValueError
        
        chat_id = f"chat_{chat_num}"
        chat_data = chats[chat_id]
        
        # Устанавливаем флаг ожидания файла
        for chat in chats.values():
            chat["waiting_for_schedule"] = False
        chat_data["waiting_for_schedule"] = True
        
        bot.reply_to(message, f"🔄 Теперь отправьте JSON-файл с расписанием для {chat_data['name']}")
    
    except ValueError:
        bot.reply_to(message, f"❌ Некорректный номер чата. Введите число от 1 до {MAX_CHATS}")

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    
    # Проверяем, ожидается ли файл для какого-либо чата
    target_chat = None
    for chat_id, chat_data in chats.items():
        if chat_data["waiting_for_schedule"]:
            target_chat = chat_data
            break
    
    if not target_chat:
        bot.reply_to(message, "❌ Сначала используйте команду /update_schedule")
        return
    
    try:
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Проверяем расширение файла
        file_extension = message.document.file_name.split('.')[-1].lower()
        if file_extension not in ['json', 'txt']:
            bot.reply_to(message, "❌ Неподдерживаемый формат файла. Используйте JSON.")
            return
        
        # Сохраняем временный файл
        temp_file = f"temp_schedule_{target_chat['id']}.json"
        with open(temp_file, 'wb') as f:
            f.write(downloaded_file)
        
        # Парсим файл
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip():
                try:
                    data = json.loads(content)
                    
                    # Проверяем наличие chat_id в каждом сообщении
                    for msg in data if isinstance(data, list) else [data]:
                        if "chat_id" not in msg:
                            bot.reply_to(message, "❌ В сообщениях отсутствует chat_id")
                            return
                    
                    # Сохраняем расписание
                    target_chat["messages"] = data if isinstance(data, list) else [data]
                    save_chat_schedule(f"chat_{target_chat['id']}", target_chat["messages"])
                    
                    bot.reply_to(message, f"✅ Расписание для {target_chat['name']} обновлено. Сообщений: {len(target_chat['messages'])}")
                except json.JSONDecodeError:
                    bot.reply_to(message, "❌ Ошибка парсинга JSON. Проверьте формат файла.")
            else:
                bot.reply_to(message, "❌ Файл пустой.")
        
        # Удаляем временный файл
        os.remove(temp_file)
    
    except Exception as e:
        bot.reply_to(message, f"❌ Ошибка при обработке файла: {str(e)}")
    finally:
        # Сбрасываем флаг ожидания
        target_chat["waiting_for_schedule"] = False
@bot.message_handler(commands=['get_schedule'])
def get_schedule(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    try:
        _, chat_num = message.text.split()
        chat_num = int(chat_num)
        if chat_num < 1 or chat_num > MAX_CHATS:
            raise ValueError
    except:
        bot.reply_to(message, f"❌ Укажите номер чата от 1 до {MAX_CHATS}")
        return
    
    chat_id = f"chat_{chat_num}"
    chat_data = chats[chat_id]
    
    if not chat_data["messages"]:
        bot.reply_to(message, f"❌ В {chat_data['name']} нет сообщений в расписании.")
        return
    
    # Создаем временный файл с расписанием
    temp_file = f"schedule_{chat_num}_export.json"
    with open(temp_file, 'w', encoding='utf-8') as f:
        json.dump(chat_data["messages"], f, ensure_ascii=False, indent=2)
    
    # Отправляем файл пользователю
    with open(temp_file, 'rb') as f:
        bot.send_document(message.chat.id, f, caption=f"📅 Расписание для {chat_data['name']}")
    
    # Удаляем временный файл
    os.remove(temp_file)

@bot.message_handler(commands=['start_all'])
def start_all_chats(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    started = 0
    for chat_id, chat_data in chats.items():
        if not chat_data["active"]:
            if load_chat_schedule(chat_id):
                chat_data["active"] = True
                started += 1
    
    global schedule_running
    if not schedule_running:
        schedule_running = True
        threading.Thread(target=process_schedule, daemon=True).start()
    
    bot.reply_to(message, f"✅ Запущено {started} чатов.")

@bot.message_handler(commands=['stop_all'])
def stop_all_chats(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    for chat_data in chats.values():
        chat_data["active"] = False
    
    bot.reply_to(message, "✅ Все чаты остановлены.")

@bot.message_handler(commands=['start_schedule'])
def start_schedule_command(message):
    global schedule_running
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    if not schedule_running:
        schedule_running = True
        threading.Thread(target=process_schedule, daemon=True).start()
        bot.reply_to(message, "✅ Расписание запущено.")
    else:
        bot.reply_to(message, "ℹ️ Расписание уже запущено.")

@bot.message_handler(commands=['stop_schedule'])
def stop_schedule_command(message):
    global schedule_running
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message, "❌ У вас нет доступа к этой команде.")
        return
    
    if schedule_running:
        schedule_running = False
        bot.reply_to(message, "✅ Расписание остановлено.")
    else:
        bot.reply_to(message, "ℹ️ Расписание уже остановлено.")

@bot.message_handler(commands=['myid'])
def get_my_id(message):
    bot.reply_to(message, f"Ваш ID: {message.from_user.id}")

# Запуск бота
if __name__ == "__main__":
    # Загружаем расписание для всех чатов при старте
    for chat_id in chats:
        load_chat_schedule(chat_id)
    
    # Запускаем обработчик расписания
    schedule_running = True
    threading.Thread(target=process_schedule, daemon=True).start()
    
    print("Бот запущен...")
    bot.infinity_polling()