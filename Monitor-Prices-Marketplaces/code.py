import os
try:
    from dotenv import load_dotenv; load_dotenv()
except ImportError:
    pass
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException, TimeoutException
import sqlite3
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from telegram import Bot
from telegram.error import TelegramError # Импортируем класс TelegramError

# Ваши настройки для Telegram бота
BOT_TOKEN = os.getenv('BOT_TOKEN')  # Замените на ваш токен бота
CHAT_ID = os.getenv('CHAT_ID')  # Замените на ID чата, куда отправлять сообщения

# Добавлены опции для Chrome, чтобы он работал в headless режиме и обходил некоторые ограничения.
options = webdriver.ChromeOptions()
# options.add_argument('--headless')  # Запуск в фоновом режиме
options.add_argument('--disable-gpu')  # Отключает аппаратное ускорение (полезно для headless)
options.add_argument('--disable-blink-features=AutomationControlled') # Маскировка от автоматизации
options.add_argument("window-size=1500,1200")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")

driver = webdriver.Chrome(options=options) # Инициализируем Chrome с опциями


links = ['https://megamarket.ru',
    'https://megamarket.ru/catalog/vakuumnye-upakovshiki/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A579192%7D%7D',
         'https://megamarket.ru/catalog/mobilnye-telefony/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A359990%7D%7D',
         'https://megamarket.ru/catalog/umnye-chasy/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A338059%7D%7D',
         'https://megamarket.ru/catalog/miksery/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A192846%7D%7D',
         'https://megamarket.ru/catalog/kuhonnye-kombajny/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100482%2C%22max%22%3A127952%7D%7D',
         'https://megamarket.ru/catalog/kuhonnye-mashiny/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A134769%7D%7D',
         'https://megamarket.ru/catalog/lomterezki/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A131626%7D%7D',
         'https://megamarket.ru/catalog/mikrovolnovye-pechi/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A140560%7D%7D',
         'https://megamarket.ru/catalog/sokovyzhimalki/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A109999%7D%7D',
         'https://megamarket.ru/catalog/mini-pechi/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A132999%7D%7D',
         'https://megamarket.ru/catalog/vakuumnye-upakovshiki/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A579192%7D%7D',
         'https://megamarket.ru/catalog/mobilnye-telefony/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A359990%7D%7D',
         'https://megamarket.ru/catalog/knopochnye-telefony/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A109000%7D%7D',
         'https://megamarket.ru/catalog/umnye-chasy/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A338059%7D%7D',
         'https://megamarket.ru/catalog/naushniki/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A754377%7D%7D',
         'https://megamarket.ru/catalog/chehly-dlya-sotovogo-telefona/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A108199%7D%7D',
         'https://megamarket.ru/catalog/vneshnie-akkumulyatory/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A181549%7D%7D',
         'https://megamarket.ru/catalog/ochki-virtualnoy-realnosti-dlya-smartfona/#?filters=%7B%2288C83F68482F447C9F4E401955196697%22%3A%7B%22min%22%3A100000%2C%22max%22%3A217790%7D%7D']

def pass_js_challenge(url: str) -> None:
    """Обходит Cloudflare JS challenge, используя существующий драйвер."""
    try:
        driver.get(url)
        time.sleep(10)  # Даем время на прохождение challenge
        print(f"Успешно пройден Cloudflare challenge для: {url}") # Убедимся, что вызов функции работает.
    except Exception as e:
        print(f"Ошибка при обходе Cloudflare: {e}")
        raise  # Перебрасываем исключение, чтобы основной цикл знал о проблеме

