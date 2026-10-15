import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
########################################################## TG-bot by Vology #############################################################################
# Привет, мой дорогой друг. Если ты читаешь этот комментарий, то скорее всего ты работаешь над ботом, которого писал я.
# Уверен, во время работы над ним у тебя появятся вопросы... Много вопросов. 
# Если тебе потребуется помощь, пиши сюда TG: @onevology
# Удачи! <3

# Уважаемый заказчик, просьба не удалять данный комментарий. Он может ускорить процесс апдейта/починки программы
# Спасибо

# eng

# Hello, my dear friend. If you're reading this comment, then you're probably working on the bot I wrote.
# I'm sure you'll have some questions while working on it... A lot of questions. 
# If you need help, write here TG: @onevology
# Good luck! <3

# Dear customer, please do not delete this comment. It can speed up the process of updating/fixing the program.
# Thank you
import telebot
from telebot import types
from PIL import Image, GifImagePlugin
import json
import parsing
import watermark

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
admins = [int(x) for x in os.getenv('ADMIN_IDS', '').split(',') if x.strip()]
channels = []
with open("channels.json", "r") as r:
    json_param = json.load(r)
    channels = json_param["channels"]
print(f"Загруженно личных каналов: {len(channels)}")
print(f"Админы: {admins}")


@bot.message_handler(commands=['panel'])
def get_admin_panel(message):
    try:
        bot.delete_message(message.from_user.id, message.id)
    except:
        "похуй значит"
    if message.from_user.id in admins:
        print(f"Была вызвана админ-панель юзером {message.from_user.first_name} - {message.from_user.id}")
        keyboard = telebot.types.InlineKeyboardMarkup()
        ras = telebot.types.InlineKeyboardButton(text="Каналы", callback_data='channels')
        buysell = telebot.types.InlineKeyboardButton(text="Парсинг с отправкой", callback_data='parse')
        smentoken = telebot.types.InlineKeyboardButton(text="Связь", callback_data='svyz')
        keyboard.add(ras, buysell, smentoken)
        bot.send_message(message.from_user.id, 'Йоу fucking админ, добро пожаловать в свою стихию, здесь обычные люди становятся твоими рабами. Выбери, что ты хочешь сделать здесь 🍑', reply_markup=keyboard)
    else:
        bot.send_message(message.from_user.id, 'У тебя нет доступа к этой команде, иди нахуй отсюда')

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    bot.delete_message(call.from_user.id, call.message.id)
    if call.data == "svyz":
        bot.send_message(call.from_user.id, '@onevology')
        call.id = call.message.id
        get_admin_panel(call)
    elif call.data == "channels":
        keyboard = telebot.types.InlineKeyboardMarkup()
        for i in [x[1] for x in channels]:
            keyboard.add(telebot.types.InlineKeyboardButton(text=i, callback_data=i))
        keyboard.add(telebot.types.InlineKeyboardButton(text="Добавить ➕", callback_data="add"))
        keyboard.add(telebot.types.InlineKeyboardButton(text="Назад", callback_data="back")) 
        bot.send_message(call.from_user.id, 'Нажмите чтобы удалить или выберите действие', reply_markup=keyboard)
    elif call.data == "back":
        get_admin_panel(call)
    elif call.data == "add":
        msg = bot.send_message(call.from_user.id, 'Напишите id канала \nУзнать его можно здесь (просто перешлите сообщение из канала) @my_id_bot')
        bot.register_next_step_handler(msg, add_to_id)
    elif call.data == "parse":
        msg = bot.send_message(call.from_user.id, 'Отправьте ссылку на YM')
        bot.register_next_step_handler(msg, parse)
    elif call.data in [x[1] for x in channels]:
        for x in range(len(channels)):
            if channels[x][1] == call.data:
                channels.remove(channels[x])
        spis = {}
        spis["channels"] = channels
        with open('channels.json', 'w') as json_file:
            json.dump(spis, json_file)
        bot.send_message(call.from_user.id, f'Канал {call.data} успешно удален')
        get_admin_panel(call)
def parse(message):
    list_YM = parsing.parse_YM(message.text)
    try:
        title = list_YM["title"]
        price = list_YM["price"]
        img = list_YM["img"]
    except:
        bot.send_message(message.from_user.id, "Что-то пошло не так, попробуйте снова")
        bot.send_message(message.from_user.id, list_YM)
        get_admin_panel(message)
        return
    print(title, " - ", price)
    msg = bot.send_photo(message.from_user.id, img, f"{title} - {price}₽\n\nНапишите цену")
    bot.register_next_step_handler(msg, price1, title, img, message.text)
def price1(message, title, img, url):
    price = message.text
    msg = bot.send_message(message.from_user.id, f"Напишите текст в сообщении")
    bot.register_next_step_handler(msg, dop_text, title, img, url, price)
def dop_text(message, title, img, url, price):
    
    for i in channels:
        text = f'<a href="{url}">{title}</a> - {price}₽\n\n{message.text}\n\n<a href="{i[2]}">{i[1]}</a>' #, parse_mode='HTML'
        bot.send_photo(i[0], watermark.water_mark(img), text, parse_mode='HTML')
    bot.send_message(message.from_user.id, f"Сообщения отправлены")
    message.id = 376429083647920
    get_admin_panel(message)
def add_to_id(message):
    #print(f"Новый канал: {message.text}")
    channel = []
    try:
        channel.append(int(message.text))
    except:
        bot.send_message(message.from_user.id, "Это не id")
        get_admin_panel(message)
        return
    msg = bot.send_message(message.from_user.id, "Напишите название канала")
    bot.register_next_step_handler(msg, add_to_name, channel)
def add_to_name(message, channel):
    msg = bot.send_message(message.from_user.id, "Скиньте ссылку на канал")
    channel.append(message.text)
    bot.register_next_step_handler(msg, add_to_url, channel)
def add_to_url(message, channel):
    spis = {}
    channel.append(message.text)
    spis["channels"] = channels
    spis["channels"].append(channel)
    with open('channels.json', 'w') as json_file:
        json.dump(spis, json_file)
    bot.send_message(message.from_user.id, 'Канал добавлен')
    get_admin_panel(message)
def main_func():
    #try:
    bot.polling(none_stop=True)
    #except Exception as e:
        #print(f"проблема с bot.polling()\n: {e}")
        #main_func()
main_func()