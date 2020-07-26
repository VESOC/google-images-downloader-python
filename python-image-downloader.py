from shutil import copyfileobj
from requests import get
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
import time
from base64 import b64decode
from os import path, mkdir


def save_image_to_file(image, dirname, suffix):
    with open('{dirname}/{suffix}.jpeg'.format(dirname=dirname, suffix=suffix), 'wb') as out_file:
        copyfileobj(image.raw, out_file)


data_list = input('어떤 사진들을 찾을까요(공백으로 구분해 주세요): ').split()
PATH = './chromedriver'
driver = webdriver.Chrome(PATH)
for data in data_list:
    url = '''https://www.google.com/search?tbm=isch&source=hp&biw=&bih=&ei=0VgdX4viLcq9hwOB7IngCQ&q=''' + data.strip()
    driver.get(url)
    try:
        parent_dir = "./images"
        path = path.join(parent_dir, data + 's')
        mkdir(path)
        print('Path made for ' + data)
    except:
        pass
    time.sleep(5)
    for j in range(15):
        driver.execute_script(
            "window.scrollTo(0,document.body.scrollHeight)")
        time.sleep(1)
    print('Done scrolling')
    image_urls = driver.find_elements_by_css_selector('img.Q4LuWd')
    print('Found', len(image_urls), 'results')
    for image_idx in range(len(image_urls)):
        n = image_urls[image_idx].get_attribute('src')
        try:
            with open("./images/{}/{}.{}".format(data + 's', str(image_idx+1), 'png' if n[11] == 'p' and n[0] == 'd' else 'jpeg'), "wb") as f:
                if n[0] == 'd':
                    try:
                        if type(n) is type('s'):
                            f.write(b64decode(n[22:]))
                    except:
                        pass
                else:
                    if type(n) is type('s'):
                        response = get(n, stream=True)
                        copyfileobj(response.raw, f)
                        del response
        except:
            pass
    print('Done scrapping images')


driver.quit()
