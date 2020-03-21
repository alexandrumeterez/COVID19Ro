import requests
from collections import OrderedDict


def get_raw_json(url):
    response = requests.get(url=url)
    data = response.json()
    return data


def get_country_data(jsonfile, countryname):
    assert countryname in jsonfile, "Wrong country name"
    return jsonfile[countryname]


def get_country_date_to_cases(country_data):
    date_to_cases = OrderedDict()
    cases_list = []
    for entry in country_data:
        confirmed = entry["confirmed"]
        date = entry["date"]

        date_parts = date.split('-')
        year, month, day = date_parts[0], date_parts[1], date_parts[2]
        date = "{}-{}-{}".format(day, month, year)

        deaths = entry["deaths"]
        recovered = entry["recovered"]
        date_to_cases[date] = {"confirmed": confirmed, "deaths": deaths, "recovered": recovered}
        cases_list.append((date, date_to_cases[date]))
    return date_to_cases, cases_list