def scrape_megamarket(url):
    """Собирает информацию о товарах с Megamarket."""
    all_products = []
    page_number = 1
    while True:
        try:
            # Сначала пытаемся пройти Cloudflare challenge
            try:
                pass_js_challenge(url)
            except Exception:
                print(f"Не удалось пройти Cloudflare для {url}, прекращаем обработку.")
                break # Если не удалось пройти Cloudflare, прекращаем обработку страницы.


            print(f"Обрабатывается страница: {url}")

            product_elements = driver.find_elements(By.XPATH, '//div[@class="catalog-item-regular-desktop__main-info"]/a')
            price_elements = driver.find_elements(By.XPATH, '//div[@class="catalog-item-regular-desktop__price-block"]/div')

            if not product_elements:
                print("Нет элементов товара на странице.")
                break

            for i in range(len(product_elements)):
                try:
                    text_MM = product_elements[i].text
                    href_MM = product_elements[i].get_attribute('href')
                    price_MMTEST1 = price_elements[i]
                    price_MMTEST2 = price_MMTEST1.text
                    no_spaces_MM = price_MMTEST2.replace(" ", "")
                    price_MM = "".join(char for char in no_spaces_MM if char.isdigit())
                    product_data = {
                        'name': text_MM,
                        'href': href_MM,
                        'price': price_MM
                    }
                    all_products.append(product_data)
                except Exception as e:
                    print(f"Ошибка при обработке товара: {e}")

            try:
                next_page_button = driver.find_element(By.CLASS_NAME, 'pagination-widget__page-link_next')
                next_page_url = next_page_button.get_attribute('href')
                if next_page_url:
                    url = next_page_url
                    page_number += 1
                    print(f"Переход на страницу {page_number}")
                    continue
                else:
                    print("Нет ссылки на следующую страницу. Завершение.")
                    break

            except NoSuchElementException:
                print("Кнопка 'Следующая страница' не найдена. Завершение.")
                break
            except Exception as e:
                print(f"Произошла ошибка при переходе на следующую страницу: {e}")
                break
        except Exception as e:
             print(f"Произошла общая ошибка при обработке страницы {url}: {e}")
             break

    return all_products


def compare_prices_citilink(product_name, mega_price, mega_href, db_cursor, bot):
    """Сравнивает цены с Citilink."""
    try:
        driver.get('https://www.citilink.ru/')
        time.sleep(5)
        poisk_citiling = driver.find_element(By.XPATH,'//*[@id="__next"]/div[1]/div[2]/div/div[2]/div/div/div[2]/div[1]/form/div/div/label/input')

        poisk_citiling.click()
        poisk_citiling.send_keys(str(product_name))

        Search_citiling = driver.find_element(By.XPATH,'//div[@class="app-catalog-1b7tt3f-components--IconWrapper e11t2rk810"]/button[2]')
        Search_citiling.click()

        time.sleep(5)

        for j in range(7):
            try:
                block_citiling = driver.find_element(By.XPATH,f'(//div[@class="e1w8wkln0 app-catalog-keatef-StyledWrapper-StyledSnippetProductVerticalLayout e5jybzt0"]/a)[{j + 1}]')
                href_citiling = block_citiling.get_attribute('href')
                price_citilinTEST1 = driver.find_element(By.XPATH,f'(//span[@class="e4ahr150 e1a7a4n70 app-catalog-e46fw7-StyledTypography--getTypographyStyle-composeBreakpointsStyles--arrayOfStylesByBreakpoints-StyledText--getTextStyle-Text--StyledTextComponent-MainPriceNumber--StyledMainPriceNumber ez8h4tf0"])[{j+1}]')
                price_citilingTEST2 = price_citilinTEST1.text
                no_spaces_citiling = price_citilingTEST2.replace(" ", "")
                price_citiling = "".join(char for char in no_spaces_citiling if char.isdigit())
                if price_citiling:
                    percentage_difference = ((int(mega_price)-int(price_citiling)) / int(price_citiling)) * 100
                    if percentage_difference >= 30:
                        # Проверяем, было ли уже найдено это совпадение
                        db_cursor.execute("SELECT 1 FROM found_prices WHERE mega_href = ? AND citilink_href = ?", (mega_href, href_citiling))
                        if db_cursor.fetchone() is None: # Если совпадение не найдено в базе данных
                            message = f"Нашел совпадение в Citilink: {mega_href} и {href_citiling}"
                            print(message)
                            try:
                                bot.send_message(chat_id=CHAT_ID, text=message) # Отправляем сообщение в Telegram
                            except TelegramError as e:
                                print(f"Ошибка при отправке сообщения в Telegram: {e}")

                            # Записываем найденное совпадение в базу данных
                            db_cursor.execute("INSERT INTO found_prices (mega_href, citilink_href) VALUES (?, ?)", (mega_href, href_citiling))
                            return  # Совпадение найдено, выходим из цикла
                        else:
                            print(f"Совпадение в Citilink уже найдено: {mega_href} и {href_citiling}")
                        # return  # Совпадение найдено, выходим из цикла -  Убрал, чтобы продолжать искать другие совпадения
                    else:
                        print(f'Попытка сравнения {product_name} с товаром {j+1} в Citilink: Разница {percentage_difference:.2f}%')
                else:
                    print("Не удалось извлечь цену из Citilink.")
            except NoSuchElementException:
                print(f"Товар {j+1} не найден в Citilink.")
                continue  # Перейти к следующему товару
            except Exception as e:
                print(f"Ошибка при обработке товара {j+1} в Citilink: {e}")
                continue
        print("Совпадений не найдено в Citilink.")

    except Exception as e:
        print(f"Общая ошибка при сравнении цен в Citilink: {e}")
        return None

