import pandas as pd
import os
import QuantLib as ql
import datetime
from Utilities import svi_prepare_vol_data as vol_data

calendar = ql.China()
evalDate = ql.Date(12,5,2017)
datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())

spotmkt = pd.read_json('marketdata\sr_future_mkt_' + datestr + '.json')
print(spotmkt)
print(spotmkt.index)
