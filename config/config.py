import numpy as np

UPDATE_INTERVAL = 1
URL_CONFIRMED = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_confirmed_global.csv"
URL_DEATHS = "https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/csse_covid_19_time_series/time_series_covid19_deaths_global.csv"
ENVIRONMENT = "DEPLOY"
POPULATION = 19271233

LOG_BOUNDS = ((0, 0, 0), (np.inf, 3, POPULATION * 0.8))
EXP_BOUNDS = ((0, 0.0, 0.0), (np.inf, 3, np.inf))
