from urllib.request import urlopen
import urllib
from bs4 import BeautifulSoup


class WebsiteParser:
    def get_soup_for_url(self, url):
        try:
            page = urlopen(url)
        except urllib.error.HTTPError as e:
            print("GOT HTTP ERROR")
            raise

        html_bytes = page.read()
        html = html_bytes.decode('utf-8')
        return BeautifulSoup(html, 'html.parser')
