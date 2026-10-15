import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
from bs4 import BeautifulSoup as bs
import requests
from time import sleep
import time
from fake_useragent import UserAgent
import random
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pickle
import pandas as pd
import sys
import base64
from bs4 import BeautifulSoup as bs, Comment
import re
from alive_progress.styles import BARS, SPINNERS
from alive_progress import alive_bar
#import os
ua = UserAgent()
#print("Загрузка. Пожалуйста, подождите...")
'''
while True:
    try:
        service = Service(ChromeDriverManager().install())
        print("\n"*100)
        break
    except Exception as e:
        print(e)
        continue
'''
#driver_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'driver', 'chromedriver.exe')
#service = Service(executable_path='/')
service = Service(ChromeDriverManager().install())
def joker(st):

    for i in range(len(list(st))):
        sleep(float(f"0.{random.randint(1, 3)}"))
        print(st[i], end="")
    print("\n")

def update_str(text):
    sys.stdout.write(f"\r{text}"+" "*40)
    sys.stdout.flush()
"""
Немного авторства никогда не мешало этому миру ~@onevology
"""
test_project = True
API_KEY = os.getenv('RUCAPTCHA_KEY', '')

headers = {
    'Accept-Encoding': 'gzip, deflate, sdch',
    'Accept-Language': 'en-US,en;q=0.8',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': ua.edge,
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Cache-Control': 'max-age=0',
    'Connection': 'keep-alive',
}
kapcha = 0
error_num = 0
error_req = 0
num_str = 0
def solve_captcha_api(image_path):
    global kapcha
    global error_req
    global error_num
    with open(image_path, "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode('utf-8')

    # Шаг 1: Отправка на rucaptcha
    post_data = {
        "key": API_KEY,
        "method": "base64",
        "body": img_base64,
        "json": 1,
        "regsense": 1,     # Учитывать регистр
        "lang": "ru"
    }
    
    res = requests.post("https://rucaptcha.com/in.php", data=post_data).json()
    if res.get("status") != 1:
        return None

    captcha_id = res.get("request")
    
    # Шаг 2: Опрос готовности
    while True:
        try:
            # Добавляем timeout=10 секунд, чтобы не ждать вечно
            url = f"https://rucaptcha.com/res.php?key={API_KEY}&action=get&id={captcha_id}&json=1"
            response = requests.get(url, timeout=10).json()

            if response.get("status") == 1:
                kapcha+=1
                return response.get("request")
            
            if response.get("request") == "CAPCHA_NOT_READY":
                sleep(5)
                continue
            break
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ReadTimeout):
            print("Сервер RuCaptcha не отвечает, пробую еще раз через 5 сек...")
            sleep(5)
            continue
        except Exception as e:
            print(f"Непредвиденная ошибка сети: {e}")
            error_req+=1
            break
    return None
