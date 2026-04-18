########################################################## TG-bot by Vology #############################################################################
# Привет, мой дорогой друг. Если ты читаешь этот комментарий, то скорее всего ты работаешь над ботом, который писал я.
# Уверен, во время работы над ним у тебя появятся вопросы... Много вопросов. 
# Если тебе потребуется помощь, пиши сюда TG @onevology
# Удачи! <3


import telebot # type: ignore
from telebot.apihelper import ApiTelegramException # type: ignore
import os

#########################################     Настройки     ###########################################
id_channel = "-1001656251836"  # айди канала
url_channel = "https://t.me/fckprogam"  # ссылка на канал
url_trainer = "https://t.me/onevology"  # ссылка на тренера


UrlSpina1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео спина1
UrlSpina2 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео спина2
UrlSpina3 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео спина3
UrlSpina4 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео спина4

UrlGrud1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео грудь1
UrlGrud2 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео грудь2
UrlGrud3 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео грудь3
UrlGrud4 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео грудь4

UrlNogi1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео ноги1
UrlNogi2 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео ноги2
UrlNogi3 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео ноги3
UrlNogi4 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео ноги4

UrlRuki1 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео руки1
UrlRuki2 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео руки2
UrlRuki3 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео руки3
UrlRuki4 = "https://www.youtube.com/watch?v=dQw4w9WgXcQ" # Видео руки4


bot = telebot.TeleBot(' ')
#########################################     Основной Код     ###########################################

def is_subscribed(user_id):
    try:
        
        a = bot.get_chat_member(id_channel, user_id)
        if a.status == "left":
            return False
        else:
            return True
    except:
        return False