def compare_prices_mvideo(product_name, mega_price, mega_href, db_cursor, bot):
    """Сравнивает цены с M.Видео."""
    try:
        driver.get('https://www.mvideo.ru/')
        time.sleep(5)
        search_mvideo = driver.find_element(By.XPATH, '//div[@class="input__container"]/input')
        search_mvideo.send_keys(product_name)
        search_mvideo.send_keys(u'\ue007')  # Send ENTER key
        time.sleep(5)

        for j in range(7):
            try:
                href_mvideo = driver.find_element(By.XPATH, f'(//div[@class="product-title product-title--grid"]/a)[{j+1}]').get_attribute('href')
                price_element = driver.find_element(By.XPATH, f'(//div[@class="price price--grid ng-star-inserted"]/span[1])[{j+1}]')
                price_mvideo_text = price_element.text
                price_mvideo = "".join(char for char in price_mvideo_text if char.isdigit())

                if price_mvideo:
                    percentage_difference = ((int(mega_price) - int(price_mvideo)) / int(price_mvideo)) * 100
                    if percentage_difference >= 30:
                        # Проверяем, было ли уже найдено это совпадение
                        db_cursor.execute("SELECT 1 FROM found_prices WHERE mega_href = ? AND mvideo_href = ?", (mega_href, href_mvideo))
                        if db_cursor.fetchone() is None: # Если совпадение не найдено в базе данных
                            message = f"Нашел совпадение в M.Видео: {mega_href} и {href_mvideo}"
                            print(message)
                            try:
                                bot.send_message(chat_id=CHAT_ID, text=message) # Отправляем сообщение в Telegram
                            except TelegramError as e:
                                print(f"Ошибка при отправке сообщения в Telegram: {e}")
                            # Записываем найденное совпадение в базу данных
                            db_cursor.execute("INSERT INTO found_prices (mega_href, mvideo_href) VALUES (?, ?)", (mega_href, href_mvideo))
                            return
                        else:
                            print(f"Совпадение в M.Видео уже найдено: {mega_href} и {href_mvideo}")
                        # return
                    else:
                        print(f'Попытка сравнения {product_name} с товаром {j+1} в M.Видео: Разница {percentage_difference:.2f}%')
                else:
                    print("Не удалось извлечь цену из M.Видео.")
            except NoSuchElementException:
                print(f"Товар {j+1} не найден в M.Видео.")
                continue
            except Exception as e:
                print(f"Ошибка при обработке товара {j+1} в M.Видео: {e}")
                continue
        print("Совпадений не найдено в M.Видео.")
    except Exception as e:
        print(f"Общая ошибка при сравнении цен в M.Видео: {e}")
        return None

