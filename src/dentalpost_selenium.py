from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException
from selenium_driver import SeleniumCommon
from website_parser_common import SearchData
from time import sleep
import constant


class DentalPostScraper(object):
    constant.DRIVER_PATH = '/Users/jasonyang/Documents/personal/arch_dental/arch_scraper/chromedriver'
    constant.CREDENTIALS = { 'username': 'jyang223@illinois.edu', 'password': 'wheezersucks' }
    constant.LOGIN_URL = 'http://www.dentalpost.net/dental-jobs/login/'
    constant.BASE_URL = 'http://www.dentalpost.net/app/search-jobs/'

    constant.role_to_code = {
        'Dentist Associate': 'DD', 'Registered Dental Hygienist': 'DH',
        'Dental Office Manager': 'FO', 'Dental Assistant': 'DA'
    }

    constant.city_to_zip = {
        'Chicago, IL': '60616',
        'Naperville, IL': '60540',
        'Oak Lawn, IL': '60453',
        'Des Plaines, IL': '60016'
    }

    def __init__(self):
        self._driver = SeleniumCommon.get_driver()
        SeleniumCommon.go_to_url(self._driver, constant.LOGIN_URL)
        self.logged_in = self.perform_login()

    def uses_driver(self):
        return True

    def construct_url(self, role, city):
        role_code = constant.role_to_code[role]
        zip_code = constant.city_to_zip[city]
        return constant.BASE_URL+role_code+'/'+zip_code

    def perform_login(self):
        success = True
        login = self._driver.find_element_by_xpath("//input[@name='email']").send_keys(constant.CREDENTIALS['username'])
        password = self._driver.find_element_by_xpath("//input[@name='password']").send_keys(constant.CREDENTIALS['password'])
        submit = self._driver.find_element_by_xpath("//button[@type='submit']").click()
        sleep(10)
        success, _ = SeleniumCommon.contains_element_xpath(self._driver, "//div[@class='dropdown-menu']")
        login_msg = "Successfully logged into DentalPost" if success else  "Failed to login"
        print(login_msg)
        return success

    def parse_current_search_page(self):
        infos = set()
        divs = self._driver.find_elements_by_xpath("//div[@class='px-0 d-flex justify-content-start flex-column pr-0 flex-grow-1 col']")
        for div in divs:
            company_name, company_loc = None, None
            try:
                company_name = div.find_element_by_xpath(".//span[@class='d-block']")
                company_loc = div.find_element_by_xpath(".//span[@class='d-block mb-2']")
            except NoSuchElementException as e:
                found = None
                if company_name:
                    found = company_name.text
                print("Unable to pull data - entry was missing company " + ("location" if found else "name"))
                continue
            infos.add((company_name.text, company_loc.text))
        return list(infos)

    def convert_output(self, name, location):
        if 'IL' not in location:
            return ''
        start_paren_idx = location.find('(')
        if start_paren_idx != -1:
            location = location[:start_paren_idx]
        return ', '.join([name, location])

    def do_scrape(self, role, location):
        if role == 'Dental Front Office':
            print('Dental Front Office and Dental Office Manager are combined on DentalPost')
            return []
        if not self.logged_in:
            return []
        print('')
        print("Starting scrape now")
        url = self.construct_url(role, location)
        SeleniumCommon.go_to_url(self._driver, url)
        print('searching this url for new info: ', url)
        found_infos = self.parse_current_search_page()
        all_infos = []
        failed_searches = []
        for info in found_infos:
            c = self.convert_output(info[0], info[1])
            add_to = all_infos if c else failed_searches
            added = SearchData(info[0], info[1], c) if c else info[0]+', '+info[1]
            add_to.append(added)
        if failed_searches:
            print('failed searches (not in Illinois):')
            print(failed_searches)
        print('')
        print("adding this number of new entries:", len(all_infos))
        for info in all_infos:
            print(info.company_name, info.company_loc, info.search_string)
        return all_infos
#
# scraper = DentalPostScraper()
# out = scraper.do_scrape('Dentist Associate', 'Chicago, IL')
# print(len(out))
