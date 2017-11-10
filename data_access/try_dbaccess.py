import QuantLib as ql
import pandas as pd
import numpy as np
from Utilities.utilities import to_dt_date
import os
from Utilities.svi_read_data import get_wind_data
import data_access.wind_data as wd
from WindPy import w
from datetime import date, datetime
import pickle

w.start()

evalDate = ql.Date(1, 1, 2016)
# evalDate = ql.Date(28, 7, 2017)
endDate = ql.Date(1, 5, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()

evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))

begstr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
endstr = str(endDate.year()) + "-" + str(endDate.month()) + "-" + str(endDate.dayOfMonth())
data = w.wsd("SR.CZC", "trade_hiscode",begstr, endstr, "")
df = pd.DataFrame(data=data.Data[0], index=data.Times)
df.to_json(os.path.abspath('..') + '\marketdata\hiscodes_sr' + '.json')
print(df)


while evalDate < endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    ids = w.wsd("SR.CZC", "trade_hiscode",datestr, datestr, "")
    #print(ids.Data)
    data = w.wsi(ids.Data[0][0], "close", datestr+" 09:00:00", datestr+" 23:31:00", "Fill=Previous")
    print(data.Times)
    #print(data.Data[-1])
    df = pd.DataFrame(data=data.Data[0], index=data.Times)
    df.to_json(os.path.abspath('..') + '\marketdata\intraday_sr_'+datestr + '.json')


'''

diffs = []
stds = []
while evalDate < endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    df = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_m_' + datestr + '.json')

    #print(df.values)
    prices = [v[0] for v in df.values]
    diffs.append(max(prices)-min(prices))
    stds.append(np.std(prices))
    #print(df.values[-1][0])
    #print(max(prices)-min(prices))
    #print(np.std(prices))
print(diffs)
print(sum(diffs)/len(diffs))
print(sum(stds)/len(stds))



evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))

begstr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
endstr = str(endDate.year()) + "-" + str(endDate.month()) + "-" + str(endDate.dayOfMonth())
data = w.wsd("M.DCE", "trade_hiscode",begstr, endstr, "")
df = pd.DataFrame(data=data.Data[0], index=data.Times)
df.to_json(os.path.abspath('..') + '\marketdata\hiscodes_m' + '.json')
df = pd.read_json(os.path.abspath('..') + '\marketdata\hiscodes_m' + '.json')
print(df)
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
a = df.loc[to_dt_date(evalDate),0]
print(a)
'''