def ParsingUrls(pages):   
    global kapcha
    global error_req
    global error_num
    print("Начинаем парсинг страниц", end="\r")
    urls_base = []
    print("Начинаем парсинг данных с каждой страницы. Подгрузка драйвера...", end="\r")
    options = webdriver.ChromeOptions()
    if not test_project:
        options.add_argument("--headless")
    options.add_argument("--force-device-scale-factor=1") # Игнорировать системное масштабирование Windows
    options.add_argument("--high-dpi-support=1")
    options.add_argument("--window-size=1920,1080")
    #options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(service=service, options=options)
    update_str("Драйвер подгружен. Начинаем парсинг....")
    with alive_bar(pages, 
            title='Парсинг страниц',
            bar='filling',      # Название стиля из списка BARS
            spinner='wait4'    # Название стиля из списка SPINNERS
            ) as bar:
        for num in range(pages):
            while True:
                try:
                    driver.get(f'https://rostov.hh.ru/search/vacancy?text=&excluded_text=&salary=&salary=&currency_code=RUR&experience=doesNotMatter&order_by=relevance&search_period=0&items_on_page=100&L_save_area=true&page={num}&search_session_id=65ca42d7-7aac-4bf1-beb1-e3ca1053e2fe')
                    bar()
                    break
                except:
                    error_req += 1
                    continue
            page = driver.page_source
            soup = bs(page, "html.parser")
            obv = soup.find_all("div", class_="magritte-redesign") #<a class="magritte-link___b4rEM_7-1-14 magritte-link_mode_primary___l6una_7-1-14 magritte-link_style_neutral___iqoW0_7-1-14 magritte-link_enable-visited___Biyib_7-1-14" data-qa="serp-item__title" tabindex="0" href="https://rostov.hh.ru/vacancy/132227513?hhtmFrom=vacancy_search_list" target="_blank"><span class="magritte-icon-dynamic___KJ4yJ_14-2-0 magritte-icon-dynamic_hover-enabled___WblhN_14-2-0 magritte-icon-dynamic_press-enabled___aGKHB_14-2-0"><span class="magritte-text___pbpft_5-0-1 magritte-text_style-primary___AQ7MW_5-0-1 magritte-text_typography-title-4-semibold___vUqki_5-0-1"><span data-qa="serp-item__title-text" class="magritte-text___tkzIl_7-1-14">Оператор call-центра<span class="premium-container--YNTLa4hq3bga7xCT"><svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" focusable="false" class="magritte-icon___rRr4Q_14-2-0 magritte-icon_initial-negative___jrGEi_14-2-0" aria-hidden="true"><g><path fill-rule="evenodd" clip-rule="evenodd" d="M8 .667C2.5.667.667 4.333.667 8S2.5 15.333 8 15.333 15.333 11.667 15.333 8 13.5.667 8 .667M7.46 3.59l-.365-.223-.177.389c-.348.76-.837 1.268-1.344 1.796q-.09.092-.179.186c-.564.592-1.124 1.242-1.318 2.275-.508 2.711 1.579 4.618 3.883 4.618 1.858 0 3.212-.99 3.766-2.335.553-1.342.29-2.988-.972-4.25l-.343-.343-.25.415c-.11.174-.254.33-.405.47-.17.156-.39.318-.658.44.03-.23.045-.51.02-.816-.068-.846-.45-1.883-1.658-2.622" fill="currentColor"></path></g></svg></span></span></span></span></a>
            for one_obv in obv:  # <button class="magritte-button___Pubhr_7-2-1 magritte-button_mode-secondary___xYz4-_7-2-1 magritte-button_size-medium___WvUsb_7-2-1 magritte-button_style-accent___TE21J_7-2-1" type="button" data-qa="vacancy-serp__vacancy_contacts"><div class="magritte-icon-dynamic___KJ4yJ_14-2-0 magritte-icon-dynamic_full-width___vgWH5_14-2-0 magritte-icon-dynamic_hover-enabled___WblhN_14-2-0 magritte-icon-dynamic_press-enabled___aGKHB_14-2-0"><span class="magritte-button-view___53Slm_7-2-1"><span class="magritte-button__content___BXYU0_7-2-1"><span class="magritte-button__label___zplmt_7-2-1">Связаться</span></span></span></div></button>
                if one_obv.find_all("button", class_="magritte-button___Pubhr_7-2-1 magritte-button_mode-secondary___xYz4-_7-2-1 magritte-button_size-medium___WvUsb_7-2-1 magritte-button_style-accent___TE21J_7-2-1") == []:
                    continue
                #<a class="magritte-link___b4rEM_7-1-15 magritte-link_mode_primary___l6una_7-1-15 magritte-link_style_neutral___iqoW0_7-1-15 magritte-link_enable-visited___Biyib_7-1-15" data-qa="serp-item__title" tabindex="0" href="https://adsrv.hh.ru/click?b=2033257&amp;place=35&amp;meta=VDIZrRlgo6itImU0s4zgCQ08fSFJBAie8qXxd8NlHjeRT-N5ojtpakLERslx-jHG437_WRwISsVMRvLKMFlHf7OSjlp3h9y8CizBZuBjsQQ6g-a939FDvGvNAfLNtxE3p1UNJMokHyqb7qGAUg0_gJy6kHrSoK2bW1wc7X0-btx0kVCk0JBUGvgbFPqeY4gmyRoEBiFI6tEBv159c0g5-KqnxFT5vWTiFys59t2Q_rekMw-Qe6Y1gmjENsmadfilFpqe5yiRuy58ZR16yyrmHPTqQn0e2fGdQVm4dGLmx_yBBPNMjyfiez73EHM0smtRivzuEqU2iefh3sGWky8lEp9vP5W6rtDNf6z6PhET2n1Hwhg36RIISUb6iuWG2WDJPqNVKgph0YFmZs78yQvBDsxj49NlPRPTVqMhcZ4SV8Oui9o39NCAG8CZ7ok-z9TywjF5-BflMEUBe9EZjQeBQx4PkHCFP81A5lwjRwPhRnTs8i0CohO8PLO4H1kGr3ptVN1WRhHrf0GOmkNHZ5Ny2w_-KMhiY7bwDZmc7THrNDkjbad_Kdb_sSW1VML4IeiyfQp99LRBb6cF1aNNYyuBrPMz-hThkFLZp9Yl0gh98fBR5NZY5MyezsZ9FUHL4Pmi2QWJ3Q70zpXnxB9GIIUmXYOoTRBydLhtrCO764qrTTyuaneZiRgLX8GcoBbrHJY2LZUwd7YAah9G8Uex-4Ftzftk2vvL3ffwwF8ZsMQL11y37rBrLpQuiP02w8nAGKnxKHRnc0EG8DJb6LBQy-816kx4hTgaFf3tJcFMMr9Iuvk%3D&amp;clickType=link_to_vacancy" target="_blank"><span class="magritte-icon-dynamic___KJ4yJ_14-2-0 magritte-icon-dynamic_hover-enabled___WblhN_14-2-0 magritte-icon-dynamic_press-enabled___aGKHB_14-2-0"><span class="magritte-text___pbpft_5-0-1 magritte-text_style-primary___AQ7MW_5-0-1 magritte-text_typography-title-4-semibold___vUqki_5-0-1"><span data-qa="serp-item__title-text" class="magritte-text___tkzIl_7-1-15">Директор по персоналу (HRD)</span></span></span></a>
                try:
                    url_one = one_obv.find_all("a", attrs={"data-qa": "serp-item__title"})[0]['href']
                except:
                    error_num+=1
                    continue
                urls_base.append(url_one)
    driver.close()
    return urls_base

