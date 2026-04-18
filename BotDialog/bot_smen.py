import os
import json
import time
from datetime import datetime
import threading
import telebot
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
import zipfile
import random
import patoolib
import aspose.zip as az
from telethon.tl.functions.account import UpdateProfileRequest
from telethon.tl.functions.account import UpdateUsernameRequest  
from telethon.tl.functions.photos import UploadProfilePhotoRequest
import asyncio
TOKEN = "8121977923:AAGolO6kLq4l4zsOQyrW-0IaQ4xXewZu7UQ"
ADMIN_IDS = [6054849445, 5747767617, 968218637]  # ID администраторов
PROXY_FILE = "proxy_smen.txt"
SESSIONS_DIR = ".\\sessions_smen"
PICTURE_DIR = ".\\pict"
zip_file_path = "\\ziprar"
bot = telebot.TeleBot(TOKEN)

with open(PROXY_FILE, "r") as f:
    proxy = [x.split(":") for x in f.readlines()]

for i in range(len(proxy)):
    star = []
    for x in proxy[i]:
        star.append(x.replace("\n", ""))
    proxy[i] = star
print("Прокси загружено: " + str(proxy))

@bot.message_handler(content_types=['document'])
def handle_document(message):
    if message.from_user.id not in ADMIN_IDS:
        return
    msg = bot.send_message(message.chat.id, "*Начинаю обработку\\.\\.\\.*", parse_mode="MarkdownV2")
    file_info = bot.get_file(message.document.file_id)
    file_extension = message.document.file_name.split('.')[-1].lower()
    if file_extension not in ['json', "rar", "zip"]:
        bot.send_message(message.chat.id, "Неподдерживаемый формат файла. Используйте JSON, RAR или ZIP.")
        return
    
    if file_extension == 'json':
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="*Обнаружен json\\-сценарий\\.\\.\\.*", parse_mode="MarkdownV2")
        temp_file = f"temp.json"
        downloaded_file = bot.download_file(file_info.file_path)
        with open(temp_file, 'wb') as f:
            f.write(downloaded_file)
        with open(temp_file, 'r', encoding='utf-8') as f:
            content = f.read()
            if content.strip():
                data = json.loads(content)
                for acc in data:
                    print("\n### аккаунт ###")
                    print(acc["login"])
                    print(acc["picture"])
                    print(acc["new_username"])
                    print(acc["First_Name"] + " " + acc["Second_Name"])
                    asyncio.run(tg_smen(acc["login"], acc["picture"], acc["new_username"], acc["First_Name"], acc["Second_Name"]))
                    time.sleep(15)
            else:
                bot.reply_to(message, "❌ Файл пустой.")
    
    elif file_extension == 'rar':  #acc
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="*Обнаружен rar\\-архив\\.\\.\\.*", parse_mode="MarkdownV2")
        name_randomed = "." + zip_file_path+f"\\{random.randint(10000, 99999)}.rar"
        downloaded_file = bot.download_file(file_info.file_path)
        with open(name_randomed, 'wb') as new_file:
            new_file.write(downloaded_file)
        with az.rar.RarArchive(name_randomed) as archive:
            archive.extract_to_directory(SESSIONS_DIR)
        kolvo = len([name for name in os.listdir(SESSIONS_DIR)])//2
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"*Успешная разархивация rar\\-архива*\nОбщее количество загруженных аккаунтов\\: *{kolvo} шт\\.*", parse_mode="MarkdownV2")
    
    
    elif file_extension == 'zip': # pict
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text="*Обнаружен zip\\-архив\\.\\.\\.*", parse_mode="MarkdownV2")
        name_randomed = "." + zip_file_path+f"\\{random.randint(10000, 99999)}.zip"
        downloaded_file = bot.download_file(file_info.file_path)
        with open(name_randomed, 'wb') as new_file:
            new_file.write(downloaded_file)
        with zipfile.ZipFile(name_randomed, 'r') as zip_ref: 
            zip_ref.extractall(PICTURE_DIR)
        kolvo = len([name for name in os.listdir(PICTURE_DIR)])
        #if kolvo == 0: kolvo = 1
        bot.edit_message_text(chat_id=message.chat.id, message_id=msg.message_id, text=f"*Успешная разархивация zip\\-архива*\nОбщее количество загруженных изображений\\: *{kolvo} шт\\.*", parse_mode="MarkdownV2")

