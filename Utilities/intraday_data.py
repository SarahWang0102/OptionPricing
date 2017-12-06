from WindPy import w
import pandas as pd
import os
import pickle


#w.start()
df = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_2017-08-11' + '.json')


print(df)