from bs4 import BeautifulSoup as bs

def get_vacancy_price(html_source):
    global kapcha
    global error_req
    global error_num
    """
    Ультимативный поиск зарплаты: ищет по атрибутам, потом по тексту с рублями.
    """
    price = "З/П не указана"
    try:
        soup = bs(html_source, "html.parser")
        
        # 1. СТРОГОЕ ПРАВИЛО: Удаляем все комментарии
        for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
            comment.extract()

        # 2. Ищем через регулярку по всем возможным data-qa (net, gross, и т.д.)
        price_tag = soup.find(attrs={"data-qa": re.compile(r"vacancy-salary.*")})
        
        if price_tag:
            # Используем separator, чтобы цифры и валюта не слиплись
            raw_text = price_tag.get_text(separator=" ", strip=True)
            # Чистим от спец-пробелов (\xa0 и \u202f)
            price = " ".join(raw_text.replace("\xa0", " ").replace("\u202f", " ").split())
        
        # 3. АВАРИЙНЫЙ ПЛАН: если data-qa пустой, ищем любой тег со знаком рубля
        if price == "З/П не указана" or not any(char.isdigit() for char in price):
            # Ищем любой короткий текст, где есть '₽'
            emergency_tag = soup.find(lambda tag: tag.name in ["span", "div"] and 
                                     "₽" in tag.text and len(tag.text) < 60)
            if emergency_tag:
                price = " ".join(emergency_tag.get_text(strip=True).replace("\xa0", " ").split())
                
    except Exception as e:
        print(f"Ошибка в get_vacancy_price: {e}")
        error_num+=1
    return price