async def tg_smen(login, picture, username, fname, sname):
    global proxy
    json_file = SESSIONS_DIR + "\\" + login + ".json"
    with open(json_file, "r") as f:
            session_data = json.load(f)
    rand_proxy = random.randint(0, len(proxy)-1)
    proxy12 = {
                            "proxy_type": "socks5",
                            "addr": proxy[rand_proxy][0],
                            "port": int(proxy[rand_proxy][1]),
                            "username": proxy[rand_proxy][2],
                            "password": proxy[rand_proxy][3],
                            "rdns": True
                        }
    if session_data.get("api_id", "") == "" or session_data.get("api_id", "") == None:
        ses = {
                            "session_file": SESSIONS_DIR + "\\" + login,
                            "phone": session_data.get("phone", ""),
                            "api_id": session_data.get("app_id", ""),
                            "api_hash": session_data.get("app_hash", ""),
                            "proxy": proxy12
                        }
    else:
        ses = {
                            "session_file": SESSIONS_DIR + "\\" + login,
                            "phone": session_data.get("phone", ""),
                            "api_id": session_data.get("api_id", ""),
                            "api_hash": session_data.get("api_hash", ""),
                            "proxy": proxy12
                        }
    client = TelegramClient(
        ses["session_file"],
        int(ses["api_id"]),
        ses["api_hash"],
        proxy=ses["proxy"]
    )

    
    await client.connect()
    if not await client.is_user_authorized():
        print(f"Сессия {ses['phone']} не авторизована")
        return False
    await client(UpdateProfileRequest(
            first_name=fname,
            last_name=sname
        ))
    print("Имя и Фамилия успешно изменены")
    try:
        await client(UpdateUsernameRequest(username)) 
        print("username успешно изменен")
    except:
        print("username занят")
    print(PICTURE_DIR+"\\"+picture)
    
    with open(PICTURE_DIR+"\\"+picture, 'rb') as file:
        file1 = await client.upload_file(file)
        await client(UploadProfilePhotoRequest(file=file1))
        print("Аватарка успешно изменена")
    
    




@bot.message_handler(commands=['list'])
def list_acc(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message.chat.id, "У вас нет доступа")
        return
    msg = "Вот список полученных аккаунтов\\:* \n"
    for name in os.listdir(SESSIONS_DIR):
        file_ras = name.split('.')[-1].lower()
        if file_ras == "json":
            continue
        msg += name.replace(".session", "") + "\n"
    msg += "*"
    bot.send_message(message.chat.id, msg, parse_mode="MarkdownV2")
@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message.chat.id, "У вас нет доступа")
        return
    



@bot.message_handler(commands=['help'])
def helppls(message):
    bot.send_message(message.chat.id, "/start - Приветствие\n/help - помощь по командам\n/json - формат заполнения json-файлов\n/remove - удаление базы аккаунтов\n/list - получить список загруженных аккаунтов\n\nЧтобы начать работать, отправьте мне .zip (изображения) или .rar (аккаунты) архивы с аккаунтами, а после json-файл со сценарием обработки (подробнее: /json)")
@bot.message_handler(commands=["remove"])
def delete_basee(message):
    if message.from_user.id not in ADMIN_IDS:
        bot.reply_to(message.chat.id, "У вас нет доступа")
        return
    chet = 0
    for name in os.listdir(SESSIONS_DIR):
        os.remove(os.path.join(SESSIONS_DIR, name))
        chet += 1
    bot.send_message(message.chat.id, f"Удалено {chet} файлов")
@bot.message_handler(commands=['json'])
def helppls(message):
    bot.send_message(message.chat.id, 'Вот пример единиченого заполнения')
    bot.send_message(message.chat.id, '[\n {\n  "login":"12345",\n  "picture":"logo.png",\n  "new_username":"@username",\n  "First_Name":"Ivan",\n  "Second_Name":"Popov"\n }\n]\n')
    bot.send_message(message.chat.id, 'А это пример заполнения нескольких аккаунтов')
    bot.send_message(message.chat.id, '[\n {\n  "login":"6789",\n  "picture":"logo2.png",\n  "new_username":"@username2",\n  "First_Name":"Nikita",\n  "Second_Name":"Pizdelov"\n },\n {\n  "login":"12345",\n  "picture":"logo.png",\n  "new_username":"@username",\n  "First_Name":"Ivan",\n  "Second_Name":"Popov"\n }\n]\n')

bot.infinity_polling()