@bot.message_handler(commands=['start'])
def starting(message):
    print("Start")
    keyboard = telebot.types.InlineKeyboardMarkup()
    check_sub = telebot.types.InlineKeyboardButton(text="Проверить подписку", callback_data='check_sub')
    url_button = telebot.types.InlineKeyboardButton(text="Подписаться", url=url_channel)
    keyboard.add(check_sub, url_button)
    subsc = is_subscribed(message.from_user.id)
    if not subsc:
        bot.send_message(message.from_user.id, f'Приветствую, *{message.from_user.first_name}*!\nДля продолжения стоит подписаться на наш канал', parse_mode="Markdown", reply_markup=keyboard)
    else:
        keyboard = telebot.types.InlineKeyboardMarkup()
        go_kach = telebot.types.InlineKeyboardButton(text="Давай!", callback_data='menu')
        keyboard.add(go_kach)
        bot.send_message(message.from_user.id, f'Приветствую, *{message.from_user.first_name}*\nВижу ты уже подписан на наш [канал]({url_channel}). Начнем?', parse_mode="Markdown", reply_markup=keyboard)
    


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
            bot.send_message(call.from_user.id, f'Нет подписки, попробуй еще раз', parse_mode="Markdown", reply_markup=keyboard)
            
        else:
            keyboard = telebot.types.InlineKeyboardMarkup()
            go_kach = telebot.types.InlineKeyboardButton(text="Продолжить", callback_data='menu')
            keyboard.add(go_kach)
            bot.send_message(call.from_user.id, f'*Подписка подтверждена* ✔️', parse_mode="Markdown", reply_markup=keyboard)
            
                
    if call.data == 'menu':
        print("menu") 
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        spina = telebot.types.InlineKeyboardButton(text="Спина", callback_data='spina') # 0
        grud = telebot.types.InlineKeyboardButton(text="Грудь", callback_data='grud') # 0
        nogi = telebot.types.InlineKeyboardButton(text="Ноги", callback_data='nogi') # 0
        ruki = telebot.types.InlineKeyboardButton(text="Руки", callback_data='ruki') # 0
        trainer = telebot.types.InlineKeyboardButton(text="Тренер", url=url_trainer)
        keyboard.add(spina, grud, nogi, ruki, trainer)
        bot.send_message(call.from_user.id, f'*Меню*\nВыбери нужную *категорию*', parse_mode="Markdown", reply_markup=keyboard)


    #########       КАТЕГОРИИ       #########

    #######       Спина       #######
    if call.data == "spina":
        print("спина")
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        SpinaPodt = telebot.types.InlineKeyboardButton(text="1", callback_data='Spina1')
        SpinaTyagaVNaklone = telebot.types.InlineKeyboardButton(text="2", callback_data='Spina2')
        SpinaExtensy = telebot.types.InlineKeyboardButton(text="3", callback_data='Spina3')
        SpinaExtensy1 = telebot.types.InlineKeyboardButton(text="4", callback_data='Spina4')
        BackToMenu = telebot.types.InlineKeyboardButton(text="Меню", callback_data='menu')
        keyboard.add(SpinaPodt, SpinaTyagaVNaklone, SpinaExtensy, SpinaExtensy1, BackToMenu)
        files = os.listdir(r"./photos/spina")
        photo = open(r"./photos/spina/"+files[4], 'rb')
        bot.send_photo(call.from_user.id, photo, caption=f'Выбери интересующую тебя *категорию*', parse_mode="Markdown", reply_markup=keyboard)
    if call.data == "Spina1":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='spina')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Spina2":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='spina')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Spina3":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='spina')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Spina4":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='spina')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    #######       /Спина       #######

    #######       Грудь       #######
    if call.data == "grud":
        print("грудь")
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        GrudZhim = telebot.types.InlineKeyboardButton(text="1", callback_data='Grud1')
        GrudZhim1 = telebot.types.InlineKeyboardButton(text="2", callback_data='Grud2')
        GrudZhim2 = telebot.types.InlineKeyboardButton(text="3", callback_data='Grud3')
        GrudZhim3 = telebot.types.InlineKeyboardButton(text="4", callback_data='Grud4')
        BackToMenu = telebot.types.InlineKeyboardButton(text="Меню", callback_data='menu')
        keyboard.add(GrudZhim, GrudZhim1, GrudZhim2, GrudZhim3, BackToMenu)
        files = os.listdir(r"./photos/grud")
        photo = open(r"./photos/grud/"+files[4], 'rb')
        bot.send_photo(call.from_user.id, photo, caption=f'Выбери интересующую тебя *категорию*', parse_mode="Markdown", reply_markup=keyboard)
    if call.data == "Grud1":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='grud')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Grud2":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='grud')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Grud3":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='grud')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Grud4":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='grud')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    #######       /Грудь       #######

    #######       Ножки :3       #######
    if call.data == "nogi":
        print("ножки")
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        NogiPrised = telebot.types.InlineKeyboardButton(text="1", callback_data='Nogi1')
        NogiExtensy = telebot.types.InlineKeyboardButton(text="2", callback_data='Nogi2')
        NogiBalgarVipad1 = telebot.types.InlineKeyboardButton(text="3", callback_data='Nogi3')
        NogiBalgarVipad = telebot.types.InlineKeyboardButton(text="4", callback_data='Nogi4')
        BackToMenu = telebot.types.InlineKeyboardButton(text="Меню", callback_data='menu')
        keyboard.add(NogiPrised, NogiExtensy, NogiBalgarVipad1, NogiBalgarVipad, BackToMenu)
        files = os.listdir(r"./photos/nogi")
        photo = open(r"./photos/nogi/"+files[4], 'rb')
        bot.send_photo(call.from_user.id, photo, caption=f'Выбери интересующую тебя *категорию*', parse_mode="Markdown", reply_markup=keyboard)
    if call.data == "Nogi1":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='nogi')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Nogi2":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='nogi')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Nogi3":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='nogi')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Nogi4":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='nogi')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    #######       /Ножки :3        #######

    #######       Руки       #######
    if call.data == "ruki":
        print("руки")
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup()
        RukiRazgib = telebot.types.InlineKeyboardButton(text="1", callback_data='Ruki1')
        RukiMahiGan = telebot.types.InlineKeyboardButton(text="2", callback_data='Ruki2')
        RukiMahiGan1 = telebot.types.InlineKeyboardButton(text="3", callback_data='Ruki3')
        RukiMahiGan2 = telebot.types.InlineKeyboardButton(text="4", callback_data='Ruki4')
        BackToMenu = telebot.types.InlineKeyboardButton(text="Меню", callback_data='menu')
        keyboard.add(RukiRazgib, RukiMahiGan, RukiMahiGan1, RukiMahiGan2, BackToMenu)
        files = os.listdir(r"./photos/ruki")
        photo = open(r"./photos/ruki/"+files[4], 'rb')
        bot.send_photo(call.from_user.id, photo, caption=f'Выбери интересующую тебя *категорию*', parse_mode="Markdown", reply_markup=keyboard)
    if call.data == "Ruki1":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='ruki')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Ruki2":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='ruki')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Ruki3":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='ruki')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    if call.data == "Ruki4":
        bot.delete_message(call.from_user.id, call.message.id)
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        Back = telebot.types.InlineKeyboardButton(text="Назад", callback_data='ruki')
        keyboard.add(Back)
        msg = bot.send_message(call.from_user.id, f'Загружаем информацию...', parse_mode="Markdown")
        send_information(call, msg)
    #######       /Руки       #######

    #########       /КАТЕГОРИИ       #########

