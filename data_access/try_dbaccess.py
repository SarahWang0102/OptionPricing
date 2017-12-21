# encoding: utf-8

import QuantLib as ql
from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime
import pandas as pd
from WindPy import w
import os
from data_access import db_utilities as du
from data_access import spider_api_dce as dce
from data_access import spider_api_sfe as sfe
from data_access import spider_api_czce as czce
import data_access.table_options_mktdata_daily as table_options
import data_access.table_futures_mktdata_daily as table_futures
import data_access.table_equity_index_intraday as table_index_intraday
import data_access.table_option_mktdata_intraday as table_option_intraday
import data_access.table_option_tick_data as table_option_tick
import data_access.table_future_tick_data as table_future_tick
import data_access.table_index_mktdata_daily as table_index


w.start()

# dt_date = '2017-12-15'
# windcode = "510050.SH"
# id_instrument = 'index_50etf'
# db_data = table_index.wind_data_index(windcode,'2017-12-18',id_instrument)
# print(db_data)
data = w.wset("optionchain","date=2017-12-07;us_code=510050.SH;option_var=全部;call_put=全部")
print(data.ErrorCode)
# engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
#                        echo=False)
# metadata = MetaData(engine)
# future_contracts = Table('future_contracts', metadata, autoload=True)
# FutureContracts = dbt.Futures
# Session = sessionmaker(bind=engine)
# sess = Session()
# query = sess.query(FutureContracts.windcode)\
#             .filter(datestr>=FutureContracts.dt_listed)\
#             .filter(datestr<=FutureContracts.dt_maturity)
# df = pd.read_sql(query.statement,query.session.bind)
# print(df)
# begstr = '2017-12-08'
# endstr = '2017-12-15'
# data = w.wsd("IH.CFE", "trade_hiscode",begstr, endstr, "")
#
# print(data.Times)
# print(data.Data)

# datestr = '2017-11-22'
# # data = w.wset("optionchain","date=2017-12-07;us_code=510050.SH;option_var=全部;call_put=全部")
# data = w.wset("optiondailyquotationstastics",
#                   "startdate="+datestr+";enddate="+datestr+";exchange=sse;windcode=510050.SH")
# df = pd.DataFrame()
# for i,f in enumerate(data.Fields):
#     df[f] = data.Data[i]
#
# print(df)
# df = df.fillna(0.0)
#
# print(df)
#
# criterion = df['option_code'].map(lambda x: x =='10000897.SH')
# print(df[criterion])
# for (i,r) in df.iterrows():
#     print(r['option_code'])
# engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
#                        echo=False)
# conn = engine.connect()
# metadata = MetaData(engine)
# option_contracts = Table('option_contracts', metadata, autoload=True)
# options_mktdata_daily = Table('options_mktdata', metadata, autoload=True)
#
# res1 = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == '2017-11-22')
#                               & (options_mktdata_daily.c.name_code == '50etf')).execute()
# res2 = select([option_contracts.c.id_instrument,option_contracts.c.windcode],
#              option_contracts.c.id_instrument == 'm_1801_c_2450').execute()
# res = select([option_contracts.c.id_instrument],
#                      option_contracts.c.windcode == '10000001.SH').execute()
# for r in res1:
#     print('r : ',r[0])
# if res1.rowcount == 0 : print('empty data')
# data = w.wset("optiondailyquotationstastics","startdate=2017-12-05;enddate=2017-12-05;exchange=sse;windcode=510050.SH")
# print(data.Fields)
# for f in data.Fields:
#     print(f)
# w.start()
#
# evalDate = ql.Date(1, 4, 2017)
# # evalDate = ql.Date(28, 7, 2017)
# endDate = ql.Date(2, 5, 2017)
# calendar = ql.China()
# daycounter = ql.ActualActual()

# evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
#
# begstr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
# endstr = str(endDate.year()) + "-" + str(endDate.month()) + "-" + str(endDate.dayOfMonth())
# # data = w.wsd("SR.CZC", "trade_hiscode",begstr, endstr, "")
# data = w.wsd("M.DCE", "trade_hiscode",begstr, endstr, "")
# df = pd.DataFrame(data=data.Data[0], index=data.Times)
# df.to_json(os.path.abspath('..') + '\marketdata\hiscodes_m' + '.json')
# # df.to_json(os.path.abspath('..') + '\marketdata\hiscodes_sr' + '.json')
# print(df)
#
# with open(os.path.abspath('..') + '/intermediate_data/total_hedging_bs_estimated_vols_call.pickle', 'rb') as f:
#     estimated_vols = pickle.load(f)[0]
#
# print(estimated_vols)
# for key in estimated_vols.keys():
#     print(key,estimated_vols[key])

'''
while evalDate < endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    # ids = w.wsd("SR.CZC", "trade_hiscode",datestr, datestr, "")
    ids = w.wsd("M.DCE", "trade_hiscode",datestr, datestr, "")
    #print(ids.Data)
    data = w.wsi(ids.Data[0][0], "close", datestr+" 09:00:00", datestr+" 23:31:00", "Fill=Previous")
    print(data.Times)
    #print(data.Data[-1])
    df = pd.DataFrame(data=data.Data[0], index=data.Times)
    df.to_json(os.path.abspath('..') + '\marketdata\intraday_m_'+datestr + '.json')
    # df.to_json(os.path.abspath('..') + '\marketdata\intraday_sr_'+datestr + '.json')



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

