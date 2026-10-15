import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass

import requests
import base64
from time import sleep

API_KEY = os.getenv('RUCAPTCHA_KEY', '')
def solve_captcha_api(image_path):
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    # Шаг 1: Отправка на rucaptcha
    post_data = {
        "key": API_KEY,
        "method": "base64",
        "body": img_base64,
        "json": 1,
        "regsense": 1 
    }
    
    res = requests.post("https://rucaptcha.com/in.php", data=post_data).json()
    if res.get("status") != 1:
        return None

    captcha_id = res.get("request")
    
    # Шаг 2: Опрос готовности
    while True:
        sleep(5)
        print("проверяем")
        response = requests.get(
            f"https://rucaptcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1"
        ).json()

        if response.get("status") == 1:
            return response.get("request")
        if response.get("request") == "CAPCHA_NOT_READY":
            continue
        break
    return None


resh = solve_captcha_api("test.jpeg")
print(resh)