def ParsingSeleniumDriver(urls):
    global kapcha
    global error_req
    global error_num
    print("Начинаем парсинг данных. Подгрузка драйвера...", end="\r")
    options = webdriver.ChromeOptions()
    
    # Режим без окна включается только если не режим теста
    if not test_project:
        options.add_argument("--headless")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=2560,1440")
    # Маскировка под человека
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36")

    
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script("document.body.style.zoom='0.1'")
    wait = WebDriverWait(driver, 15)
    data = []
    
    # 1. Первоначальный заход для установки кук
    try:
        driver.get("https://rostov.hh.ru")
        with open("hh_cookies.pkl", "rb") as file:
            cookies = pickle.load(file)
            for cookie in cookies:
                driver.add_cookie(cookie)
        driver.refresh()
    except Exception as e:
        print(f"Ошибка при загрузке кук: {e}")
    with alive_bar(len(urls), 
            title='Основной парсинг',
            bar='filling',      # Название стиля из списка BARS
            spinner='wait4'    # Название стиля из списка SPINNERS
            ) as bar:
        for val, url in enumerate(urls, 1):
            try:
                #update_str(f"Обработка {val}/{len(urls)}")
                driver.get(url)
                bar()
                # 2. Проверка на капчу
                captchas = driver.find_elements(By.XPATH, "//img[@data-qa='account-captcha-picture']")
                if captchas:
                    #update_str("Обнаружена капча. Решаем...")
                    captchas[0].screenshot("current_captcha.png")
                    code = solve_captcha_api("current_captcha.png")
                    if code:
                        input_field = driver.find_element(By.NAME, "captchaText")
                        input_field.send_keys(code)
                        driver.find_element(By.XPATH, "//button[@data-qa='account-captcha-submit']").click()
                        sleep(3)
                    else:
                        #print(f"Не удалось решить капчу на {url}, пропускаем")
                        continue

                # 3. Ожидание перехода с рекламной ссылки на страницу вакансии
                try:
                    WebDriverWait(driver, 10).until(lambda d: "hh.ru/vacancy/" in d.current_url)
                except:
                    pass

                # 4. Инициализация переменных (защита от UnboundLocalError)
                name = "Не найдено"
                price = "З/П не указана"
                name_company = "Не найдена"
                phone_number = "Скрыт или нет"
                name_contact = "Не указано"
                city = "непонятно"

                # 5. Сбор данных вакансии (Title, Price, Company)
                try:
                    # Ждем появления заголовка
                    wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "[data-qa='vacancy-title']")))
                    
                    # Извлекаем название
                    name = driver.find_element(By.CSS_SELECTOR, "[data-qa='vacancy-title']").text
                    
                    # Ждем, пока блок зарплаты наполнится текстом (решает проблему пустых дампов)
                    try:
                        price = get_vacancy_price(driver.page_source)
                    except:
                        price = "З/П не указана"
                    #<div class="magritte-text___pbpft_5-0-1 magritte-text_style-primary___AQ7MW_5-0-1 magritte-text_typography-label-2-regular___ia7GB_5-0-1">Москва</div>
                    
                    
                    # Извлекаем компанию
                    try:
                        name_company = driver.find_element(By.CSS_SELECTOR, "[data-qa='vacancy-company-name']").text
                    except:
                        name_company = "Не указана"

                except Exception as e:
                    #print(f"Ошибка сбора основных данных на {url}: {e}")
                    name = "Ошибка загрузки"

                # 6. Взаимодействие с контактами
                try:
                    contact_btn_xpath = "//button[contains(@data-qa, 'show-employer-contacts')]"
                    buttons = driver.find_elements(By.XPATH, contact_btn_xpath)
                    
                    if buttons:
                        # Скроллим к кнопке и кликаем
                        driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", buttons[0])
                        sleep(2)
                        buttons[0].click()
                        
                        # Ждем подгрузки (AJAX)
                        sleep(2) 
                        #driver.save_screenshot("full_page.png")
                        # Для контактов используем BS4, так как их может быть несколько
                        soup_contacts = bs(driver.page_source, "html.parser")
                        city = soup_contacts.find("div", class_="magritte-text___pbpft_5-0-1 magritte-text_style-primary___AQ7MW_5-0-1 magritte-text_typography-label-2-regular___ia7GB_5-0-1").text
                        phone_tag = soup_contacts.find("span", attrs={"data-qa": "vacancy-contacts__phone-number"})
                        if phone_tag:
                            phone_number = phone_tag.get_text(strip=True)
                        #<div data-qa="vacancy-contacts__fio" class="magritte-text___pbpft_5-0-1 magritte-text_style-primary___AQ7MW_5-0-1 magritte-text_typography-title-5-semibold___Y-owC_5-0-1">Мозолевская Дарья Романовна</div>
                        soup_contacts = bs(driver.page_source, "html.parser")
                        #driver.save_screenshot("debug_view.png")
                        fio_tag = soup_contacts.find("div", attrs={"data-qa": "vacancy-contacts__fio"})
                        if fio_tag:
                            name_contact = fio_tag.get_text(strip=True)
                except Exception as e:
                    # Если контактов нет или кнопка не сработала — не критично
                    pass

                # Финальная очистка строк
                price = price.replace("\xa0", " ").replace("\u202f", " ").strip()
                name_company = name_company.replace("\xa0", " ").strip()

                row = [name, price, name_company, city, phone_number, name_contact, url]
                data.append(row)
                #print(f"Успешно: {name[:30]}...")

            except Exception as e:
                #print(f"Критическая ошибка на странице {url}: {e}")
                error_req+=1
                data.append(["ОШИБКА", str(e), "", "", "", url])

    driver.quit()
    return data
