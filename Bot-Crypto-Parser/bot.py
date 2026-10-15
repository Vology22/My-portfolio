import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
import time
import telebot
from telebot import types
from telebot.types import InputMediaPhoto
import json
import requests
import threading
from PIL import Image, GifImagePlugin
with open("infobot.json", "r") as r:
    json_param = json.load(r)
    channel_id = json_param["id_channel"]
    URL_channel = json_param["url_channel"] 
    admins = json_param["admins"] 
    admin = json_param["admin"] 

def long_running_function():
    # Ваш длительный код здесь
    while True:
        with open("tokensZ.json", "r") as r:
            json_param = json.load(r)
        for i in json_param:
            url = f"https://api.dexscreener.com/latest/dex/search?q={i}"
            response = requests.get(url, headers={})
            data = response.json()
            #print(data['pairs'][0]['priceUsd'])
            json_param[i] = str(data['pairs'][0]['priceUsd'])
            with open('tokensZ.json', 'w') as json_file:
                json.dump(json_param, json_file)
            with open("tokens.json", "r") as r:
                json_param1 = json.load(r)
            for c in json_param1:
                for k in json_param1[c]:
                    #print(k[1])    
                    if k[1] == i and float(k[0]) < float(data['pairs'][0]['priceUsd']):
                        bot.send_message(c, f'The "{i}" token has increased in price! ')
        time.sleep(10)
thread = threading.Thread(target=long_running_function)
thread.start()
bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))  #тест

@bot.message_handler(commands=['start']) # start
def get_start(message):
    markup = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton("Subscribe ✔", url=URL_channel)
    markup.add(button1)
    key_check = types.InlineKeyboardButton(text='Check Subscription ✔', callback_data='check')
    markup.add(key_check)
    bot.send_message(message.from_user.id, "Subscribe to our channel before you start", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    try:
        bot.delete_message(call.from_user.id, call.message.id)
    except:
        "похуй"
    tokens_names = []
    try:
        with open("tokens.json", "r") as r:
                tokens_user = json.load(r)
                
                for i in tokens_user[str(call.from_user.id)]:
                    tokens_names.append(i[1])
        ########## ТОКЕНЫ
        #print(tokens_names)
        if call.data in tokens_names:
            for cc in tokens_user[str(call.from_user.id)]:
                if cc[1] == call.data:
                    with open("tokens.json", "r") as file:
                        data1 = json.load(file)
                    data1[str(call.from_user.id)].remove([cc[0], call.data])
                    bot.send_message(call.from_user.id, f'The {call.data} token has been successfully deleted')
                    with open('tokens.json', 'w') as json_file:
                        json.dump(data1, json_file)
                    call.data = "mm"
                    callback_worker(call)
    except:
        "похуй"
    if call.data == "deletetoken":
        markup = types.InlineKeyboardMarkup()
        if not (str(call.from_user.id) in tokens_user):
            bot.send_message(call.from_user.id, "You don't have any tokens.", reply_markup=markup )
            call.data = "mm"
            callback_worker(call)
            return
        for i in tokens_user[str(call.from_user.id)]:
            markup.add(types.InlineKeyboardButton(text=f"{i[1]} ({i[0]})", callback_data=i[1]))
        markup.add(types.InlineKeyboardButton(text='Back to menu', callback_data='mm'))
        bot.send_message(call.from_user.id, "Click on the token to delete it.", reply_markup=markup )
    if call.data == 'newtoken':
        msg = bot.send_message(call.from_user.id, "Send me a token with [dexscreener](https://dexscreener.com/)", parse_mode='Markdown')
        bot.register_next_step_handler(msg, add_to_url, call.from_user.id)
    ########## АДМИН ПАНЕЛЬ
    if call.data == 'changesupport': # добавление админа
        msg = bot.send_message(call.from_user.id, "Send me a support link.")
        bot.register_next_step_handler(msg, change_admin)
    if call.data == 'addtoadmin': # добавление админа
        msg = bot.send_message(call.from_user.id, "Send the user's ID")
        bot.register_next_step_handler(msg, add_to_admins)
    if call.data == 'changech': # смена канала
        msg = bot.send_message(call.from_user.id, 'Send the id and link to the channel (in the url name format) separated by a space Keep in mind that the bot must be the admin in this channel')
        bot.register_next_step_handler(msg, change_channel)
    if call.data == "adminpanel":
        markup = types.InlineKeyboardMarkup()
        addtoadm = types.InlineKeyboardButton(text='Add to admin', callback_data='addtoadmin')
        change_channels = types.InlineKeyboardButton(text='Change the channel', callback_data='changech')
        changesupport = types.InlineKeyboardButton(text='Change the support', callback_data='changesupport')
        back = types.InlineKeyboardButton(text='Back to menu', callback_data='mm')
        markup.add(addtoadm, change_channels, changesupport, back)
        bot.send_message(call.from_user.id, f'This is the *admin panel*\\.\nSelect a *section*',  parse_mode='MarkdownV2', reply_markup=markup )
    ########## ГЛАВНОЕ МЕНЮ 
    if call.data == "aboutus":
        markup = types.InlineKeyboardMarkup()
        programmer = types.InlineKeyboardButton("Our programmer", url="https://t.me/onevology")
        channel = types.InlineKeyboardButton(text='Our channel', url=URL_channel)
        admin_url = types.InlineKeyboardButton(text='Support', url=admin)
        back = types.InlineKeyboardButton(text='Back to menu', callback_data='mm')
        markup.add(programmer, channel, admin_url, back)
        bot.send_message(call.from_user.id, f'This is the *about us*\\.\nSelect a *section*',  parse_mode='MarkdownV2', reply_markup=markup )
    if call.data == "mm":
        markup = types.InlineKeyboardMarkup()
        newtkn = types.InlineKeyboardButton(text='New Token', callback_data='newtoken')
        deltkn = types.InlineKeyboardButton(text='My Tokens', callback_data='deletetoken')
        abus = types.InlineKeyboardButton(text='About us', callback_data='aboutus')
        markup.add(newtkn, deltkn, abus)
        if str(call.from_user.id) in admins:
            markup.add(types.InlineKeyboardButton(text='admin panel', callback_data='adminpanel'))
        bot.send_message(call.from_user.id, f'This is the *main menu*\\.\nSelect a *section*',  parse_mode='MarkdownV2', reply_markup=markup )
    ########## ПРОВЕРКА ПОДПИСКИ
    if call.data == "check":
        user_in_channel = bot.get_chat_member(channel_id, call.from_user.id)
        #print(user_in_channel)
        if user_in_channel.status in ["member", "administrator", "creator"]:
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton(text="Let's go!", callback_data='mm'))
            bot.send_message(call.from_user.id, f'You are subscribed! Shall we go to the main menu?', reply_markup=markup)
            #ref_check(call)
        else:
            # Пользователь не является участником канала
            markup = types.InlineKeyboardMarkup()
            button1 = types.InlineKeyboardButton("Subscribe ✔", url=URL_channel)
            markup.add(button1)
            key_check = types.InlineKeyboardButton(text='Check Subscription ✔', callback_data='check')
            markup.add(key_check)
            bot.send_message(call.from_user.id, f'*You haven\'t subscribed*\\!',  parse_mode='MarkdownV2', reply_markup=markup)
