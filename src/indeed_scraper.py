import urllib
from urllib.request import urlopen
from bs4 import BeautifulSoup
from time import sleep
from website_parser_common import SearchData
import website_parser_common
import random
import constant

class IndeedWebScraper(object):
    # specific classes
    # Deprecated: constant.DIV_COMPANY_CARD_CLASS = 'sjcl'
    constant.TABLE_CLASS = 'jobCard_mainContent'
    constant.LOCATION_CLASS = 'companyLocation'
    constant.COMPANY_CLASS = 'companyName'
    constant.NUM_PER_PAGE = 10

    def __init__(self):
        print('starting a new scraper for indeed')
        self.parser = website_parser_common.WebsiteParser()

    def uses_driver(self):
        return False

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
            info = SearchData(name, loc, search_string)
            card_data.append(info)
        return card_data

    # get all of the cards from the html file
    def get_cards_per_page(self, url):
        soup = self.parser.get_soup_for_url(url)

        page_cards = soup.find_all(lambda tag: tag.name == 'table' and
                                            tag.get('class') == [ constant.TABLE_CLASS ])
        print("Found page_cards - num:", len(page_cards))
        return page_cards

    # add to the set until you're done
    def do_scrape(self, role, location):
        print("Beginning scrape for role", role, "location", location)
        finished, data = None, set()
        base_url, iteration = self.construct_base_url(role, location), 0
        fails, all_infos = 2, []
        while not finished:
            finished = True
            start_param = iteration*constant.NUM_PER_PAGE
            url = base_url
            if start_param:
                url += "&start="+str(start_param)
            page_cards = self.get_cards_per_page(url)
            new_info = self.parse_company_cards(page_cards)
            print()
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
            sleep(random.randint(4,10))
        return all_infos

# url = "https://www.indeed.com/jobs?q=Dentist+Associate&l=Chicago%2C+IL"
# web_scraper = IndeedWebScraper('Dental Associate','Chicago', 'IL')
# web_scraper.scrape()