def save_to_excel(data_list):
    column_names = [
        "Название вакансии", 
        "Зарплата", 
        "Компания", 
        "Город",
        "Телефон", 
        "Контактное лицо",
        "Ссылка на объявление"
    ]
    df = pd.DataFrame(data_list, columns=column_names)
    file_name = f"db_{random.randint(100000, 999999)}.xlsx"
    df.to_excel(file_name, index=False)
    return file_name

def main():
    global kapcha
    global error_req
    global error_num
    #### СТАТИСТИКА ####
    start_time = time.perf_counter()

    ####################
    if not test_project:
        joker("Parser v1.0 by vology")   
        joker("TG: @onevology")
    while True:
        pages_num = input("Введите количество страниц (<=20) с объявлением (в каждой по 100): ")
        try:
            if int(pages_num) > 20:
                print("Введите значение меньше или равно 20!")
            else:
                break
        except:
            print("Введите число!")
    print("Получение ссылок на страницы hh.ru")
    urls = ParsingUrls(int(pages_num))
    print("Парсинг каждой страницы")
    data = ParsingSeleniumDriver(urls)   #  Имя вакансии, цена, название компании, номер телефона, имя контакта
    name_db = save_to_excel(data)
    print(f"Данные сохранены в базу {name_db}")

    end_time = time.perf_counter()
    #### СТАТИСТИКА ####
    total_time = end_time - start_time
    print("\n")
    print("==== Статистика вполнения ====") 
    print(f"Время выполнения программы: {total_time:.2f}\nКоличество ошибок: {error_num}\nКоличество ошибок сети: {error_req}\nКоличество капчи: {kapcha}")
    #################### 
    input("Чтобы закрыть окно нажмите Enter")
    
    #data = ParsingSeleniumDriver(["https://rostov.hh.ru/vacancy/132330040?hhtmFrom=vacancy_search_list"])
    #print(data)


if __name__ == "__main__":
    main()