def add_to_token(msg, id, num, tokenn):
    
    if msg.text == "cancel" or msg.text == "отмена":
        bot.send_message(id, f"Ok.")
        return
    with open("tokensZ.json", "r") as r:
        json_param = json.load(r)
    with open("tokens.json", "r") as r:
        json_param1 = json.load(r)
    if msg.text not in json_param:
        url = f"https://api.dexscreener.com/latest/dex/search?q={tokenn}"
        response = requests.get(url, headers={})
        data = response.json()
        try:
            print(data['pairs'][0]['priceUsd'])
            bot.send_message(id, f"Successfully!\n\nToken: {tokenn}\nURL: https://dexscreener.com/solana/{tokenn}\nPrice USD: {data['pairs'][0]['priceUsd']}")
            json_param[tokenn] = str(data['pairs'][0]['priceUsd'])
            with open('tokensZ.json', 'w') as json_file:
                json.dump(json_param, json_file)
        except:
            msg = bot.send_message(id, "Invalid token. Please try again or write 'cancel'")
            bot.register_next_step_handler(msg, add_to_token, id)
    else:
        bot.send_message(id, f"Successfully!\n\nToken: {tokenn}\nURL: https://dexscreener.com/solana/{tokenn}\nPrice USD: {json_param[tokenn]}")
    if str(id) not in json_param1:
        json_param1[str(id)] = [[num, tokenn]]
        with open('tokens.json', 'w') as json_file:
                json.dump(json_param1, json_file)
    else:
        json_param1[str(id)].append([num, tokenn])
        with open('tokens.json', 'w') as json_file:
                json.dump(json_param1, json_file)
    msg.from_user.id = id
    msg.data = "mm"
    callback_worker(msg)
def add_to_url(msgj, id):
    msg = bot.send_message(id, f"Send the value, after which you should be notified. (example 0.725987)")
    bot.register_next_step_handler(msg, add_to_num, id, msgj.text)  #Send the value, after which you should be notified. (example 0.725987)
def add_to_num(msgj, id, url):
    try:
        float(msgj.text)
    except:
        msg = bot.send_message(id, f"Try again.  (example 0.725987)")
        bot.register_next_step_handler(msg, add_to_num, id)
        return
    msg = bot.send_message(id, f"Провека значений....")
    add_to_token(msg, id, msgj.text, url)


def change_admin(message):
    admin = message.text
    new_json = {
        "id_channel" : channel_id,
        "url_channel" : URL_channel,
        "admins" : admins,
        "admin" : admin
    }
    with open('infobot.json', 'w') as json_file:
        json.dump(new_json, json_file)
    bot.send_message(message.from_user.id, f'Fucking админ был добавлен')
    message.data = "mm"
    callback_worker(message)   
def change_channel(message):
    channel_id = message.text.split(" ")[0]
    URL_channel = message.text.split(" ")[1]
    new_json = {
        "id_channel" : channel_id,
        "url_channel" : URL_channel,
        "admins" : admins,
        "admin" : admin
    }
    with open('infobot.json', 'w') as json_file:
        json.dump(new_json, json_file)
    # .items()
    bot.send_message(message.from_user.id, f'Fucking канал был изменен')
    message.data = "mm"
    callback_worker(message)
def add_to_admins(message):
    admins.append(str(message.text))
    new_json = {
        "id_channel" : channel_id,
        "url_channel" : URL_channel,
        "admins" : admins,
        "admin" : admin
    }
    with open('infobot.json', 'w') as json_file:
        json.dump(new_json, json_file)
    bot.send_message(message.from_user.id, f'Fucking админ был добавлен')
    message.data = "mm"
    callback_worker(message)
def main_func():
    #try:
    bot.polling(none_stop=True)
    #except Exception as e:
        #print(f"проблема с bot.polling()\n: {e}")
        #main_func()
main_func()