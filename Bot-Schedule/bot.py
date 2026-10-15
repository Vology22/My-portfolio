import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
import telebot
from telebot import types # для указание типов
from datetime import date, datetime, date

id_group = -1002700757578
shablon = "*Расписание на завтра епта*\nжирным выделены лекции\n\n"
monday = "_9:50_ - _11:25_ *CS103. Алг и Геом - Ерусалимский Я.М 120 аудитория*\n_9:50_ - _14:30_ ИнЯз 308, 307, 306, 305, 208 аудитории"

tuesdayVERH = "*ВЕРХНЯЯ НЕДЕЛЯ*\n_11:55_ - _13:30_ *CS102. Дискр. Математика Ерусалимский Я.М. - 120 аудитория*\n_13:45_ - _15:20_ CS103. Алг и Геом - Чернявская И.А. 304 аудитория\n\n*ОНЛАЙН*\nОсн Раб с Данн для ИИ с _19:00_ - Доц Е.А."
tuesdayNIZH = "*НИЖНЯЯ НЕДЕЛЯ*\n_9:50_ - _11:25_ *CS103. Алг и Геом  Ерусалимский Я.М - 120 аудитория*.\n_11:55_ - _13:30_ *CS102. Дискр. Математика - Ерусалимский Я.М. 120 аудитория*\n_13:45_ - _15:20_ CS103. Алг и Геом - Чернявская И.А. - 304 аудитория\n\n*ОНЛАЙН*\nОсн Раб с Данн для ИИ с _19:00_ - Доц Е.А."

wednesday = "_8:00_ - _9:35_ Осн Раб с Данн для ИИ Доц Е.А.- 301 аудитория\n_9:50_ - _11:25_ CS102. Дискр Математика  Крутенко Е. - 212 аудитория\n\nбез лекций"

thursday = "_8:00_ - _9:35_ CS101. Основы Программирования Шабас И.Н. и Андреева Е.М. - 101 и 102 аудитории\n_9:50_ - _11:25_ Техн-и и Фронт Наук о... - ХЗ пока\n_11:55_ - _13:30_ Осн Раб с Данн для ИИ - 301 аудитория"

fridayVERH = "*ВЕРХНЯЯ НЕДЕЛЯ*\n_9:50_ - _11:25_ *CS101. Основы Программирования Михалкович С.С. - 120 аудитория*\n_11:55_ - _15:20_ CS104. Непр Матем Абрамян А.В. - 207 аудитория"
fridayNIZH = "*НИЖНЯЯ НЕДЕЛЯ*\n_8:00_ - _9:35_ *CS101. Основы Программирования Михалкович С.С. - 120 аудитория*\n_9:50_ - _11:25_ *CS101. Основы Программирования Михалкович С.С. - 120 аудитория*\n_11:55_ - _13:30_ CS104. Непр Матем Абрамян А.В. - 207 аудитория"

saturday = "_9:50_ - _11:25_ CS101. Основы Пр Шабас И.Н. и Андреева Е.М. - 118 аудитория\n_11:55_ - _13:30_ *CS104. Непр Матем Абрамян А.В. - 120 аудитория*\n\n*ОНЛАЙН*\nТехн-и и Фронт Наук о Данн в 16:00"

bot = telebot.TeleBot(os.getenv('BOT_TOKEN'))
'''

bot.send_message(id_group, shablon+monday, parse_mode="Markdown")
bot.send_message(id_group, shablon+tuesdayNIZH, parse_mode="Markdown")
bot.send_message(id_group, shablon+tuesdayVERH, parse_mode="Markdown")
bot.send_message(id_group, shablon+wednesday, parse_mode="Markdown")
bot.send_message(id_group, shablon+thursday, parse_mode="Markdown")
bot.send_message(id_group, shablon+fridayNIZH, parse_mode="Markdown")
bot.send_message(id_group, shablon+fridayVERH, parse_mode="Markdown")
bot.send_message(id_group, shablon+saturday, parse_mode="Markdown")



'''
#d = date(2025, 5, 8)
def is_even_week(target_date=None):
    start_date = date(2025, 9, 1)
    if target_date is None:
        target_date = date.today()
    delta_days = (target_date - start_date).days
    week_number = delta_days // 7 + 1
    return week_number % 2 == 0

vid_ned = not is_even_week()

today = date.today()
today1 = today.weekday()

today_week = today1
if today1 == 0:
    if vid_ned:
        bot.send_message(id_group, shablon+tuesdayVERH, parse_mode="Markdown")
    else:
        bot.send_message(id_group, shablon+tuesdayNIZH, parse_mode="Markdown")
elif today1 == 1:
    bot.send_message(id_group, shablon+wednesday, parse_mode="Markdown")
elif today1 == 2:
    bot.send_message(id_group, shablon+thursday, parse_mode="Markdown")
elif today1 == 3:
    if vid_ned:
        bot.send_message(id_group, shablon+fridayVERH, parse_mode="Markdown")
    else:
        bot.send_message(id_group, shablon+fridayNIZH, parse_mode="Markdown")
elif today1 == 4:
    bot.send_message(id_group, shablon+saturday, parse_mode="Markdown")
elif today1 == 5:
    bot.send_message(id_group, "*Завтра выходные*\nбухаем", parse_mode="Markdown")
elif today1 == 6:
    bot.send_message(id_group, shablon+monday, parse_mode="Markdown")
    

#bot.polling(none_stop=True, interval=0)