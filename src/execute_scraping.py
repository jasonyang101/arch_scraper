from selenium_driver import SeleniumCommon
from website_parser_common import WebsiteParser
import dentalpost_selenium
import ihire_selenium
import indeed_scraper
import address_search
import constant
import sys
import os

class ScrapeExecutor:
    constant.SEARCH_CITIES = {
        'indeed': ['Chicago, IL', 'Naperville, IL', 'Oak Lawn, IL', 'Des Plaines, IL'],
        'dentalpost': ['Chicago, IL', 'Naperville, IL', 'Oak Lawn, IL', 'Des Plaines, IL'],
        'ihire': ['Schaumburg, IL', 'Chicago, IL', 'Naperville, IL', 'Evanston, IL']
    }
    constant.SEARCH_ROLES = [ 'Dentist Associate', 'Registered Dental Hygienist',
                                'Dental Office Manager', 'Dental Assistant', 'Dental Front Office']
    constant.WEBSITES = {
        'indeed': indeed_scraper.IndeedWebScraper,
        'dentalpost': dentalpost_selenium.DentalPostScraper,
        'ihire': ihire_selenium.iHireScraper }
    constant.results_path = '../results/output.csv'
    constant.stats_path = '../results/stats.txt'
    constant.failures_path = '../results/failed_searches.txt'

    def  __init__(self):
        self.address_searcher = address_search.AddressSearcher()
        self.role_data = {}
        if not os.path.exists('../results'):
            os.mkdir('../results')
        # REFACTOR THIS WHEN WE HAVE MULTIPLE SITES
        if os.path.exists('../results/output.csv'):
            os.remove('../results/output.csv')
        if os.path.exists('../results/stats.txt'):
            os.remove('../results/stats.txt')

    def scrape(self):
        scraper = constant.WEBSITES[self.site]()
        all_infos = set()
        for role in constant.SEARCH_ROLES:
            if (self.site == 'dentalpost'
                    or self.site == 'ihire') and role == 'Dental Front Office':
                continue
            roles = set()
            for city in constant.SEARCH_CITIES[self.site]:
                scraped_info = scraper.do_scrape(role, city)
                scraped_info = set(scraped_info)
                filtered_info = self.filter_excluded_info(scraped_info)
                roles = roles.union(filtered_info)
                # break
            prev_length = len(all_infos)
            self.role_data[role] = roles
            all_infos = all_infos.union(roles)
            print("Total entries found for role: "+role, len(roles))
            print("Number of new (unique) job entries added in for role: "+role, len(all_infos)-prev_length)
            # break
        if scraper.uses_driver():
            SeleniumCommon.end_driver(scraper._driver)
        return all_infos

    # pass in infos from the scrape
    def get_csv_output(self, infos, address_dict):
        csv_output = []
        for info in infos:
            # add name, roles, formatted address
            if info.search_string not in address_dict:
                continue
            roles_for_info = [ role
                for role in constant.SEARCH_ROLES
                if role in self.role_data and info in self.role_data[role] ]
            roles_str = '+'.join(roles_for_info)
            parsed_addr = self.parse_formatted_address(address_dict[info.search_string])
            csv_entry = [info.company_name, roles_str] + parsed_addr + [self.site]
            csv_output.append(csv_entry)
        return csv_output

    def filter_excluded_info(self, infos):
        remove_set = set()
        for info in infos:
            lower_name = info.company_name.lower()
            idx = lower_name.find('+')
            if idx != -1:
                lower_name = lower_name[:idx]
            excluded = [ excl for excl in WebsiteParser.EXCLUSIONS if excl in lower_name ]
            if excluded:
                remove_set.add(info)
        return infos - remove_set

    # example: 519 N Cass Ave Ste 401, Westmont, IL 60559, United States
    def parse_formatted_address(self, addr):
        addr_split = addr.split(',')
        components = list(map(lambda s: s.strip(), addr_split))
        street = components[0]
        # split IL 60559 into [IL, 60559]
        state_zip = components[2].split(' ')
        if len(state_zip) == 1:
            state_zip.append('missing zip')
        city_state = components[1]+' '+state_zip[0]
        return [street, city_state, state_zip[1]]

    def write_results(self, csv_output):
        headers = ['company_name', 'role', 'address', 'city state', 'zip', 'source website']
        headers_str = ', '.join(headers)
        write_data = [headers_str]
        for data in csv_output:
            data = map(lambda s: s.replace(',', '').strip(), data)
            data_str = ', '.join(data)
            write_data.append(data_str)
        self.write_data_to_file(constant.results_path, write_data)

    def write_stats(self, num_entries):
        m = 'a' if os.path.exists(constant.stats_path) else 'w'
        header = "Statistics for site - {site}:".format(site=self.site)
        entries_str = "Total number of unique entries: {num_entries}".format(num_entries=num_entries)
        role_data_str = "For the role {role}, found this number of job entries {entries}"
        role_strs = [ role_data_str.format(role=role, entries=len(self.role_data[role]))
                        for role in self.role_data ]
        write_data = [header, entries_str] + role_strs
        self.write_data_to_file(constant.stats_path, write_data)

    def write_failed_info(self, failed_searches):
        failure_header_str = "For {site}, Google maps search failed to find the address for these companies".format(site=self.site)
        write_data = [failure_header_str] + failed_searches
        self.write_data_to_file(constant.failures_path, write_data)

    def write_data_to_file(self, file_path, write_data):
        m = 'a' if os.path.exists(file_path) else 'w'
        with open(file_path, m) as f:
            for d in write_data:
                d = d+'\n'
                f.write(d)
            if file_path != constant.results_path:
                f.write('\n')
        return

    def after_run(self, num_entries):
        print("Successfully written data output to results/output.csv")
        print("Successfully written stat output to results/stats.txt")
        print("Total number of written entries:", num_entries)

    def search_infos(self, search_infos):
        search_strings = [ info.search_string for info in search_infos ]
        self.address_searcher.set_search_strings(search_strings)
        address_dict, failed_searches = self.address_searcher.run_searches()
        if failed_searches:
            print("Unable to find maps information for these addresses: ")
            print(failed_searches)
            self.write_failed_info(failed_searches)
        return address_dict

    def execute(self, site):
        self.site = site
        all_infos = self.scrape()
        address_dict = self.search_infos(all_infos)
        csv_output = self.get_csv_output(all_infos, address_dict)
        num_entries = len(csv_output)
        self.write_results(csv_output)
        self.write_stats(num_entries)
        self.after_run(num_entries)

if __name__ == '__main__':
    args = sys.argv[1:]
    if not args:
        print("Missing parameter for which websites to use")
        exit()
    accepted_params = ['indeed', 'dentalpost', 'ihire', 'all']
    if any([arg not in accepted_params for arg in args]):
        print("Unknown parameter found. Fix the parameters")
        exit()
    sites = args
    if args[0] == 'all':
        sites = ['indeed', 'dentalpost', 'ihire']
    executor = ScrapeExecutor()
    for site in sites:
        executor.execute(site)
