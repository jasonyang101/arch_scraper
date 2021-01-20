from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium_driver import SeleniumCommon
from time import sleep
import urllib
import constant

# Sample URL
# 'https://www.ihiredental.com/search?City=Chicago&State=IL&ctname=Dental%20Assistant&ct=253&loc=Chicago%2C%20IL&IsFromSerp=True&CareerTitleIds=253#!/search/c=&k=&loc=Chicago,%20IL&p=2&o=14&d=25&st=page&ct=253'
# Chicago, IL
# Naperville, IL
# Evanston, IL
# Schaumburg, IL
# Could pull this out and make it more modular by having a parent selenium driver class.. but this is easier.
# Dental Assistant:
# https://www.ihiredental.com/search?ct=0&d=25&loc=Schaumburg%2C%20IL#!/search/c=&k=&loc=Schaumburg,%20IL&p=1&o=14&d=25&st=new&ct=253
# https://www.ihiredental.com/candidate/jobs/search/?ct=0&d=25&loc=Schaumburg%2c+IL#!/search/k=&loc=Schaumburg,%20IL&p=1&o=14&d=25&st=page&ct=253
# https://www.ihiredental.com/candidate/jobs/search/?ct=0&d=25&loc=Schaumburg%2C%20IL#!/search/c=&k=&loc=Schaumburg%2C%20IL&p=1&o=14&d=25&st=new&ct=242
# Dental Hygenist:
# https://www.ihiredental.com/search?ct=0&d=25&loc=Schaumburg%2C%20IL#!/search/c=&k=&loc=Schaumburg,%20IL&p=1&o=14&d=25&st=new&ct=254
# Dental Associate:
# https://www.ihiredental.com/search?ct=0&d=25&loc=Schaumburg%2C%20IL#!/search/c=&k=&loc=Schaumburg,%20IL&p=1&o=14&d=25&st=new&ct=242
# Front Office:
# https://www.ihiredental.com/search?ct=0&d=25&loc=Schaumburg%2C%20IL#!/search/c=&k=&loc=Schaumburg,%20IL&p=1&o=14&d=25&st=new&ct=245

class iHireSearchData:
    def __init__(self, company_name, company_loc, search_string):
        self.company_name = company_name
        self.company_loc = company_loc
        self.search_string = search_string


class iHireScraper(object):
    constant.DRIVER_PATH = '/Users/jasonyang/Documents/personal/arch_dental/arch_scraper/chromedriver'
    constant.CREDENTIALS = { 'username': 'jyang223@illinois.edu', 'password': 'wheezersucks' }
    constant.LOGIN_URL = 'https://www.ihiredental.com/jobseeker/account/signin?redir=%2Fcareeradvice'
    constant.BASE_URL = "https://www.ihiredental.com/candidate/jobs/search/?ct=0&d=25&loc={location}#!/search/c=&k=&loc={location}&p={page}&o=14&d=25&st=page&ct={job_code}"

    constant.role_to_code = {
        'Dentist Associate': '242', 'Registered Dental Hygienist': '254',
        'Dental Office Manager': '245', 'Dental Assistant': '253'
    }


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
        sleep(5)
        success = SeleniumCommon.ensure_login_successful(self._driver, "//a[@class='dropdown-toggle communities']")
        login_msg = "Successfully logged into iHire" if success else "Failed to login to iHire"
        print(login_msg)
        return success

    def construct_url(self, role, city, page_num):
        code = constant.role_to_code[role]
        loc = urllib.parse.quote(city)
        return constant.BASE_URL.format(location=loc, page=str(page_num), job_code=code)

    def parse_current_search_page_table(self, page_num):
        print('parsing for tables')
        infos = set()
        try:
            tables = self._driver.find_elements_by_xpath("//table[@class='wide']")
        except NoSuchElementException as e:
            print("Unable to find any entries. Finished on page_number", page_num)
            return []
        for table in tables:
            company_name, company_loc = None, None
            try:
                company_name = table.find_element_by_xpath(".//span[@class='company']")
                company_loc = table.find_element_by_xpath(".//span[@class='location']")
            except NoSuchElementException as e:
                print("Unable to pull data - entry is missing company info")
                continue
            infos.add((company_name.text, company_loc.text))
        for info in infos:
            print("Found info {name} {loc}".format(name=info[0], loc=info[1]))
        return list(infos)

    def parse_current_search_page_div(self, page_num):
        print('parsing for divs')
        infos = set()
        try:
            divs = self._driver.find_elements_by_xpath("//div[@class='col-xs-12']")
        except NoSuchElementException as e:
            print("Unable to find any entries. Finished on page_number", page_num)
            return []
        # parse through the divs
        for div in divs:
            company_name, company_loc = None, None
            try:
                company_name = div.find_element_by_xpath(".//span[@class='company']")
                company_loc = div.find_element_by_xpath(".//span[contains(@data-bind, 'text: City')]")
                company_state = div.find_element_by_xpath(".//span[@data-bind='text: State']")
            except NoSuchElementException as e:
                print("Unable to pull data - entry is missing company info")
                continue
            loc = company_loc.text+' '+company_state.text
            if company_name.text:
                infos.add((company_name.text, loc))
        for info in infos:
            print("Found a new entry {name} {loc}".format(name=info[0], loc=info[1]))
        return list(infos)

    def parse_initial_button(self):
        success = True
        try:
            submit = self._driver.find_element_by_xpath("//button[@id='end-button']").click()
        except NoSuchElementException as e:
            success = False
        msg = "Found and clicked initial got it button" if success else "Unable to find the got it button (may be unnecessary)"
        print(msg)
        if success:
            sleep(5)
        return success

    def do_scrape(self, role, location):
        if role == 'Dental Front Office':
            print('Dental Front Office and Dental Office Manager are combined on iHire')
            return []
        if not self.logged_in:
            return []

        output = []
        print('Starting scrape now')
        finished, page_num = False, 1
        initial_button = False
        while not finished:
            url = self.construct_url(role, location, page_num)
            print()
            print('searching this url for new info:', url)
            print()
            SeleniumCommon.go_to_url(self._driver, url)
            if not initial_button:
                success = self.parse_initial_button()
                initial_button = True
            print("beginning parsing method #1:")
            curr = self.parse_current_search_page_table(page_num)
            if not curr:
                print("beginning parsing method #2:")
                curr = self.parse_current_search_page_div(page_num)
            if not curr: break
            output += curr
            page_num += 1
        print('finished with role, location:', role, location)
        print('found this number of entries', len(output))
        return output

scraper = iHireScraper()
cities = ['Schaumburg, IL', 'Chicago, IL', 'Naperville, IL', 'Evanston, IL']
roles = ['Dentist Associate', 'Registered Dental Hygienist', 'Dental Office Manager', 'Dental Assistant']
final = set()
for role in roles:
    for city in cities:
        output = scraper.do_scrape(role, city)
        output_s = set(output)
        final = final.union(output_s)
print(len(final))
for info in final:
    print(info)

scraper.do_scrape('Dentist Associate', 'Schaumburg, IL')
SeleniumCommon.end_driver(scraper._driver)
