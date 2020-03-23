from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from backend.fetch import *
from config.config import URL, UPDATE_INTERVAL
import atexit
from utils.plot_utils import *
from datetime import datetime
from bokeh.layouts import column
from bokeh.resources import INLINE
from bokeh.embed import components
from models.predictive_models import *
from scipy.optimize import curve_fit
from scipy.optimize import fsolve
from models.data import prepare_data
from utils.extra import mongodb_to_dict
from pymongo import MongoClient
from bokeh.document.document import Document

import os

doc = Document()
client = MongoClient(os.environ['MONGODB_URI'])
db = client.get_default_database()

app = Flask(__name__, template_folder="templates", static_folder='static')


def update_models():
    ro_data = mongodb_to_dict(db.cases.find({}))
    indices, confirmed_cases = prepare_data(ro_data)
    logistic_values, _ = curve_fit(logistic_model, indices, confirmed_cases, p0=[2, 58, 100000])
    exponential_values, _ = curve_fit(exponential_model, indices, confirmed_cases, p0=[1, 1, 1])
    a, b, c = logistic_values[0], logistic_values[1], logistic_values[2]
    sol = int(fsolve(lambda x: logistic_model(x, a, b, c) - int(c), b))

    models_params = db.models_params

    result = models_params.update_one({'_id': 1},
                                      {'$set':
                                          {
                                              'logistic_values': list(logistic_values),
                                              'exponential_values': list(exponential_values),
                                              'sol': sol
                                          }
                                      },
                                      upsert=True)


def update_data():
    raw_json = get_raw_json(URL)
    data = get_country_data(raw_json, "Romania")
    _, cases_list = get_country_date_to_cases(data)

    cases = db.cases
    for case in cases_list:
        result = cases.update_one({'_id': case[0]}, {
            '$set': {'confirmed': case[1]['confirmed'], 'deaths': case[1]['deaths'],
                     'recovered': case[1]['recovered']}},
                                  upsert=True)
    last_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db.last_updated.update_one({'_id': 1}, {'$set': {'last_updated': last_updated}}, upsert=True)
    update_models()
    update_plots()


def update_plots():
    ro_data = mongodb_to_dict(db.cases.find({}))
    overlapped_plot = generate_overlap(ro_data, "orange", "red", "green")
    confirmed_cases_plot = generate_plot(ro_data, "confirmed", "orange", "gold")
    deaths_cases_plot = generate_plot(ro_data, "deaths", "salmon", "red")
    recovered_cases_plot = generate_plot(ro_data, "recovered", "yellowgreen", "green")
    col_layout_index = column(overlapped_plot, confirmed_cases_plot, deaths_cases_plot, recovered_cases_plot,
                              sizing_mode="stretch_width")
    script_index, div_index = components(col_layout_index)

    params = db.models_params.find_one({'_id': 1})
    logistic_values = params['logistic_values']
    exponential_values = params['exponential_values']
    sol = params['sol']

    logistic_plot = generate_logistic_exponential_plot(ro_data, sol, logistic_values[0], logistic_values[1],
                                                       logistic_values[2], exponential_values[0], exponential_values[1],
                                                       exponential_values[2])
    col_layout_preds = column(logistic_plot, sizing_mode="stretch_width")
    script_preds, div_preds = components(col_layout_preds)

    db.plots_index.update_one({'_id': 1},
                              {
                                  '$set':
                                      {
                                          'script_index': script_index,
                                          'div_index': div_index
                                      }
                              },
                              upsert=True)

    db.plots_preds.update_one({'_id': 1},
                              {
                                  '$set':
                                      {
                                          'script_preds': script_preds,
                                          'div_preds': div_preds
                                      }
                              },
                              upsert=True)


@app.route("/index")
@app.route("/")
def index():
    plots_index = db.plots_index.find_one({'_id': 1})
    script, div = plots_index['script_index'], plots_index['div_index']
    last_updated = db.last_updated.find_one({'_id': 1})['last_updated']

    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    return render_template("index.html", js_resources=js_resources, css_resources=css_resources, script=script,
                           div=div, last_updated=last_updated)


@app.route("/predictions")
def predictions():
    plots_preds = db.plots_preds.find_one({'_id': 1})
    script, div = plots_preds['script_preds'], plots_preds['div_preds']
    last_updated = db.last_updated.find_one({'_id': 1})['last_updated']
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    return render_template("predictions.html", js_resources=js_resources, css_resources=css_resources, script=script,
                           div=div, last_updated=last_updated)


@app.route("/sources")
def sources():
    last_updated = db.last_updated.find_one({'_id': 1})['last_updated']
    return render_template("sources.html", last_updated=last_updated)


scheduler = BackgroundScheduler()
scheduler.add_job(func=update_data, trigger="interval", hours=UPDATE_INTERVAL)
scheduler.start()

if __name__ == '__main__':
    atexit.register(lambda: scheduler.shutdown())
    update_data()
    app.run()
