from flask import Flask, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from backend.fetch import *
from config.config import *
import atexit
from datetime import datetime, timedelta
from utils.plot_utils import *
from bokeh.layouts import column
from bokeh.resources import INLINE
from bokeh.embed import components
from models.predictive_models import *
from scipy.optimize import curve_fit
from scipy.optimize import fsolve
from models.data import prepare_data
from utils.extra import mongodb_to_dict
from pymongo import MongoClient
import os
from bokeh.models.widgets import Tabs, Panel

client = MongoClient(os.environ['MONGODB_URI'], retryWrites=False)
db = client.get_default_database()

app = Flask(__name__, template_folder="templates", static_folder='static')


def update_models():
    ro_data = mongodb_to_dict(db.cases.find({}))
    indices, confirmed_cases = prepare_data(ro_data)
    logistic_values, _ = curve_fit(logistic_model, indices, confirmed_cases, p0=[3, 60, 50000],
                                   bounds=(0, [5., 365., 1000000]))
    exponential_values, _ = curve_fit(exponential_model, indices, confirmed_cases, p0=[1, 1, 1],
                                      bounds=(0, [5., 365., 1000000]))
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
    data = get_cases(get_big_df(URL_CONFIRMED, URL_DEATHS))
    _, cases_list = get_country_date_to_cases(data)

    cases = db.cases
    for case in cases_list:
        result = cases.update_one({'_id': case[0]}, {
            '$set': {'confirmed': case[1]['confirmed'], 'deaths': case[1]['deaths']}},
                                  upsert=True)
    last_updated = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    db.last_updated.update_one({'_id': 1}, {'$set': {'last_updated': last_updated}}, upsert=True)
    update_models()
    update_plots()


def update_plots():
    ro_data = mongodb_to_dict(db.cases.find({}))

    overlapped_plot = Tabs(tabs=[
        Panel(
            child=column(generate_overlap(ro_data, "orange", "red", 'linear'), sizing_mode="stretch_width"),
            title="Liniar"),
        Panel(child=column(generate_overlap(ro_data, "orange", "red", 'log'), sizing_mode="stretch_width"),
              title="Logaritmic")
    ], sizing_mode="stretch_width")

    confirmed_cases_plot = Tabs(tabs=[
        Panel(
            child=column(generate_plot(ro_data, "confirmed", "orange", "gold", 'linear'), sizing_mode="stretch_width"),
            title="Liniar"),
        Panel(child=column(generate_plot(ro_data, "confirmed", "orange", "gold", 'log'), sizing_mode="stretch_width"),
              title="Logaritmic")
    ], sizing_mode="stretch_width")

    deaths_cases_plot = Tabs(tabs=[
        Panel(
            child=column(generate_plot(ro_data, "deaths", "salmon", "red", 'linear'), sizing_mode="stretch_width"),
            title="Liniar"),
        Panel(child=column(generate_plot(ro_data, "deaths", "salmon", "red", 'log'), sizing_mode="stretch_width"),
              title="Logaritmic")
    ], sizing_mode="stretch_width")

    col_layout_index = column(overlapped_plot, confirmed_cases_plot, deaths_cases_plot,
                              sizing_mode="stretch_width")
    script_index, div_index = components(col_layout_index)

    params = db.models_params.find_one({'_id': 1})
    logistic_values = params['logistic_values']
    exponential_values = params['exponential_values']
    sol = params['sol']

    logistic_plot = generate_logistic_exponential_plot(ro_data, sol, logistic_values[0], logistic_values[1],
                                                       logistic_values[2], exponential_values[0], exponential_values[1],
                                                       exponential_values[2], 'linear')
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
    params = db.models_params.find_one({'_id': 1})
    sol = params['sol']
    c = params['logistic_values'][2]
    end_date = datetime.strptime("22.01.2020", "%d.%m.%Y") + timedelta(sol)
    end_date_str = end_date.strftime("%d.%m.%Y")
    return render_template("predictions.html", js_resources=js_resources, css_resources=css_resources, script=script,
                           div=div, last_updated=last_updated, end_date_str=end_date_str, n_confirmed=int(c))


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
    app.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
