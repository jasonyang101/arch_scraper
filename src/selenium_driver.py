from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from time import sleep
import constant

class SeleniumCommon:
    @classmethod
    def go_to_url(cls, driver, url):
        driver.get(url)
        sleep(10)

    @classmethod
    def get_driver(cls):
        options = Options()
        options.headless = True
        options.add_argument("--window-size=1920,1200")
        return webdriver.Chrome(options=options, executable_path=constant.DRIVER_PATH)

    @classmethod
    def end_driver(cls, driver):
        driver.quit()

    @classmethod
    def contains_element_xpath(cls, driver, x_path):
        success, elem = True, None
        try:
            elem = driver.find_element_by_xpath(x_path)
        except NoSuchElementException as e:
            success = False
        return success, elem
