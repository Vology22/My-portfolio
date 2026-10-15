import telebot 
import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
import random
import datetime
from threading import Lock
from pickledb import PickleDB
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))

# Блокировка для потокобезопасности
message_lock = Lock()

def is_subscribed(user_id):
    try:
        a = bot.get_chat_member(id_channel, user_id)
        if a.status == "left":
            return False
        else:
            return True
    except:
        return False
db = PickleDB('data.db')
db.save()
id_channel = "-1002809590717"  # айди канала
url_channel = "https://t.me/barahol2234"  # ссылка на канал
url_admin = os.getenv('ADMIN_URL', '')  # ссылка на меня
url_bot = "https://t.me/baraholka_vape_krasnodar_bot"
password = os.getenv('ADMIN_PASSWORD', '')
admins = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]

# Глобальные словари для хранения состояний
user_states = {}
user_data = {}

@bot.message_handler(commands=['start'])
def starting(message):
    if " " in message.text:
        print("hgdhddgh")
        id_message = message.text.split()[1].strip()
        bot.send_message(message.from_user.id, f'*Вы* жалуетесь на пост *{id_message}* пользователя\n\n_Опишите проблему_', parse_mode="Markdown")
        bot.register_next_step_handler(message, report_msg, id_message)
        return
    keyboard = telebot.types.InlineKeyboardMarkup()
    check_sub = telebot.types.InlineKeyboardButton(text="Проверить подписку", callback_data='check_sub')
    url_button = telebot.types.InlineKeyboardButton(text="Подписаться", url=url_channel)
    keyboard.add(check_sub, url_button)
    subsc = is_subscribed(message.from_user.id)
    if not subsc:
        bot.send_message(message.from_user.id, 
                        f'Приветствую, *{message.from_user.first_name}*!\nДля использования бота необходимо *подписаться* на наш канал', 
                        parse_mode="Markdown", reply_markup=keyboard)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        go_kach = telebot.types.InlineKeyboardButton(text="Мне есть 18 лет ✔️", callback_data='menu')
        keyboard.add(go_kach)
        bot.send_message(message.from_user.id, 
                        f'Приветствую, *{message.from_user.first_name}*\nВижу ты уже подписан на наш [канал]({url_channel})', 
                        parse_mode="Markdown")
        bot.send_message(message.from_user.id, 
                        f'Нажимая кнопку ниже, вы подтверждаете, что _вам исполнилось_ *18 лет*', 
                        parse_mode="Markdown", reply_markup=keyboard)
def report_msg(message, id_message):
    bot.send_message(message.from_user.id, f'_Ваша проблема отправлена на рассмотрение_', parse_mode="Markdown")
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    delandban = telebot.types.InlineKeyboardButton(text="Забанить пользователя и удалить объявление", callback_data=f"ban2 {id_message}")
    sorry = telebot.types.InlineKeyboardButton(text="Понять и простить", callback_data=f"skip")
    keyboard.add(delandban, sorry)
    for admin in admins:
        bot.forward_message(admin, id_channel, int(id_message))
        bot.send_message(admin, f'Поступила жалоба от {message.from_user.username}!\n\nВот текст сообщения:\n*{message.text}*\n\nЧто делаем?', reply_markup=keyboard, parse_mode="Markdown")
@bot.callback_query_handler(func=lambda call: call.data.startswith('desc'))  #   https://t.me/<юзернейм_бота>?start=test
def reg(call):
    bot.delete_message(call.from_user.id, call.message.id)
    recommended, desc = call.data.split('12|21')[1].split("://K")
    
    with open(desc.strip(), "r", encoding="utf-8") as f:
        text = f.read()
    img1, user_pr, disc = text.split("glent")
    user_id = int(img1.split("\\")[0])
    if recommended.strip() == "1":
        disc = disc.strip() + "\n\n\n*Рекомендовано администраторами ✔️*"
    disc += "\n\n*Не будьте жертвами мошенников. Не переводите никакие деньги до встречи с продавцом.*"
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    check_sub = telebot.types.InlineKeyboardButton(text="Написать продавцу", url=f"{user_pr.strip()}")
    url_button = telebot.types.InlineKeyboardButton(text="Разместить объявление", url=url_bot)
    #report_button = telebot.types.InlineKeyboardButton(text="Пожаловаться", url=f"{url_bot}?start=test")
    keyboard.add(check_sub, url_button)
    photo = open(img1, 'rb')
    msg = bot.send_photo(id_channel, photo, disc.strip(), reply_markup=keyboard, parse_mode="Markdown")
    report_button = telebot.types.InlineKeyboardButton(text="Пожаловаться", url=f"{url_bot}?start={msg.message_id}")#12||21{user_pr.strip()}")
    
    print(f"{url_bot}?start={msg.message_id}12||21{user_pr.strip()}")
    keyboard.add(report_button)
    db.set(msg.message_id, user_id)
    db.save()
    bot.edit_message_reply_markup(chat_id=id_channel, message_id=msg.message_id, reply_markup=keyboard)
