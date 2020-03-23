from collections import OrderedDict
from datetime import datetime


def mongodb_to_dict(db_result):
    d = OrderedDict()
    for case in db_result:
        date = datetime.strptime(case['_id'], "%d-%m-%Y")
        confirmed = case['confirmed']
        deaths = case['deaths']
        recovered = case['recovered']
        d[date] = {'confirmed': confirmed, 'deaths': deaths, 'recovered': recovered}
    return d
