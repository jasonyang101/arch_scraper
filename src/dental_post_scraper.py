from bs4 import BeautifulSoup
from time import sleep
import requests
import json
import random
import constant
from pprint import pprint
# REQUEST - https://wwwapis.dentalpost.net/api8/users/s%2F767832/jobs?position=DA&zip=60540&type=PERM&radius=30
# [ 'Dentist Associate', 'Registered Dental Hygienist', 'Dental Office Manager', 'Dental Assistant', 'Dental Front Office']
class DentalPostSearchData:
    def __init__(self, company_name, company_loc, search_string):
        self.company_name = company_name
        self.company_loc = company_loc
        self.search_string = search_string

class DentalPostScraper(object):

    constant.role_to_code = {
        'Dental Associate': 'DD', 'Registered Dental Hygienist': 'DH',
        'Dental Office Manager': 'FO', 'Dental Assistant': 'DA'
    }

    constant.city_to_zip = {
        'Chicago, IL': '60616',
        'Naperville, IL': '60540',
        'Oak Lawn, IL': '60453',
        'Des Plaines, IL': '60016'
    }

    constant.headers = {
        'authority': 'wwwapis.dentalpost.net',
        'sec-ch-ua': '"Google Chrome";v="87", " Not;A Brand";v="99", "Chromium";v="87"',
        'accept': 'application/json, text/plain, */*',
        'authorization': 'Bearer eyJhbGciOiJIUzI1NiJ9.eyJzdWIiOiJzLzc2NzgzMiIsInJvbGUiOiJzdGFmZiIsImRlbGVnYXRlZCI6ImZhbHNlIiwibGVnYWN5IjoiZmFsc2UiLCJyZWZyZXNoIjoiNzQzMTM3MzctOWYwOC00Yzg4LTljYTItMDIxOGEzMTU1ZjE5IiwiZXhwIjoxNjEwNzkwMTY2fQ.p6v4o7FHPK13sqzhSb4Jt3mQraARh6_KnIz51MqXr-c',
        'sec-ch-ua-mobile': '?0',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.88 Safari/537.36',
        'origin': 'https://www.dentalpost.net',
        'sec-fetch-site': 'same-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'referer': 'https://www.dentalpost.net/',
        'accept-language': 'en-US,en;q=0.9',
    }

    def __init__(self, role, location):
        self.role = role
        self.location = location
        self.login_payload = { 'username': 'jyang223@illinois.edu', 'password': 'wheezersucks' }
        self.login_headers = { 'content-type': 'application/json' }
        self.login_url = 'https://wwwapis.dentalpost.net/api8/auth/login'

    # def login(self):
    #     payload = { 'username': 'jyang223@illinois.edu', 'password': 'wheezersucks' }
    #     headers = { 'content-type': 'application/json' }
    #     url = 'https://wwwapis.dentalpost.net/api8/auth/login'
    #     session = requests.session()
    #     login = session.post(url, data=json.dumps(payload), headers=headers)
    #     assert login.ok == True
    #     return session

    def do_request(self):
        session = requests.session()
        login = session.post(self.login_url, data=json.dumps(self.login_payload), headers=self.login_headers)
        assert login.ok == True
        print("LOGIN WAS OK")

        role_code = constant.role_to_code[self.role]
        zip_code = constant.city_to_zip[self.location]
        params = (
            ('position', role_code),
            ('zip', zip_code)
        )
        param_url = 'https://wwwapis.dentalpost.net/api8/users/s%2F767832/jobs?position=DD&zip=60521'
        user_jobs_url = 'https://wwwapis.dentalpost.net/api8/users/s%2F767832/jobs'
        r = requests.get('https://wwwapis.dentalpost.net/api8/users/s%2F767832/jobs', headers=constant.headers, params=params)
        assert r.ok == True
        r_json = r.json()
        print(r_json)
        found_jobs = []
        premium_jobs, external_jobs = r_json['premiumJobs'], r_json['externalJobs']
        # if the company is confidential, it won't show the employer/company name
        for job in premium_jobs:
            if job['employerName']:
                new_job = [job['employerName'], job['city'], job['state']]
                found_jobs.append(new_job)
        for job in external_jobs:
            if job['company']:
                new_job = [job['company'], job['city'], job['state']]
                found_jobs.append(new_job)
        return found_jobs

    def do_scrape(self):
        found_jobs = self.do_request()
        all_infos = []
        for job_data in found_jobs:
            company_name = job_data[0]
            company_loc = job_data[1]+', '+job_data[2]
            search_string = company_name + ' ' + company_loc
            print('adding info:', company_name, company_loc, search_string)
            all_infos.append(DentalPostSearchData(company_name, company_loc, search_string))
        return all_infos




scraper = DentalPostScraper('Dental Associate', 'Chicago, IL')
scraper.do_scrape()
