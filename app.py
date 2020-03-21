from flask import Flask
from apscheduler.schedulers.background import BackgroundScheduler
from backend.fetch import *
from config.config import URL, UPDATE_INTERVAL
import atexit
from datetime import datetime

app = Flask(__name__)

ro_data = {}
last_updated = ""
ro_data["last_updated"] = last_updated


def update_data():
    global ro_data, last_updated
    raw_json = get_raw_json(URL)
    data = get_country_data(raw_json, "Romania")
    ro_data, _ = get_country_date_to_cases(data)
    last_updated = datetime.now().strftime("%H:%M:%S")
    ro_data["last_updated"] = last_updated


@app.route("/")
def index():
    return ro_data


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", seconds=UPDATE_INTERVAL)
scheduler.start()

if __name__ == '__main__':
    atexit.register(lambda: scheduler.shutdown())
    app.run()
