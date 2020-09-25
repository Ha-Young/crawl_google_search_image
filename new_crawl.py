import os
import time
import socket

from urllib.request import urlretrieve
from urllib.error import HTTPError, URLError
from selenium import webdriver
from selenium.common.exceptions import ElementClickInterceptedException, NoSuchElementException, \
    ElementNotInteractableException
from PIL import Image
from pygame import mixer

def scroll_down():
    scroll_count = 0

    print("ㅡ 스크롤 다운 시작 ㅡ")

    # 스크롤 위치값 얻고 last_height 에 저장
    last_height = driver.execute_script("return document.body.scrollHeight")

    # 결과 더보기 버튼을 클릭했는지 유무
    after_click = False

    while True:
        print(f"ㅡ 스크롤 횟수: {scroll_count} ㅡ")
        # 스크롤 다운
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        scroll_count += 1
        time.sleep(1)

        # 스크롤 위치값 얻고 new_height 에 저장
        new_height = driver.execute_script("return document.body.scrollHeight")

        # 스크롤이 최하단이며
        if last_height == new_height:

            # 결과 더보기 버튼을 클릭한적이 있는 경우
            if after_click is True:
                print("ㅡ 스크롤 다운 종료 ㅡ")
                break

            # 결과 더보기 버튼을 클릭한적이 없는 경우
            if after_click is False:
                if driver.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div/div[5]/input').is_displayed():
                    driver.find_element_by_xpath('//*[@id="islmp"]/div/div/div/div/div[5]/input').click()
                    after_click = True
                elif NoSuchElementException:
                    print("ㅡ NoSuchElementException ㅡ")
                    print("ㅡ 스크롤 다운 종료 ㅡ")
                    break

        last_height = new_height

def click_and_retrieve(index, img, img_list_length):
    global crawled_count
    try:
        img.click()
        driver.implicitly_wait(3)
        src = driver.find_element_by_xpath(
            '//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div[1]/div[1]/div/div[2]/a/img').get_attribute('src')
        if src.split('.')[-1] == "png":
            urlretrieve(src, path + date + '/' + query + '/' + str(crawled_count + 1) + ".png")
            print(f"{index + 1} / {img_list_length} 번째 사진 저장 (png)")
        else:
            urlretrieve(src, path + date + '/' + query + '/' + str(crawled_count + 1) + ".jpg")
            print(f"{index + 1} / {img_list_length} 번째 사진 저장 (jpg)")
        crawled_count += 1

    except HTTPError:
        print("ㅡ HTTPError & 패스 ㅡ")
        pass

def crawling():
    global crawled_count

    print("ㅡ 크롤링 시작 ㅡ")

    # 이미지 고급검색 중 이미지 유형 '사진'
    url = f"https://www.google.com/search?as_st=y&tbm=isch&hl=ko&as_q={query}&as_epq=&as_oq=&as_eq=&cr=&as_sitesearch=&safe=images&tbs=itp:photo"
    driver.get(url)
    driver.maximize_window()
    scroll_down()

    div = driver.find_element_by_xpath('//*[@id="islrg"]/div[1]')
    # class_name에 공백이 있는 경우 여러 클래스가 있는 것이므로 아래와 같이 css_selector로 찾음
    img_list = div.find_elements_by_css_selector(".rg_i.Q4LuWd")
    os.makedirs(path + date + '/' + query)
    print(f"ㅡ {path}{date}/{query} 생성 ㅡ")

    for index, img in enumerate(img_list):
        try:
            click_and_retrieve(index, img, len(img_list))

        except ElementClickInterceptedException:
            print("ㅡ ElementClickInterceptedException ㅡ")
            driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
            print("ㅡ 100만큼 스크롤 다운 및 3초 슬립 ㅡ")
            time.sleep(3)
            click_and_retrieve(index, img, len(img_list))

        except NoSuchElementException:
            print("ㅡ NoSuchElementException ㅡ")
            driver.execute_script("window.scrollTo(0, window.scrollY + 100)")
            print("ㅡ 100만큼 스크롤 다운 및 3초 슬립 ㅡ")
            time.sleep(3)
            click_and_retrieve(index, img, len(img_list))

        except ConnectionResetError:
            print("ㅡ ConnectionResetError & 패스 ㅡ")
            pass

        except URLError:
            print("ㅡ URLError & 패스 ㅡ")
            pass

        except socket.timeout:
            print("ㅡ socket.timeout & 패스 ㅡ")
            pass

        except socket.gaierror:
            print("ㅡ socket.gaierror & 패스 ㅡ")
            pass

        except ElementNotInteractableException:
            print("ㅡ ElementNotInteractableException ㅡ")
            break

    try:
        print("ㅡ 크롤링 종료 (성공률: %.2f%%) ㅡ" % (crawled_count / len(img_list) * 100.0))

    except ZeroDivisionError:
        print("ㅡ img_list 가 비어있음 ㅡ")

    #driver.quit()

