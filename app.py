from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from backend.fetch import *
from config.config import URL, UPDATE_INTERVAL
import atexit
from utils.plot_utils import generate_plot
from datetime import datetime

app = Flask(__name__)

ro_data = {}
last_updated = ""


def update_data():
    global ro_data, last_updated
    raw_json = get_raw_json(URL)
    data = get_country_data(raw_json, "Romania")
    ro_data, _ = get_country_date_to_cases(data)
    last_updated = datetime.now().strftime("%H:%M:%S")


@app.route("/")
def confirmed():
    confirmed_cases_plot = generate_plot(ro_data, "confirmed", "blue", "red", "confirmed_cases_plot")
    return confirmed_cases_plot


@app.route("/morti")
def deaths():
    confirmed_cases_plot = generate_plot(ro_data, "deaths", "blue", "red", "confirmed_cases_plot")
    return confirmed_cases_plot


@app.route("/vindecati")
def recovered():
    confirmed_cases_plot = generate_plot(ro_data, "recovered", "blue", "red", "confirmed_cases_plot")
    return confirmed_cases_plot


#
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=update_data, trigger="interval", seconds=UPDATE_INTERVAL)
# scheduler.start()

if __name__ == '__main__':
    # atexit.register(lambda: scheduler.shutdown())
    update_data()
    app.run(debug=True)
