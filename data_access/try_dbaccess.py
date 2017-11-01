import QuantLib as ql
import pandas as pd
import os
from Utilities.svi_read_data import get_wind_data
import data_access.wind_data as wd
from WindPy import w
from datetime import date,datetime
import pickle
w.start()

evalDate = ql.Date(26, 4, 2017)
#evalDate = ql.Date(28, 7, 2017)
endDate = ql.Date(20, 10, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()


while evalDate < endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    ids = w.wsd("M.DCE", "trade_hiscode",datestr, datestr, "")
    #print(ids.Data)
    data = w.wsi(ids.Data[0][0], "close", datestr+" 09:00:00", datestr+" 23:31:00", "Fill=Previous")
    #print(data.Times[-1])
    #print(data.Data[-1])
    df = pd.DataFrame(data=data.Data[0], index=data.Times)
    df.to_json(os.path.abspath('..') + '\marketdata\intraday_m_'+datestr + '.json')



'''
while evalDate < endDate:
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    df = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_'+datestr + '.json')
    print(len(df))
    evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
'''