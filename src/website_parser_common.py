from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup

class SearchData:
    def __init__(self, company_name, company_loc, search_string):
        self.company_name = company_name
        self.company_loc = company_loc
        self.search_string = search_string

    def __hash__(self):
        return hash((self.company_name, self.company_loc, self.search_string))

    def __eq__(self, other):
        if not isinstance(other, type(self)):
            return False
        return self.company_name == other.company_name and \
                self.company_loc == other.company_loc and self.search_string == other.search_string

class WebsiteParser:
    EXCLUSIONS = ['aspen', 'united dental', 'destiny dental', 'webster dental', 'confidential']

    def get_soup_for_url(self, url):
        try:
            page = urlopen(url)
        except urllib.error.HTTPError as e:
            print("GOT HTTP ERROR")
            raise

        html_bytes = page.read()
        html = html_bytes.decode('utf-8')
        return BeautifulSoup(html, 'html.parser')