def send_information(call, msg):
    print("Отправка информации")
    #print(msg)
    bot.delete_message(msg.chat.id, msg.message_id)
    keyboard = telebot.types.InlineKeyboardMarkup()
    BackToMenu = telebot.types.InlineKeyboardButton(text="Меню", callback_data='menu')

    if call.data == "Spina1":
        files = os.listdir(r"./photos/spina/1")
        photo = open(r"./photos/spina/1/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlSpina1)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?',  reply_markup=keyboard)
    if call.data == "Spina2":
        files = os.listdir(r"./photos/spina/2")
        photo = open(r"./photos/spina/2/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlSpina2)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Spina3":
        files = os.listdir(r"./photos/spina/3")
        photo = open(r"./photos/spina/3/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlSpina3)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Spina4":
        files = os.listdir(r"./photos/spina/4")
        photo = open(r"./photos/spina/4/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlSpina4)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)



    if call.data == "Grud1":
        files = os.listdir(r"./photos/grud/1")
        photo = open(r"./photos/grud/1/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlGrud1)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Grud2":
        files = os.listdir(r"./photos/grud/2")
        photo = open(r"./photos/grud/2/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlGrud2)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Grud3":
        files = os.listdir(r"./photos/grud/3")
        photo = open(r"./photos/grud/3/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlGrud3)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Grud4":
        files = os.listdir(r"./photos/grud/4")
        photo = open(r"./photos/grud/4/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlGrud4)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)



    if call.data == "Nogi1":
        files = os.listdir(r"./photos/nogi/1")
        photo = open(r"./photos/nogi/1/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlNogi1)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Nogi2":
        files = os.listdir(r"./photos/nogi/2")
        photo = open(r"./photos/nogi/2/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlNogi2)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Nogi3":
        files = os.listdir(r"./photos/nogi/3")
        photo = open(r"./photos/nogi/3/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlNogi3)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Nogi4":
        files = os.listdir(r"./photos/nogi/4")
        photo = open(r"./photos/nogi/4/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlNogi4)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)



    if call.data == "Ruki1":
        files = os.listdir(r"./photos/nogi/1")
        photo = open(r"./photos/ruki/1/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlRuki1)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Ruki2":
        files = os.listdir(r"./photos/nogi/2")
        photo = open(r"./photos/ruki/2/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlRuki2)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Ruki3":
        files = os.listdir(r"./photos/nogi/3")
        photo= open(r"./photos/ruki/3/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlRuki3)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)
    if call.data == "Ruki4":
        files = os.listdir(r"./photos/nogi/4")
        photo= open(r"./photos/ruki/4/"+files[0], 'rb')
        video = telebot.types.InlineKeyboardButton(text="Видео", url=UrlRuki4)
        keyboard.add(video, BackToMenu)
        bot.send_photo(call.from_user.id, photo, caption=f'Хотите глянуть видео?', reply_markup=keyboard)

    
        






'''
Спина:

    Подтягивания

    Тяга в наклоне

    Экстензия

Грудь:

    Жим лежа 

Ноги: 

    Приседания со штангой

    Экстензия 

    Болгарские выпады 

Руки:

    Разгибания на трицепс

    Махи гантелями
is_subscribed(message.from_user.id)
'''
bot.infinity_polling(timeout=10, long_polling_timeout = 5)
bot.polling(none_stop=True, interval=0)