import QuantLib as ql
import pandas as pd
import os
from Utilities.svi_read_data import get_wind_data
import data_access.wind_data as wd
from WindPy import w
from datetime import date,datetime
import pickle
w.start()

evalDate = ql.Date(1, 8, 2017)
#endDate = ql.Date(2, 8, 2017)
endDate = ql.Date(20, 10, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()
'''
while evalDate < endDate:

    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())

    data = w.wsi("510050.SH", "close", datestr+" 09:30:00", datestr+" 15:01:00", "Fill=Previous")
    print(data.Times)
    print(len(data.Data))
    df = pd.DataFrame(data=data.Data[0], index=data.Times)
    df.to_json(os.path.abspath('..') + '\marketdata\intraday_etf_'+datestr + '.json')

    evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))

'''
while evalDate < endDate:
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    df = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_'+datestr + '.json')
    print(len(df))
    evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))