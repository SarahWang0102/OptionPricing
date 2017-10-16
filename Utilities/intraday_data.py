from WindPy import w
import pandas as pd
import os
import pickle



intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\sintraday_etf_2017-08-28' + '.json')
print(intraday_etf.index)


print(list(intraday_etf.index))
cont = list(intraday_etf.index)
print(intraday_etf[cont[0]])

