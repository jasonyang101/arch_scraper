import requests
from pprint import pprint
import urllib
import constant
# https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Museum%20of%20Contemporary%20Art%20Australia&inputtype=textquery&fields=photos,formatted_address,name,rating,opening_hours,geometry&key=YOUR_API_KEY


class AddressSearcher:
    constant.ADDR = 'formatted_address'
    constant.CANDIDATES = 'candidates'

    def __init__(self, search_strings=[]):
        api_key_file = open('../creds/google_api_key.txt')
        self.api_key = api_key_file.read()
        self.search_strings = search_strings

    def set_search_strings(self, search_strings):
        self.search_strings = search_strings

    def construct_url(self, search_string):
        url = [ 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?' ]
        params = {
            'input': urllib.parse.quote(search_string),
            'inputtype': 'textquery',
            'fields': 'formatted_address',
            'key': self.api_key
        }
        for param, param_val in params.items():
            url.append(param+'='+param_val)
        return '&'.join(url)

    # leaving this here but unsure if it will be used
    def text_search_url(self, search_string):
        url = [ 'https://maps.googleapis.com/maps/api/place/textsearch/json?' ]
        params = {
            'query': urllib.parse.quote(search_string),
            'key': self.api_key
        }
        for param, param_val in params.items():
            url.append(param+'='+param_val)
        return '&'.join(url)

    def run_searches(self):
        search_output = {}
        failed_searches = []
        for search in self.search_strings:
            find_place_url = self.construct_url(search)
            print('querying from', find_place_url)
            r = requests.get(find_place_url)
            response_json = r.json()
            if response_json['status'] != 'OK':
                failed_searches.append(search)
                continue
            # pull the best candidate
            candidates = response_json['candidates']
            addr = candidates[0]['formatted_address']
            search_output[search] = addr
        return (search_output, failed_searches)




# find_place_url = construct_url('Healthy Smiles of La Grange La Grange, IL 60525')
# sample = "Healthy Smiles of La Grange La Grange, IL 60525"
# address_search = AddressSearcher([sample])
# address_search.run_searches()
