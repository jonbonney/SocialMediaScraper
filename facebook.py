import undetected_chromedriver.v2 as uc
import time
from selenium.webdriver.common.by import By
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common import exceptions
from selenium.webdriver.support.wait import WebDriverWait
import re
import math


def time_elapsed(time_start):
    # Display time elapsed
    elapsed = round(time.perf_counter() - time_start)
    print('Time Elapsed: ' + str(math.floor(elapsed/60)) + ':' + str(elapsed % 60).zfill(2))


def main():
    time_start = time.perf_counter()

    driver = uc.Chrome()
    driver.implicitly_wait(5)
    action = ActionChains(driver)

    # Request the webpage
    driver.get('https://www.facebook.com/7Eleven')
    # Implicitly wait for page to load by looking for the h1 element
    driver.find_element(By.TAG_NAME, 'h1')
    time.sleep(2)
    time_elapsed(time_start)

    # # # This whole section was to exit a dialog that appears asking to log into facebook
    # # # but this dialog no longer seems to appear
    # Move mouse to near the top of screen
    # login_button = driver.find_element(By.LINK_TEXT, "Log In")
    # action = ActionChains(driver)
    # action.move_to_element(login_button)
    # action.move_by_offset(-100, 0)
    # action.perform()
    # print('Mouse moved to near the top of screen')

    # Scroll down a bit
    # driver.execute_script("window.scrollTo({top: 2000, behavior: 'smooth'});")
    # print('scrolling')

    # Wait for login dialogue to appear, then click outside the dialogue
    # time.sleep(3)
    # action.click().perform()
    # print('exiting login dialogue')

    # Scroll down a bit to load widgets
    # driver.execute_script("window.scrollTo({top: 4000, behavior: 'smooth'});")
    # print('scrolling')
    # time.sleep(0.5)
    # time_elapsed(time_start)

    # Look for all the side card widgets
    class_id = 'sjgh65i0'
    cards = driver.find_elements(By.CLASS_NAME, class_id)
    print(f"There are {len(cards)} elements with class {class_id}")
    time_elapsed(time_start)

    if cards:
        # Find the Transparency Card
        transparency_card = None
        for card in cards:
            p = r'Page transparency'
            if re.match(p, card.text):
                transparency_card = card
                print('Transparency Card found')
                break
        if not transparency_card:
            raise Exception('Transparency Card NOT found')
        time_elapsed(time_start)

        # Get all children of the Transparency Card
        children = transparency_card.find_elements(by=By.CSS_SELECTOR, value='*')
        # Find the "See all" child
        see_all = None
        for child in children:
            if child.text == 'See all':
                see_all = child
                print('"See all" button found')
                break
        if not see_all:
            raise Exception('"See all" button NOT found')
        time_elapsed(time_start)

        # Scroll into view of the "See all" button
        driver.execute_script("arguments[0].scrollIntoView(true);", see_all)
        print('scrolling into view of "See all')
        time.sleep(0.5)

        # Click the "See all" element of the Transparency Card
        action.move_to_element(see_all)
        action.click()
        action.perform()
        print('clicking "See all"')

        # Find the Page Transparency dialog element
        dialog = driver.find_element(by=By.CSS_SELECTOR, value="div[aria-label='Page transparency'][role='dialog']")
        action.move_to_element(dialog)
        action.perform()

        # Check if there is a "See x more" button
        see_more_buttons = dialog.find_elements(
            by=By.CSS_SELECTOR,
            # Element must be a div with an aria-label starting with 'See' and ending with 'More' and role=button
            value="div[aria-label^='See'][aria-label$='More'][role='button']"
        )
        time.sleep(3)
        for button in see_more_buttons:
            driver.execute_script("arguments[0].scrollIntoView(true);", button)
            action.move_to_element(button)
            action.click()
            action.perform()
            print('clicked a "See x More" button')
            time.sleep(3)

        # Parse dialog text to find creation date
        p = r"Created - .*\n(?P<creation_date>.*)\n"
        creation_date = re.search(p, dialog.text).group('creation_date')
        print(creation_date)
        time_elapsed(time_start)

    else:
        print('checking for older page design...')
        card = driver.find_element(by=By.CSS_SELECTOR, value="div[class='_4-u2 _3xaf _7jo_ _4-u8']")
        p = r'Page created - (?P<creation_date>.*)'
        creation_date = re.search(p, card.text).group('creation_date')
        if creation_date:
            print(creation_date)
        else:
            print('creation date not found')
        time_elapsed(time_start)


if __name__ == '__main__':
    main()



