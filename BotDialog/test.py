from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.functions.channels import JoinChannelRequest
import os
import json
import asyncio
import random
PROXY_FILE = "proxy.txt"
SESSIONS_DIR = "testacc"

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
    print(sessions)
    return sessions

sessions = load_sessions()

# Назначение прокси сессиям
for i, session in enumerate(sessions):
    if proxies:
        session["proxy"] = proxies[i % len(proxies)]

async def send_telegram_message(session_info):
    print(f"Попытка поключения {session_info['phone']}")
    try:
        client = TelegramClient(
            session_info["session_file"],
            int(session_info["api_id"]),
            session_info["api_hash"],
            proxy=session_info["proxy"]
        )
    except Exception as e:
        print(f"Ошибка в {session_info["session_file"]} - {e}")
        return
    
    await client.connect()
    if not await client.is_user_authorized():
        print(f"Сессия {session_info['phone']} не авторизована")
        #return False
    try:
        me = await client.get_me()
        print(me.username)
    except:
        ""
    try:
        neme1 = await client.get_entity("https://t.me/tr_sis")
    except:
        print(f"{session_info['phone']} заморожена")
        return
    try:
        msg_id = await client.send_message(neme1, "Hello, you")
        print("Отправлено")
    except Exception as e:
        print(e)
    
    await asyncio.sleep(random.randint(10, 15))
    
    #result = await client(JoinChannelRequest("@wildberries_business"))
    #print(await client.get_participants("@wildberries_business"))
for session in sessions:
    message = asyncio.run(send_telegram_message(session))