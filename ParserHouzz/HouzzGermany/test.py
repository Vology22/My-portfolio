import requests, pickle
import selenium
import os
from msedge.selenium_tools import Edge, EdgeOptions
#print(f"{os.getcwd()}\\Def")
#path_to_profil = f"{os.getcwd()}\\Def"
edge_options = EdgeOptions()
edge_options.use_chromium = True 
edge_options.add_argument("--start-maximized")
edge_options.add_argument("--disable-dev-shm-usage")
edge_options.add_argument("--no-sandbox") 
edge_options.add_argument("--remote-debugging-port=9222") 
edge_options.add_argument('--log-level=3')
edge_options.add_argument(f"user-data-dir=C:\\Users\\gogov\\AppData\\Local\\Microsoft\\Edge\\User Data")
edge_options.add_argument(f"profile-directory=Profile 1")
driver = Edge(options=edge_options, executable_path = os.getcwd() + "\\msedgedriver.exe")
driver.implicitly_wait(10) # Ждет до 10 секунд

url2 = "https://www.houzz.ru/professionaly/arhitektory/arhitekturnaya-masterskaya-sovremennyy-dom-pfvwru-pf~666189932"
url1 = "https://www.houzz.ru"


driver.get(url2)

input()
driver.close()
