import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
import website_parser_common
import random
import constant

class IndeedSearchData:
    def __init__(self, company_name, company_loc, search_string):
        self.company_name = company_name
        self.company_loc = company_loc
        self.search_string = search_string

class IndeedWebScraper(object):
    # specific classes
    constant.DIV_COMPANY_CARD_CLASS = 'sjcl'
    constant.LOCATION_CLASS = 'location'
    constant.COMPANY_CLASS = 'company'
    constant.NUM_PER_PAGE = 10

    def __init__(self, role, location):
        print('starting a new scraper for indeed with role, location: ', role, location)
        self.role = role
        self.location = location
        self.base_url = self.construct_base_url(role,location)
        self.parser = website_parser_common.WebsiteParser()

    def construct_base_url(self, role, location):
        role_str = "q="+urllib.parse.quote(role)
        loc_str = "l="+urllib.parse.quote(location)
        radius = "radius=15"
        return "https://www.indeed.com/jobs?" + '&'.join([role_str, loc_str, radius])

    def parse_company_cards(self, company_cards):
        card_data = []
        for i, cc in enumerate(company_cards):
            # print(serp_card)
            name, loc = None, None
            name_html = cc.find_all(class_=constant.COMPANY_CLASS)
            name = name_html[0].get_text(' ', strip=True)
            loc_html = cc.find_all(class_=constant.LOCATION_CLASS)
            if loc_html:
                loc = loc_html[0].get_text(' ', strip=True)
                start_paren_idx = loc.find('(')
                if start_paren_idx != -1:
                    loc = loc[:start_paren_idx]
            search_string = name + ((' '+loc) if loc else '')
            info = IndeedSearchData(name, loc, search_string)
            card_data.append(info)
        return card_data

    # get all of the cards from the html file
    def get_cards_per_page(self, url):
        soup = self.parser.get_soup_for_url(url)
        page_cards = soup.find_all(lambda tag: tag.name == 'div' and
                                            tag.get('class') == [ constant.DIV_COMPANY_CARD_CLASS ])
        return page_cards

    # add to the set until you're done
    def do_scrape(self):
        finished, data = None, set()
        url, iteration = self.base_url, 0
        fails, all_infos = 2, []
        while not finished:
            finished = True
            start_param = iteration*constant.NUM_PER_PAGE
            if start_param:
                url = self.base_url+"&start="+str(start_param)
            page_cards = self.get_cards_per_page(url)
            new_info = self.parse_company_cards(page_cards)
            print('searching this url for new info: ', url)
            count = 0
            for info in new_info:
                if info.search_string not in data:
                    count += 1
                    finished = False
                    print('adding new entry', info.search_string)
                    data.add(info.search_string)
                    all_infos.append(info)
            print('adding this many new informations to the output:', count)
            iteration+=1
            # sometimes if we get 0 answers out, if we query again, we'll get new answers
            # so to combat this, we'll only quit out after getting 0 new entries 3 times total
            if finished and fails > 0:
                fails -= 1
                finished = not finished
            sleep(random.randint(3,10))
        return all_infos

    def scrape(self):
        search_infos = []
        infos = self.do_scrape()
        for info in infos:
            search_infos.append(IndeedSearchData(self.role, self.location, info))
        return search_infos

# url = "https://www.indeed.com/jobs?q=Dentist+Associate&l=Chicago%2C+IL"
# web_scraper = IndeedWebScraper('Dental Associate','Chicago, IL')
# web_scraper.scrape()
