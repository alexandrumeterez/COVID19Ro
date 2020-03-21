import requests
from collections import OrderedDict
from datetime import datetime


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

        # datetime_obj = datetime.strptime(date, "%y-%m-%d")

        date_parts = date.split('-')
        year = date_parts[0]
        month = date_parts[1]
        if len(month) == 1:
            month = "0" + month
        day = date_parts[2]
        if len(day) == 1:
            day = "0" + day
        date = "{}-{}-{}".format(day, month, year)
        datetime_obj = datetime.strptime(date, "%d-%m-%Y")
        deaths = entry["deaths"]
        recovered = entry["recovered"]
        date_to_cases[datetime_obj] = {"confirmed": confirmed, "deaths": deaths, "recovered": recovered}
        cases_list.append((date, date_to_cases[datetime_obj]))
    return date_to_cases, cases_list