@bot.callback_query_handler(func=lambda call: call.data.startswith('ban2'))
def ban2(call):
    id_message = call.data.split()[1]
    bot.delete_message(id_channel, int(id_message))
    bot.delete_message(call.from_user.id, call.message.id)
    userid = db.get(int(id_message))
    photo = open("ban.jpg", 'rb')
    bot.send_photo(int(userid), photo, "*Администратор* посчитал, что ваше объявление серьезно нарушает правила пользования ботом \n\n*Вы больше не сможете отправлять объявления*", parse_mode="Markdown")
    with open("banlist.txt", "a") as f:
        f.write(f"\n{userid}") 
@bot.callback_query_handler(func=lambda call: call.data.startswith('ban'))
def ban(call):
    bot.delete_message(call.from_user.id, call.message.id)
    userid = call.data.split('12|21')[1]
    photo = open("ban.jpg", 'rb')
    bot.send_photo(int(userid), photo, "*Администратор* посчитал, что ваше объявление серьезно нарушает правила пользования ботом \n\n*Вы больше не сможете отправлять объявления*", parse_mode="Markdown")
    with open("banlist.txt", "a") as f:
        f.write(f"\n{userid}")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    print("Вызвана call-кнопка")
    
    if call.data == 'check_sub': 
        print("проверка подписки")
        bot.delete_message(call.from_user.id, call.message.id)
        if not is_subscribed(call.from_user.id):
            keyboard = telebot.types.InlineKeyboardMarkup()
            check_sub = telebot.types.InlineKeyboardButton(text="Проверить подписку", callback_data='check_sub')
            url_button = telebot.types.InlineKeyboardButton(text="Подписаться", url=url_channel)
            keyboard.add(check_sub, url_button)
            bot.send_message(call.from_user.id, 
                           f'Нет подписки, попробуй еще раз', 
                           parse_mode="Markdown", reply_markup=keyboard)
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            go_kach = telebot.types.InlineKeyboardButton(text="Мне есть 18 лет ✔️", callback_data='menu')
            keyboard.add(go_kach)
            bot.send_message(call.from_user.id, 
                            f'*Подписка подтверждена* ✔️\n\nНажимая кнопку ниже, вы подтверждаете, что _вам исполнилось_ *18 лет*', 
                            parse_mode="Markdown", reply_markup=keyboard)
    elif call.data == "skip":
        bot.send_message(call.from_user.id, 
                           f'*Забыли*', 
                           parse_mode="Markdown")
    elif call.data == 'menu':
        try:
            os.makedirs(str(call.from_user.id), exist_ok=True)
            with open(f"{call.from_user.id}/readme.txt", "w") as f:
                f.write("Пользователь подтвердил свое совершеннолетие. За его покупку или продажу он сам несет ответственность")
        except Exception as e:
            print(f"Error creating user folder: {e}")
        
        keyboard = telebot.types.InlineKeyboardMarkup()
        trainer = telebot.types.InlineKeyboardButton(text="Разработчик", url=url_admin)
        keyboard.add(trainer)
        bot.send_message(call.from_user.id, 
                        f'*По вопросам разработки пишите разработчику (по кнопке)*\n\nПреимущества *бота*:\n* -Проверка каждого поста\n -Проверка картинок на копипаст\n -Обратная связь*', 
                        parse_mode="Markdown", reply_markup=keyboard)
        bot.send_message(call.from_user.id, 
                        f'*Правила* или *почему ваш пост может быть неодобрен*:\n* -Ваш пост не соответствует теме продажи электронных сигарет/подов\n -Ваш пост был зафиксирован как опасный или мошеннический (*_ограничения использования бота навсегда_*)\n -Ранние блокировки\n -Не указан какой-либо из обязательных пунктов*', 
                        parse_mode="Markdown")
        bot.send_message(call.from_user.id, 
                        f'*Для публикации поста просто отправьте фото товара (без текста)*\n\n_Отправка только одного фото._', 
                        parse_mode="Markdown")