def filtering():
    print("ㅡ 필터링 시작 ㅡ")
    filtered_count = 0
    dir_name = path + date + '/' + query
    for index, file_name in enumerate(os.listdir(dir_name)):
        try:
            file_path = os.path.join(dir_name, file_name)
            img = Image.open(file_path)

            # 이미지 해상도의 가로와 세로가 모두 350이하인 경우
            if img.width < 200 and img.height < 200:
                img.close()
                os.remove(file_path)
                print(f"{index} 번째 사진 삭제")
                filtered_count += 1

        # 이미지 파일이 깨져있는 경우
        except OSError:
            os.remove(file_path)
            filtered_count += 1

    print(f"ㅡ 필터링 종료 (총 갯수: {crawled_count - filtered_count}) ㅡ")

def checking():
    # 입력 받은 검색어가 이름인 폴더가 존재하면 중복으로 판단
    for dir_name in os.listdir(path):
        file_list = os.listdir(path + dir_name)
        if query in file_list:
            print(f"ㅡ 중복된 검색어 ({dir_name}) ㅡ")
            return True




search_key = ['한글','illustration', 'illust','nature', 'picture', 'photo', 'drawing', 'take photo', 'background image', 'sky', 'dark star', 'party', 'movie', 'poster', 'good image', 'confuse image', '이미지', '자동차', '신용카드', '신용카드 배경', '일러스트', '일러스트레이션', '그림', '배경화면', '배경', '사진', '자연', '풍경', '거리', 'street', 'hiphop', 'concert', '포스터', '판촉물', '상품', 'product', '복잡한 이미지', '깨끗한 이미지', '배경 이미지', '책', 'book', '책 이미지', '법원문서', '문서', 'document', 'math', '수학', '역사', 'history', 'path', '경로', 'algorithm', '알고리즘', 'microsoft', 'stock', 'girl group', 'building', '빌딩', 'structure', '구조', '컴퓨터', 'coumputer', 'vacation', '휴가', 'sky diving', '스카이다이빙', '바다', 'sea', 'sea picture', '바다 사진', '바닷속', 'animation', '하늘 사진', 'sky picture', 'sky photo', 'brand', 'brand shop', '편집샵', '산속', 'forest', 'forest picture', '산속 사진', '사막', 'desert', '사막 사진', 'desert picture', 'desert photo', 'nature picture', 'nature photo', 'nature', 'nature page2', 'nature page3', 'nature page4', 'background page1', 'background page2', 'background page3', 'background page4', 'background page5']
# query = 'illustration'

for query in search_key:
    # clickAndRetrieve() 과정에서 urlretrieve 이 너무 오래 걸릴 경우를 대비해 타임 아웃 지정
    socket.setdefaulttimeout(30)

    # 이미지들이 저장될 경로 및 폴더 이름
    path = "D:/Crawling/"
    date = "2020.09.24"

    # 드라이버 경로 지정 (Microsoft Edge)
    driver = webdriver.Chrome()

    # 크롤링한 이미지 수
    crawled_count = 6000

    # 검색어 입력 받기
    # query = input("입력: ")
    # # 이미 크롤링했던 검색어일 때
    # while checking() is True:
    #     query = input("입력: ")

    crawling()
    filtering()

driver.close()