def compare_prices_technopark(product_name, mega_price, mega_href, db_cursor, bot):
    """Сравнивает цены с Технопарк."""
    try:
        driver.get('https://technopark.ru/')
        time.sleep(5)

        # Замените на фактический XPATH
        search_technopark = driver.find_element(By.XPATH, '//form[@class="header-search-input header-search-input--new is-active header-search-input--suggest-open"]/input') # XPATH ПОЛЯ ПОИСКА Технопарк
        search_technopark.send_keys(product_name)
        search_technopark.send_keys(u'\ue007')  # Send ENTER key
        time.sleep(5)

        for j in range(7):
            try:
                # Замените на фактические XPATH
                #Исправлено на поиск первого элемента, тк xpath одинаковый
                product_element = driver.find_element(By.XPATH, '//div[@class="product-card-big__body"]/a[2]') # XPATH БЛОКА ТОВАРА Технопарк
                href_technopark = product_element.get_attribute('href') # XPATH ССЫЛКИ НА ТОВАР В БЛОКЕ Технопарк
                price_element = driver.find_element(By.XPATH, '//div[@class="product-prices product-card-big__prices product-prices product-prices--theme-light product-prices--large product-prices--al-left product-prices--dir-vertical"]/div') # XPATH ЦЕНЫ ТОВАРА В БЛОКЕ Технопарк
                price_technopark_text = price_element.text
                price_technopark = "".join(char for char in price_technopark_text if char.isdigit())

                if price_technopark:
                    percentage_difference = ((int(mega_price) - int(price_technopark)) / int(price_technopark)) * 100
                    if percentage_difference >= 30:
                        # Проверяем, было ли уже найдено это совпадение
                        db_cursor.execute("SELECT 1 FROM found_prices WHERE mega_href = ? AND technopark_href = ?", (mega_href, href_technopark))
                        if db_cursor.fetchone() is None: # Если совпадение не найдено в базе данных
                            message = f"Нашел совпадение в Технопарк: {mega_href} и {href_technopark}"
                            print(message)
                            try:
                                bot.send_message(chat_id=CHAT_ID, text=message)  # Отправляем сообщение в Telegram
                            except TelegramError as e:
                                print(f"Ошибка при отправке сообщения в Telegram: {e}")
                            # Записываем найденное совпадение в базу данных
                            db_cursor.execute("INSERT INTO found_prices (mega_href, technopark_href) VALUES (?, ?)", (mega_href, href_technopark))
                            return
                        else:
                            print(f"Совпадение в Технопарк уже найдено: {mega_href} и {href_technopark}")
                        # return
                    else:
                        print(f'Попытка сравнения {product_name} с товаром {j+1} в Технопарк: Разница {percentage_difference:.2f}%')
                else:
                    print("Не удалось извлечь цену из Технопарка.")
            except NoSuchElementException:
                print(f"Товар {j+1} не найден в Технопарк.")
                continue
            except Exception as e:
                print(f"Ошибка при обработке товара {j+1} в Технопарк: {e}")
                continue
        print("Совпадений не найдено в Технопарк.")

    except Exception as e:
        print(f"Общая ошибка при сравнении цен в Технопарк: {e}")
        return None

