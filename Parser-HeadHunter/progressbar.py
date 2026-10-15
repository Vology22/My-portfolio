from alive_progress.styles import BARS, SPINNERS
from alive_progress import alive_bar

'''# Вывести названия всех доступных баров
print("Доступные бары:", list(BARS.keys()))

print("\nДоступные спиннеры:", list(SPINNERS.keys()))

import time  #wait3

items = range(50)
#filling
for c in list(SPINNERS.keys()):
    with alive_bar(len(items), 
                title=c,
                bar='filling',      # Название стиля из списка BARS
                spinner=c     # Название стиля из списка SPINNERS
                ) as bar:
        for item in items:
            time.sleep(0.1)
            bar()'''
print("\n\n"*100)
from tqdm import tqdm
import time
for i in tqdm(range(100)):
    time.sleep(0.05)


print ("\n\n")
for i in tqdm(range(100), 
              desc="Загрузка файлов", 
              ascii=False, 
              ncols=100, 
              colour='green'):
    time.sleep(0.05)

print("\n\n")
'''
from tqdm.notebook import tqdm
for i in tqdm(range(100)):
    time.sleep(0.05)'''