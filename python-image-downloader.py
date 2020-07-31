from shutil import copyfileobj
from requests import get
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from time import sleep
from base64 import b64decode
import os

# Gets an array of keywords separated by spaces/유저가 입력한 키워드들을 리스트로 저장
keyword_list = input('어떤 사진들을 찾을까요(공백으로 구분해 주세요): ').split()
PATH = './chromedriver'
driver = webdriver.Chrome(PATH)

# Runs a for loop for each keyword/키워드 별로 반복문을 돌림
for keyword in keyword_list:
    # Link to images tab on Google with the keyword/구글의 키워드 검색결과의 이미지 탭으로 가는 링크
    url = '''https://www.google.com/search?tbm=isch&source=hp&biw=&bih=&ei=0VgdX4viLcq9hwOB7IngCQ&q=''' + keyword.strip()
    driver.get(url)
    # Creates a directory with the keyword if it doesn't exist/폴더가 없으면 키워드로 폴더를 만듦
    try:
        parent_dir = "./images/"
        path = os.path.join(parent_dir, keyword + 's')
        os.mkdir(path)
        print('Path made for ' + keyword)
    except:
        print('Directory already exists for keyword:', keyword)
    # Waits for 5 seconds in case the page doesn't load fast enough/페이지가 로딩이 느릴 때를 대비해 5초를 기다림
    sleep(5)
    # Goes to the bottom of the page/페이지의 가장 밑까지 가게하는 코드
    for j in range(10):
        driver.execute_script(
            'window.scrollTo(0,document.body.scrollHeight)')
        sleep(0.5)
    # Clicks the button that loads more images/이미지를 더 로딩하는 버튼을 누름
    more_btn = driver.find_element_by_class_name('mye4qd')
    actions = ActionChains(driver)
    actions.click(more_btn).perform()
    # Goes to the bottom of the next page/다음 페이지의 가장 밑까지 가게한다
    for j in range(10):
        driver.execute_script(
            'window.scrollTo(0,document.body.scrollHeight)')
        sleep(0.5)
    print('Done scrolling')
    # Finds all images within the page/페이지 내 모든 이미지를 찾음
    image_urls = driver.find_elements_by_css_selector('img.Q4LuWd')
    # Prints the amount of images-usually 400/이미지의 갯수를 출력함-보통 400 정도
    print('Found', len(image_urls), 'results')
    count = 1
    err = -1
    for image_idx in range(len(image_urls)):
        # Gets the source of the image(data or link)/이미지의 소스를 가져옴(데이터 혹은 링크)
        # Some images return None with 'src' but 'data-src' works/몇 이미지에는 'src'는 None을 반환하지만 'data-src'는 됨
        src = image_urls[image_idx].get_attribute('data-src') 
        if image_urls[image_idx].get_attribute('data-src') == None:
            src = image_urls[image_idx].get_attribute('src')
        try:
            # Overwrites the targeted image/선택된 이미지를 덮어쓴다
            # Although all links are saved as jpeg, some datas are stored as png the ternary statement below prevents error/링크 사진들은 모두 jpeg 포멧이지만 몇몇 데이터들은 png이므로 아래 삼항 연산자로 에러를 없앰
            with open("./images/{}/{}.{}".format(keyword + 's', str(count), 'png' if src[11] == 'p' and src[0] == 'd' else 'jpeg'), "wb") as f:
                # Image source is divided into two groups-base64 data and a link
                # if the first letter of the source is 'd' it is a data otherwise a link
                # 이미지 소스는 base64 데이터와 링크로 나뉜다
                # 만약 소스의 첫번째 글자가 'd'라면 데이터이고 아니면 링크이다
                if src[0] == 'd':  # Data/데이터
                    try:
                        # Decoding the data into an image-starts from the 22nd index because of google and their latency stuff
                        # 이미지 데이터를 디코딩해 저장한다(데이터를 해석해 저장)-구글의 레이턴시 관련 이유로 22번째 인덱스부터 시작한다.
                        f.write(b64decode(src[22:]))
                        count += 1
                    except:
                        print('Problem with saving image from encoded data:', src)
                else:  # Link/링크
                    try:
                        # Calls requests.get on the link which returns the image along with other things-stream is used for stability
                        # requests.get 함수를 사용해 링크에서 이미지(와 기타 등등)을 가져온다-stream은 안정성을 위해 추가
                        response = get(src, stream=True)
                        # Saves only the image in the currently open file
                        # 이미지만을 열고있는 파일에 저장한다.
                        copyfileobj(response.raw, f)
                        # Deletes the image to clear buffer-in case there is one
                        # 버퍼를 없앤다
                        del response
                        count += 1
                    except:
                        print('Problem with url:', src)
        except:
            print('Problem with opening image file',
                  image_urls[image_idx], image_idx)
            err = count-1
    print('Last found error index:', 'Not Found' if err == -1 else count-1)
    print('Done scrapping images')

# Closes the browser and stops code execution using selenium
# 브라우저를 닫고 더 이상의 셀레니움을 사용한 코드 실행을 멈춤
driver.quit()
