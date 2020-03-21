from backend.fetch import *
from config.config import URL
from pprint import pprint

if __name__ == '__main__':
    data = get_raw_json(URL)
    date_to_cases, cases_list = get_country_date_to_cases(get_country_data(data, "Romania"))
    pprint(cases_list)