@bot.message_handler(commands=[password])
def unbun(message):
    new_banlist = ""
    with open("banlist.txt", "r+") as f:
        banlist = f.readlines()
        for user_banned in banlist:
            try:
                if int(user_banned.replace("\n", "")) == message.from_user.id:
                    bot.send_message(message.from_user.id, "Вы были удачно удалены из бан-листа")
                    continue
            except:
                continue
            print(new_banlist)
            new_banlist += "\n" + str(message.from_user.id)
    with open("banlist.txt", "w") as f:
        f.write(new_banlist)
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    with message_lock:
        user_id = message.from_user.id
        with open("banlist.txt", "r") as f:
            banlist = f.readlines()
        for user_banned in banlist:
            try:
                if user_id == int(user_banned.replace("\n", "")):
                    bot.send_message(user_id, "Сожалеем, но вы забанены администратором <3")
                    return
            except:
                continue
        # Проверяем, не находится ли пользователь уже в процессе создания поста
        if user_states.get(user_id) == 'processing':
            bot.send_message(user_id, "Пожалуйста, завершите текущий процесс публикации перед началом нового.")
            return
            
        user_states[user_id] = 'processing'
        
        try:
            # Создаем папку для пользователя
            user_folder = f"{user_id}"
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)

            # Уникальная папка для этой отправки
            folder_name = f"{datetime.date.today()}-{random.randint(10000, 99999)}"
            full_path = os.path.join(user_folder, folder_name)
            os.makedirs(full_path, exist_ok=True)

            # Сохраняем фото (берем самое качественное - последнее в списке)
            best_photo = message.photo[-1]
            file_info = bot.get_file(best_photo.file_id)
            downloaded_file = bot.download_file(file_info.file_path)
            photo_path = os.path.join(full_path, "photo.jpg")
            
            with open(photo_path, 'wb') as new_file:
                new_file.write(downloaded_file)
                
            # Сохраняем данные пользователя
            user_data[user_id] = {
                'folder_path': full_path,
                'photo_path': photo_path,
                'step': 'price'
            }
            
            bot.send_message(user_id, "✅ Фото сохранено! Укажите желаемую цену.")
            
        except Exception as e:
            print(f"Error processing photo: {e}")
            bot.send_message(user_id, "Произошла ошибка при обработке фото. Пожалуйста, попробуйте еще раз.")
            user_states.pop(user_id, None)
            user_data.pop(user_id, None)

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'processing' and 
                                         user_data.get(message.from_user.id, {}).get('step') == 'price')
def handle_price(message):
    with message_lock:
        user_id = message.from_user.id
        user_data[user_id]['price'] = message.text
        user_data[user_id]['step'] = 'condition'
        
        bot.send_message(user_id, "Укажите состояние по шкале от 1 до 10 (например 8)")

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'processing' and 
                                         user_data.get(message.from_user.id, {}).get('step') == 'condition')
def handle_condition(message):
    with message_lock:
        user_id = message.from_user.id
        
        try:
            condition = int(message.text)
            if condition < 1 or condition > 10:
                raise ValueError
                
            user_data[user_id]['condition'] = condition
            user_data[user_id]['step'] = 'description'
            
            bot.send_message(user_id, "Напишите описание (от 20 символов)")
            
        except ValueError:
            bot.send_message(user_id, "Пожалуйста, укажите число от 1 до 10")
            return

@bot.message_handler(func=lambda message: user_states.get(message.from_user.id) == 'processing' and 
                                         user_data.get(message.from_user.id, {}).get('step') == 'description')
def handle_description(message):
    with message_lock:
        user_id = message.from_user.id
        
        if len(message.text) < 20:
            bot.send_message(user_id, "Описание должно содержать не менее 20 символов. Пожалуйста, попробуйте еще раз.")
            return
            
        user_data[user_id]['description'] = message.text
        username = f"@{message.from_user.username}" if message.from_user.username else str(user_id)
        
        # Формируем текст поста
        post_text = f"Цена: {user_data[user_id]['price']}\n\nСостояние: {user_data[user_id]['condition']}\n\nОписание: {user_data[user_id]['description']}"
        
        # Сохраняем данные в файл
        with open(f"{user_data[user_id]['folder_path']}/post.txt", "w", encoding="utf-8") as f:
            f.write(f"{user_data[user_id]['photo_path']} glent https://t.me/{message.from_user.username} glent {post_text}")
        
        # Отправляем подтверждение пользователю
        bot.send_message(user_id, "Пост отправлен на проверку ✔️\n\nДля создания нового объявления просто отправьте новое фото", parse_mode="Markdown")
        
        # Отправляем пост админам на проверку
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        check_sub = telebot.types.InlineKeyboardButton(text="Написать продавцу", 
                                                      url=f"https://t.me/{message.from_user.username}")
        url_button = telebot.types.InlineKeyboardButton(text="Разместить объявление", url=url_bot)
        send = telebot.types.InlineKeyboardButton(text="Отправить в канал", callback_data=f"desc 12|21 0://K{user_data[user_id]['folder_path']}/post.txt")
        sendrec = telebot.types.InlineKeyboardButton(text="Отправить в канал и рекомендовать", callback_data=f"desc 12|21 1://K{user_data[user_id]['folder_path']}/post.txt")
        banuser = telebot.types.InlineKeyboardButton(text="Забанить пользователя", callback_data=f"ban 12|21 {user_id}")
        keyboard.add(send, sendrec, banuser)
        
        try:
            with open(user_data[user_id]['photo_path'], 'rb') as photo:
                for admin in admins:
                    bot.send_photo(admin, photo, post_text, reply_markup=keyboard)
        except Exception as e:
            print(f"Error sending photo to admin: {e}")
        
        # Очищаем состояние пользователя
        user_states.pop(user_id, None)
        user_data.pop(user_id, None)

if __name__ == '__main__':
    print("Бот запущен")
    bot.infinity_polling(timeout=10, long_polling_timeout=5)