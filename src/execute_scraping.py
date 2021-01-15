import indeed_scraper
import address_search
import constant
import os

class ScrapeExecutor:
    constant.SEARCH_CITIES = ['Chicago, IL', 'Naperville, IL', 'Oak Lawn, IL', 'Des Plaines, IL']
    constant.SEARCH_ROLES = [ 'Dentist Associate', 'Registered Dental Hygienist',
                                'Dental Office Manager', 'Dental Assistant', 'Dental Front Office']
    constant.WEBSITES = {'indeed': indeed_scraper.IndeedWebScraper }
    constant.results_path = '../results/output.csv'

    def  __init__(self, site):
        self.address_searcher = address_search.AddressSearcher()
        self.role_data = {}
        self.site = site
        if not os.path.exists('../results'):
            os.mkdir('../results')


    def scrape(self):
        all_infos = set()
        for role in constant.SEARCH_ROLES:
            roles = set()
            for city in constant.SEARCH_CITIES:
                scraper = constant.WEBSITES[self.site](role, city)
                scraped_info = scraper.do_scrape()
                scraped_info = set(scraped_info)
                roles = roles.union(scraped_info)
                break
            prev_length = len(all_infos)
            self.role_data[role] = roles
            all_infos = all_infos.union(roles)
            print("Total unique entries found for role: "+role, len(roles))
            print("Number of new unique elements found for role: "+role, len(all_infos)-prev_length)
            break

        for info in all_infos:
            print(info.search_string)
        print("Total number of unique elements found in the search: ", len(all_infos))
        return all_infos

    # pass in infos from the scrape
    def get_csv_output(self, infos, address_dict):
        csv_output = []
        for info in infos:
            # add name, roles, formatted address
            if info.search_string not in address_dict:
                continue
            roles_for_info = [ role for role in constant.SEARCH_ROLES if role in self.role_data and info in self.role_data[role] ]
            roles_str = '+'.join(roles_for_info)
            csv_output.append( [info.company_name, roles_str, address_dict[info.search_string]] )
        return csv_output

    def write_data(self, csv_output):
        m = 'a' if os.path.exists(constant.results_path) else 'w'
        with open(constant.results_path, m) as f:
            for data in csv_output:
                data = map(lambda s: s.strip(), data)
                data_str = ', '.join(data) + '\n'
                f.write(data_str)

    def after_run(self, csv_output):
        print("Successfully written to results/output.csv")
        print("Total number of written entries:", len(csv_output))

    def search_infos(self, search_infos):
        search_strings = [ info.search_string for info in search_infos ]
        self.address_searcher.set_search_strings(search_strings)
        address_dict, failed_searches = self.address_searcher.run_searches()
        if failed_searches:
            print("Unable to find maps information for these addresses: ")
            print(failed_searches)
        return address_dict

    def execute(self):
        all_infos = self.scrape()
        address_dict = self.search_infos(all_infos)
        csv_output = self.get_csv_output(all_infos, address_dict)
        self.write_data(csv_output)
        self.after_run(csv_output)

if __name__ == '__main__':
    executor = ScrapeExecutor('indeed')
    all_infos = executor.execute()
