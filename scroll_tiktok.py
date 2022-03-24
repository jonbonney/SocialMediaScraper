from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import undetected_chromedriver.v2 as uc
import time
import random


def main():
    # options = webdriver.ChromeOptions()
    # options.add_argument('--disable-blink-features=AutomationControlled')
    # options.add_experimental_option("excludeSwitches", ['enable-automation'])
    driver = uc.Chrome()
    scroll_pause = 0.5
    scroll_final = 3

    driver.get('http://www.tiktok.com/@hottopic')

    # Get scroll height
    last_height = driver.execute_script("return document.body.scrollHeight")

    while True:
        # Scroll to bottom of page
        driver.execute_script("window.scrollTo({top: document.body.scrollHeight, behavior: 'smooth'});")

        # Wait to load page
        time.sleep(scroll_pause)

        # Calculate new scroll height and compare with last scroll height
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(scroll_final)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
        last_height = new_height

    time.sleep(10)


if __name__ == '__main__':
    main()




