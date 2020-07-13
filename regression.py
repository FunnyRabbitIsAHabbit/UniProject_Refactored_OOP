"""

Uni project

Developer: Stanislav Alexandrovich Ermokhin

"""


import statsmodels.api as sm
# import pmdarima as pm
import pandas as pd
import json

from statsmodels.tsa.arima_model import ARIMA
from datetime import datetime


def linear_model(name_data, ts_data_dep, ts_data_indep):
    """

    :param name_data: str
    :param ts_data_dep: pandas.DataFrame
    :param ts_data_indep: pandas.DataFrame
    :return: results_filename str, data dict {year: value}
    """

    now = str(datetime.now().timestamp())
    filename = 'models/LINEAR_model_' + name_data + now[:now.find('.')] + '.txt'

    ts_data_indep = sm.add_constant(ts_data_indep)
    reg = sm.OLS(ts_data_dep, ts_data_indep)
    model_fit = reg.fit()
    results = model_fit.summary()

    with open(filename, 'w') as a:
        a.write(str(results))

    df = pd.DataFrame(ts_data_dep.items(), columns=['multi_index', 'value'])
    year = df['multi_index'][0][1]
    df['year'] = [int(year) + i for i in range(len(df.index))]
    df = df.drop(columns=['multi_index'], axis=1)
    dic = df.to_dict('index')
    nd = {dic[key]['year']: float(dic[key]['value'])
          for key in dic}

    json_filename = 'models/LINEAR_model_' + name_data + now[:now.find('.')] + '.json'
    with open(json_filename, 'w') as a:
        json.dump(nd, a)

    return filename, nd


def arima_model(name_data, ts_data, p=None, d=None, q=None, prdct=None):
    """

    :param name_data: str
    :param ts_data: array like object
    :param p: str or None
    :param d: str or None
    :param q: str or None
    :param prdct: int or None
    :return: results_filename str,
    data dict {year: value},
    predicted data dict {year: value}
    """

    try:
        p = int(p)
        d = int(d)
        q = int(q)

        model_fit = ARIMA(ts_data, order=(p, d, q)).fit()
        model_data = model_fit._results.data.__dict__

        ddic = model_data['orig_endog'].items()
        df = pd.DataFrame(ddic, columns=['multi_index', 'value'])
        year = df['multi_index'][0][1]
        df['year'] = [int(year) + i for i in range(len(df.index))]
        df = df.drop(columns=['multi_index'], axis=1)
        dic = df.to_dict('index')
        year_since = int(df['year'].tail(1))
        forec = model_fit.forecast(steps=prdct)
        prediction = forec[0]
        nd = {dic[key]['year']: float(dic[key]['value'])
              for key in dic}

        predictions = {year_since + i: float(prediction[i-1])
                       for i in range(1, len(prediction)+1)}
        results = model_fit.summary()
        now = str(datetime.now().timestamp())
        filename = 'models/ARIMA_model_' + name_data + now[:now.find('.')] + '.txt'

        with open(filename, 'w') as a:
            a.write(str(results))

        json_filename = 'models/ARIMA_model_' + name_data + now[:now.find('.')] + '.json'
        nd.update(predictions)
        with open(json_filename, 'w') as a:
            json.dump(nd, a)

        return filename, nd, predictions

    except Exception as error:
        return error, dict(), dict()
