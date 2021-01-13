from urllib.request import urlopen
from bs4 import BeautifulSoup

class IndeedData:
    def __init__(self, company_name, company_loc):
        self.name = company_name
        self.loc = company_loc

class IndeedWebScraper(object):
    def __init__(self, url):
        page = urlopen(url)
        html_bytes = page.read()
        html = html_bytes.decode('utf-8')
        soup = BeautifulSoup(html, 'html.parser')
        company_cards = soup.find_all(lambda tag: tag.name == 'div' and
                                           tag.get('class') == ['sjcl'])
        self.data = self.parse_company_cards(company_cards)

    def parse_company_cards(self, company_cards):
        card_data = []
        print(len(company_cards))
        for i, cc in enumerate(company_cards):
            # print(serp_card)
            name, loc = None, None
            name_html = cc.find_all(class_='company')
            name = name_html[0].get_text(' ', strip=True)
            div_loc = "location"
            loc_html = cc.find_all(class_='location')
            if loc_html:
                loc = loc_html[0].get_text(' ', strip=True)
            card_data.append(IndeedData(name, loc))
        for c in card_data:
            print(c.name, c.loc)
        return card_data


url = "https://www.indeed.com/jobs?q=Dentist+Associate&l=Chicago%2C+IL"
web_scraper = IndeedWebScraper(url)
