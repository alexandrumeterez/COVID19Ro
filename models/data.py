import numpy as np


def prepare_data(data):
    dates, cases = list(data.keys()), list(data.values())
    confirmed_cases = [c['confirmed'] for c in cases]
    indices = [(d - dates[0]).days for d in dates]
    return indices, confirmed_cases


def extract_variances(cov_mat):
    errors = [np.sqrt(cov_mat[i][i]) for i in [0, 1, 2]]
    return errors
