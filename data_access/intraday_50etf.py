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
#evalDate = ql.Date(20, 4, 2017)
endDate = ql.Date(1, 5, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()

evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))


while evalDate < endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    ids = w.wsd("SR.CZC", "trade_hiscode",datestr, datestr, "")

    #w.wsi("510050.SH", "close", "2017-11-09 09:00:00", "2017-11-09 12:17:54", "Fill=Previous")
    #print(ids.Data)
    data = w.wsi("510050.SH", "close", datestr+" 09:00:00", datestr+" 15:01:00", "Fill=Previous")
    #print(data.Times)
    #print(data.Data)
    df = pd.DataFrame(data=data.Data[0], index=data.Times)
    df.to_json(os.path.abspath('..') + '\marketdata\intraday_etf_'+datestr + '.json')

