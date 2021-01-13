import requests
from pprint import pprint
from google import google
# https://maps.googleapis.com/maps/api/place/findplacefromtext/json?input=Museum%20of%20Contemporary%20Art%20Australia&inputtype=textquery&fields=photos,formatted_address,name,rating,opening_hours,geometry&key=YOUR_API_KEY

api_key_file = open('../creds/google_api_key.txt')
api_key = api_key_file.read()

def construct_url(search_string):
    url = [ 'https://maps.googleapis.com/maps/api/place/findplacefromtext/json?' ]
    params = {
        'query': search_string.replace(' ', '%20'),
        'inputtype': 'textquery',
        'fields': 'formatted_address',
        'key': api_key
    }
    for param, param_val in params.items():
        url.append(param+'='+param_val)
    return '&'.join(url)


def text_search_url(search_string):
    url = [ 'https://maps.googleapis.com/maps/api/place/textsearch/json?' ]
    params = {
        'query': search_string.replace(' ', '+'),
        # 'inputtype': 'textquery',
        # 'fields': 'formatted_address',
        'key': api_key
    }
    for param, param_val in params.items():
        url.append(param+'='+param_val)
    return '&'.join(url)

# find_place_url = construct_url('Healthy Smiles of La Grange La Grange, IL 60525')
sample = "Healthy Smiles of La Grange La Grange, IL 60525"
text_search_url = text_search_url(sample)
search_results = google.search(sample, num_page)
r = requests.get(text_search_url)
pprint(r.json())
