from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import WheelZoomTool, HoverTool
from flask import Markup
from datetime import datetime, timedelta
from models.predictive_models import logistic_model, exponential_model

TRANSLATION = {
    "confirmed": "Nr. cazuri confirmate",
    "deaths": "Nr. morti",
    "recovered": "Nr. vindecati"
}


def generate_plot(data, type_of_case, line_color, circle_color):
    plot = figure(x_axis_type="datetime", y_axis_label=TRANSLATION[type_of_case])

    xaxis = list(data.keys())
    yaxis = [x[type_of_case] for x in data.values()]
    source = ColumnDataSource({
        'x_axis': xaxis,
        'y_axis': yaxis
    })

    plot.xaxis.formatter = DatetimeTickFormatter(months=["%d/%m/%Y"], days=["%d/%m/%Y"], hours=["%d/%m/%Y"],
                                                 minutes=["%d/%m/%Y"])

    plot.line(source=source, x='x_axis', y='y_axis', line_width=3, color=line_color)
    plot.circle(source=source, x='x_axis', y='y_axis', fill_color=circle_color, size=8)

    plot.add_tools(WheelZoomTool())
    plot.add_tools(
        HoverTool(tooltips=[('Data', '@x_axis{%d/%m/%Y}'), ('Cazuri', '@y_axis')], formatters={"x_axis": "datetime"}))

    return plot


def generate_overlap(data, line_color1, line_color2, line_color3):
    plot = figure(x_axis_type="datetime")

    xaxis = list(data.keys())
    yaxis_confirmed = [x["confirmed"] for x in data.values()]
    yaxis_deaths = [x["deaths"] for x in data.values()]
    yaxis_recovered = [x["recovered"] for x in data.values()]

    source = ColumnDataSource({
        'x_axis': xaxis,
        'y_axis_confirmed': yaxis_confirmed,
        'y_axis_deaths': yaxis_deaths,
        'y_axis_recovered': yaxis_recovered

    })

    plot.xaxis.formatter = DatetimeTickFormatter(months=["%d/%m/%Y"], days=["%d/%m/%Y"], hours=["%d/%m/%Y"],
                                                 minutes=["%d/%m/%Y"])
    plot.line(source=source, x='x_axis', y='y_axis_confirmed', color=line_color1, line_width=3, legend="Confirmate")
    plot.line(source=source, x='x_axis', y='y_axis_deaths', color=line_color2, line_width=3, legend="Morti")
    plot.line(source=source, x='x_axis', y='y_axis_recovered', color=line_color3, line_width=3, legend="Vindecati")

    plot.add_tools(WheelZoomTool())

    return plot


def generate_logistic_exponential_plot(data, last_day_number, a_logistic, b_logistic, c_logistic, a_exp, b_exp, c_exp):
    dates = list(data.keys())

    pred_x_range = list(range(0, last_day_number))
    xaxis_real = list(data.keys())
    xaxis_predicted = [dates[0] + timedelta(pred_x) for pred_x in pred_x_range]
    yaxis_real = [x["confirmed"] for x in data.values()]
    yaxis_predicted_logistic = [logistic_model(x, a_logistic, b_logistic, c_logistic) for x in pred_x_range]
    yaxis_predicted_exponential = [exponential_model(x, a_exp, b_exp, c_exp) for x in pred_x_range]

    plot = figure(x_axis_type="datetime", y_axis_label="Nr. cazuri confirmate", y_range=(-100, 1000))

    plot.xaxis.formatter = DatetimeTickFormatter(months=["%d/%m/%Y"], days=["%d/%m/%Y"], hours=["%d/%m/%Y"],
                                                 minutes=["%d/%m/%Y"])

    plot.line(x=xaxis_predicted, y=yaxis_predicted_logistic, line_width=3, color="blue",
              legend="f(x)={:.2f}/(1 + exp(-(x-{:.2f})/{:.2f})".format(c_logistic, b_logistic, a_logistic))
    plot.line(x=xaxis_predicted, y=yaxis_predicted_exponential, line_width=3, color="red",
              legend="f(x)={:.2f}*exp({:.2f}(x-{:.2f}))".format(a_exp, b_exp, c_exp))
    plot.circle(x=xaxis_real, y=yaxis_real, fill_color="orange", size=8, legend="Date reale")
    plot.legend.location = "top_left"
    plot.add_tools(WheelZoomTool())
    return plot
