import requests
from collections import OrderedDict
from datetime import datetime
import pandas as pd


def csv_to_dataframe_data(url):
    df = pd.read_csv(url)
    df = df.loc[df['Country/Region'] == 'Romania']
    df = df.drop(df.columns[0:4], axis=1)
    df.columns = df.columns.str.replace("/", ".")
    return df


def get_big_df(url_confirmed, url_deaths):
    df_confirmed = csv_to_dataframe_data(url_confirmed)
    df_deaths = csv_to_dataframe_data(url_deaths)
    df = pd.concat([df_confirmed, df_deaths], ignore_index=True)
    df = df.rename(index={0: 'confirmed', 1: 'deaths'})
    return df


def get_cases(df):
    confirmed = df.loc['confirmed'].values
    deaths = df.loc['deaths'].values
    c_and_d = list(zip(confirmed, deaths))
    dates = df.columns.values
    return list(zip(dates, c_and_d))


def get_country_date_to_cases(country_data):
    date_to_cases = OrderedDict()
    cases_list = []
    for entry in country_data:
        date = entry[0]
        date_parts = date.split('.')
        year = date_parts[2]
        month = date_parts[0]
        if len(month) == 1:
            month = "0" + month
        day = date_parts[1]
        if len(day) == 1:
            day = "0" + day
        date = "{}-{}-{}".format(day, month, year)
        datetime_obj = datetime.strptime(date, "%d-%m-%y")
        confirmed = entry[1][0]
        deaths = entry[1][1]
        date_to_cases[datetime_obj] = {"confirmed": int(confirmed), "deaths": int(deaths)}
        cases_list.append((date, date_to_cases[datetime_obj]))
    return date_to_cases, cases_list
