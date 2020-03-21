from bokeh.plotting import figure, ColumnDataSource
from bokeh.resources import CDN
from bokeh.embed import file_html
from bokeh.models.formatters import DatetimeTickFormatter
from bokeh.models import WheelZoomTool, HoverTool
from flask import Markup
from datetime import datetime

TRANSLATION = {
    "confirmed": "Nr. cazuri confirmate",
    "deaths": "Nr. morti",
    "recovered": "Nr. vindecati"
}


def generate_plot(data, type_of_case, line_color, circle_color, plot_name):
    plot = figure(x_axis_type="datetime", x_axis_label="Data", y_axis_label=TRANSLATION[type_of_case])

    xaxis = list(data.keys())
    yaxis = [x[type_of_case] for x in data.values()]
    source = ColumnDataSource({
        'x_axis': xaxis,
        'y_axis': yaxis
    })

    plot.xaxis.formatter = DatetimeTickFormatter(months=["%d/%m/%Y"], days=["%d/%m/%Y"], hours=["%d/%m/%Y"],
                                                 minutes=["%d/%m/%Y"])

    plot.line(source=source, x='x_axis', y='y_axis', color=line_color)
    plot.circle(source=source, x='x_axis', y='y_axis', fill_color=circle_color, size=8)

    plot.add_tools(WheelZoomTool())
    plot.add_tools(
        HoverTool(tooltips=[('Data', '@x_axis{%d/%m/%Y}'), ('Cazuri', '@y_axis')], formatters={"x_axis": "datetime"}))

    return Markup(file_html(plot, CDN, plot_name))
