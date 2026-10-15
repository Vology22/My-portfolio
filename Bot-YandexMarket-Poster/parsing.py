from bs4 import BeautifulSoup as bs
import requests
import random
print("Parse-модуль активирован")

test = "https://ya.cc/m/6PDfTQ"
headers = {
    'User-Agent': ('Mozilla/5.0 (Windows NT 6.0; rv:14.0) Gecko/20100101 '
                   'Firefox/14.0.1'),
    'Accept':
    'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Language':
    'ru-ru,ru;q=0.8,en-us;q=0.5,en;q=0.3',
    'Accept-Encoding':
    'gzip, deflate',
    'Connection':
    'keep-alive',
    'DNT':
    '1'
}
#<div class="_23gJ9">   <div class="_1nuzB _1MOwX _1bCJz Mb7vH">flex
#<span class="ds-text ds-text_weight_bold ds-text_color_price-term ds-text_typography_headline-3 ds-text_headline-3_tight ds-text_headline-3_bold">113 850</span>
#<article class="_3zVgf _3Urwh _2xIXL">flex
#<img id="transition-page" class="_1WAh0" alt="Ноутбук Apple MacBook Air 13 2024" src="https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/orig" srcset="https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/120x160 120w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/180x240 180w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/240x320 240w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/300x400 300w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/351x468 351w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/402x536 402w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/450x600 450w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/501x668 501w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/552x736 552w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/600x800 600w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/900x1200 900w, https://avatars.mds.yandex.net/get-mpic/5319329/2a00000…/optimize 1200w" loading="eager" sizes="(max-width: 1199px) 266px, (max-width: 1365px) 334px, (max-width: 1535px) 414px, (max-width: 1919px) 480px, 576px" fetchpriority="high">
def parse_YM(url):
    try:
        
        r = requests.get(url, headers=headers)
        print(r.status_code)
        soup = bs(r.text, "html.parser")
        try:
            title = soup.find_all('div', class_='_1nuzB _1MOwX _1bCJz Mb7vH')[0].find_all('div')[0].find_all('h1')[0].text
        except:
            redirect_url = r.url
            print(redirect_url)
            r.close()
            r = requests.get(redirect_url, headers=headers)
            soup = bs(r.text, "html.parser")
            title = soup.find_all('div', class_='_1nuzB _1MOwX _1bCJz Mb7vH')[0].find_all('div')[0].find_all('h1')[0].text
        price = soup.find_all('span', class_='ds-text ds-text_weight_bold ds-text_color_price-term ds-text_typography_headline-3 ds-text_headline-3_tight ds-text_headline-3_bold')[0].text.replace("\u2006", "")
        try:
            img = soup.find_all("article", class_='_3zVgf _3Urwh _2xIXL')[0].find_all("img")[0]["src"]
        except:
            #<article class="_3zVgf _3Urwh _21HC9">flex
            img = soup.find_all("article", class_='_3zVgf _3Urwh _21HC9')[0].find_all("img")[0]["src"]
        return {
            "title" : title,
            "price" : price,
            "img" : img
            }
    except Exception as e:
        return e
print(parse_YM(test))