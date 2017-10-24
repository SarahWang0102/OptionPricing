import QuantLib as ql
import pandas as pd
import os
from Utilities.svi_read_data import get_wind_data
import data_access.wind_data as wd
from WindPy import w
from datetime import date,datetime
w.start()

evalDate = ql.Date(22, 8, 2017)
endDate = ql.Date(20, 8, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()


df = wd.get_optionsinfo()
df_option = pd.read_json(os.path.abspath('..') + '\marketdata\optioncontractbasicinfo' + '.json')
#df_option.to_json(os.path.abspath('..') + '\marketdata\wd_options' + '.json')
print(df_option.index)
print(df_option[0])
print(df[0])


