import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
import lxml.html
from lxml.cssselect import CSSSelector
import time

import os

print("########## 하영의 구글 이미지 크롤링 ###########")
search_key = input("검색 키워드 입력: ")
url = f'https://www.google.com/search?q={search_key}&tbm=isch&ved=2ahUKEwid5YCD14DsAhVZAaYKHezkC_UQ2-cCegQIABAA&oq=keywordfdfdfdf&gs_lcp=CgNpbWcQAzoECAAQGDoGCAAQChAYUMYYWM8cYOAdaABwAHgAgAFviAHfBZIBAzEuNpgBAKABAaoBC2d3cy13aXotaW1nwAEB&sclient=img&ei=ovtrX52MDtmCmAXsya-oDw&bih=937&biw=1920&hl=ko'

browser = webdriver.Chrome()
browser.get(url)

# html = browser.page_source
# soup = BeautifulSoup(html)
html = requests.get(url, stream=True)
html.raw.decode_content = True
tree = lxml.html.parse(html.raw)

# image_selector = CSSSelector('img.rg_i.Q4LuWd')
# images = image_selector(tree)
images = browser.find_elements_by_css_selector('img.rg_i.Q4LuWd')
print(images)

imgurls = []

for img in images:
    imgElement = None
    try:
        img.click();
        #element = WebDriverWait(browser, 3).until(EC.presence_of_all_elements_located((By.ID, 'Sva75c')))
        time.sleep(1)
        soup = BeautifulSoup(browser.page_source, 'html.parser')
        imgElement = soup.select_one('div#Sva75c div.v4dQwb img.n3VNCb')
        imgurls.append(imgElement.attrs["src"])

    except KeyError:
        imgurls.append(imgElement.attrs["data-src"])
    except:
        continue

if not os.path.exists(search_key):
    os.mkdir(search_key)


print(imgurls)


browser.close()