import pickle
from selenium import webdriver

def save_coockie():
    driver = webdriver.Chrome()
    driver.get("https://rostov.hh.ru")

    input("Залогинься вручную в браузере и нажми Enter здесь...")

    with open("hh_cookies.pkl", "wb") as file:
        pickle.dump(driver.get_cookies(), file)
    driver.quit()

if __name__ == "__main__":
    save_coockie()