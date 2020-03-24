from collections import OrderedDict
from datetime import datetime


def mongodb_to_dict(db_result):
    d = OrderedDict()
    for case in db_result:
        date = datetime.strptime(case['_id'], "%d-%m-%y")
        confirmed = case['confirmed']
        deaths = case['deaths']
        d[date] = {'confirmed': confirmed, 'deaths': deaths}
    return d