def compare_prices_dns(product_name, mega_price, mega_href, db_cursor, bot):
    """Сравнивает цены с DNS."""
    try:
        driver.get('https://www.dns-shop.ru/')
        time.sleep(5)

        # Замените на фактический XPATH
        search_dns = driver.find_element(By.XPATH, '//div[@class="presearch__wrapper"]/input') # XPATH ПОЛЯ ПОИСКА DNS
        search_dns.send_keys(product_name)
        search_dns.send_keys(u'\ue007')  # Send ENTER key
        time.sleep(5)

        for j in range(7):
            try:
                # Замените на фактические XPATH
                #Исправлено на поиск первого элемента, тк xpath одинаковый
                href_dns = driver.find_element(By.XPATH, f'(//div[@class="catalog-product__name-wrapper"]/a)[{j+1}]').get_attribute('href') # XPATH ССЫЛКИ НА ТОВАР В БЛОКЕ DNS
                price_element = driver.find_element(By.XPATH, f'(//div[@class="product-buy__price-wrap product-buy__price-wrap_interactive"]/div[1])[{j+1}]') # XPATH ЦЕНЫ ТОВАРА В БЛОКЕ DNS
                price_dns_text = price_element.text
                price_dns = "".join(char for char in price_dns_text if char.isdigit())

                if price_dns:
                    percentage_difference = ((int(mega_price) - int(price_dns)) / int(price_dns)) * 100
                    if percentage_difference >= 30:
                        # Проверяем, было ли уже найдено это совпадение
                        db_cursor.execute("SELECT 1 FROM found_prices WHERE mega_href = ? AND dns_href = ?", (mega_href, href_dns))
                        if db_cursor.fetchone() is None: # Если совпадение не найдено в базе данных
                            message = f"Нашел совпадение в DNS: {mega_href} и {href_dns}"
                            print(message)
                            try:
                                bot.send_message(chat_id=CHAT_ID, text=message) # Отправляем сообщение в Telegram
                            except TelegramError as e:
                                print(f"Ошибка при отправке сообщения в Telegram: {e}")
                            # Записываем найденное совпадение в базу данных
                            db_cursor.execute("INSERT INTO found_prices (mega_href, dns_href) VALUES (?, ?)", (mega_href, href_dns))
                            return
                        else:
                            print(f"Совпадение в DNS уже найдено: {mega_href} и {href_dns}")
                        # return
                    else:
                        print(f'Попытка сравнения {product_name} с товаром {j+1} в DNS: Разница {percentage_difference:.2f}%')
                else:
                    print("Не удалось извлечь цену из DNS.")
            except NoSuchElementException:
                print(f"Товар {j+1} не найден в DNS.")
                continue
            except Exception as e:
                print(f"Ошибка при обработке товара {j+1} в DNS: {e}")
                continue
        print("Совпадений не найдено в DNS.")

    except Exception as e:
        print(f"Общая ошибка при сравнении цен в DNS: {e}")
        return None

# Подключение к базе данных
conn = sqlite3.connect('price_comparisons.db') # Создаем подключение к базе данных
cursor = conn.cursor()

# Создание таблицы для хранения найденных совпадений (если она не существует)
cursor.execute("""
    CREATE TABLE IF NOT EXISTS found_prices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        mega_href TEXT,
        citilink_href TEXT,
        mvideo_href TEXT,
        technopark_href TEXT,
        dns_href TEXT
    )
""")
conn.commit()

# Инициализация бота Telegram
try:
    bot = Bot(token=BOT_TOKEN)
    print("Бот Telegram успешно инициализирован.")
except Exception as e:
    print(f"Ошибка при инициализации бота Telegram: {e}.  Проверьте токен.")
    bot = None #  Если бот не инициализирован, присваиваем None, чтобы избежать ошибок

# Основной цикл
for link in links:
    try:
        megamarket_products = scrape_megamarket(link)

        if megamarket_products:
            print(f"Найдено {len(megamarket_products)} товаров на Megamarket.")

            for product in megamarket_products:
                if bot: # Проверяем, что бот был успешно инициализирован
                    compare_prices_citilink(product['name'], product['price'], product['href'], cursor, bot)
                    compare_prices_mvideo(product['name'], product['price'], product['href'], cursor, bot)  # Передаем собранные данные
                    compare_prices_technopark(product['name'], product['price'], product['href'], cursor, bot)
                    compare_prices_dns(product['name'], product['price'], product['href'], cursor, bot)
                else:
                    print("Telegram бот не инициализирован, пропуск отправки сообщений.")
        else:
            print(f"Не удалось получить товары с {link}.")
            continue

    except Exception as e:
        print(f"Произошла общая ошибка при обработке {link}: {e}")
        continue

driver.quit()
conn.commit() # Сохраняем изменения в базе данных
conn.close() # Закрываем соединение с базой данных
print("Завершено.")