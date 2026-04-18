########################################################## Parser by Vology #############################################################################
# Привет, мой дорогой друг. Если ты читаешь этот комментарий, то скорее всего ты работаешь над парсером, который писал я.
# Уверен, во время работы над ним у тебя появятся вопросы... Много вопросов. 
# Если тебе потребуется помощь, пиши сюда TG @onevology
# Удачи! <3
from bs4 import BeautifulSoup as bs
import io
a = ''
with io.open("sites.html", "r", encoding='utf-8') as f:
    a = f.read()
#print(r.status_code)
soup = bs(a, "html.parser")
name_group = soup.find_all("li")
chlen = '['
for i in name_group:
    #print(i)
    print(i.find_all("a")[0]["href"])
    chlen += f'["{i.find_all("a")[0].text}", "{i.find_all("a")[0]["href"]}"], '
print(chlen + "]")
#<a href="https://vk.com/biovk?from=top&trackcode=d37ade76_NeyKPXxzU_PXcCmflCMVYB-7ZCw6ohlOH9ujy2lT7oluQPKEIyjA9xTxLJ-XplVwBGd5dw" onclick="return nav.go(this, event, { params: { search_string: '' }})">Биология</a>
# <div class="labeled title verified_label">
