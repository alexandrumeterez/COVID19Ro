from flask import Flask, Markup, render_template
from apscheduler.schedulers.background import BackgroundScheduler
from backend.fetch import *
from config.config import URL, UPDATE_INTERVAL
import atexit
from utils.plot_utils import generate_plot, generate_overlap
from datetime import datetime
from bokeh.layouts import column
from bokeh.resources import INLINE

from bokeh.embed import file_html, components
from bokeh.resources import CDN

app = Flask(__name__, template_folder="templates")

ro_data = {}
last_updated = ""


def update_data():
    global ro_data, last_updated
    raw_json = get_raw_json(URL)
    data = get_country_data(raw_json, "Romania")
    ro_data, _ = get_country_date_to_cases(data)
    last_updated = datetime.now().strftime("%H:%M:%S")


@app.route("/")
def index():
    overlapped_plot = generate_overlap(ro_data, "orange", "red", "green")
    confirmed_cases_plot = generate_plot(ro_data, "confirmed", "orange", "gold")
    deaths_cases_plot = generate_plot(ro_data, "deaths", "salmon", "red")
    recovered_cases_plot = generate_plot(ro_data, "recovered", "yellowgreen", "green")
    col_layout = column(overlapped_plot, confirmed_cases_plot, deaths_cases_plot, recovered_cases_plot,
                        sizing_mode="stretch_width")
    script, div = components(col_layout)
    js_resources = INLINE.render_js()
    css_resources = INLINE.render_css()
    return render_template("index.html", js_resources=js_resources, css_resources=css_resources, script=script, div=div)


#
# scheduler = BackgroundScheduler()
# scheduler.add_job(func=update_data, trigger="interval", seconds=UPDATE_INTERVAL)
# scheduler.start()

if __name__ == '__main__':
    # atexit.register(lambda: scheduler.shutdown())
    update_data()
    app.run(debug=True)
