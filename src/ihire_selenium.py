from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium_driver import SeleniumCommon
from time import sleep
import constant

# Sample URL
# 'https://www.ihiredental.com/search?City=Chicago&State=IL&ctname=Dental%20Assistant&ct=253&loc=Chicago%2C%20IL&IsFromSerp=True&CareerTitleIds=253#!/search/c=&k=&loc=Chicago,%20IL&p=2&o=14&d=25&st=page&ct=253'

class iHireSearchData:
    def __init__(self, company_name, company_loc, search_string):
        self.company_name = company_name
        self.company_loc = company_loc
        self.search_string = search_string

# Could pull this out and make it more modular by having a parent selenium driver class.. but this is easier.
class iHireScraper(object):
    constant.DRIVER_PATH = '/Users/jasonyang/Documents/personal/arch_dental/arch_scraper/chromedriver'
    constant.CREDENTIALS = { 'username': 'jyang223@illinois.edu', 'password': 'wheezersucks' }
    constant.LOGIN_URL = 'https://www.ihiredental.com/jobseeker/account/signin?redir=%2Fcareeradvice'

    def __init__(self):
        print("Creating webdriver for iHire")
        self._driver = SeleniumCommon.get_driver()
        SeleniumCommon.go_to_url(self._driver, constant.LOGIN_URL)
        self.logged_in = self.perform_login()

    def perform_login(self):
        success = True
        # has a single box for the login email. Need to submit that, then enter password
        login = self._driver.find_element_by_xpath("//input[@name='EmailAddress']").send_keys(constant.CREDENTIALS['username'])
        submit = self._driver.find_element_by_xpath("//button[@type='submit' and @class='btn btn-link']").click()
        sleep(10)
        try:
            self._driver.find_element_by_xpath("//input[@name='Password']").send_keys(constant.CREDENTIALS['password'])
            submit = self._driver.find_element_by_xpath("//button[@type='submit']").click()
        except NoSuchElementException as e:
            success = False
        if not success:
            print("Failed to find the password page. Exiting login..")
            return success
        sleep(10)
        success = SeleniumCommon.ensure_login_successful(self._driver, "//a[@class='dropdown-toggle communities']")
        login_msg = "Successfully logged into iHire" if success else "Failed to login to iHire"
        print(login_msg)
        return success

    

scraper = iHireScraper()
