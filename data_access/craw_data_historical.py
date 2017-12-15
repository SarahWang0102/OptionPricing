# encoding: utf-8

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

w.start()
# tradetype = 0  # 0:期货，1：期权
beg_date = datetime.date(2016, 9, 6)
end_date = datetime.date(2017, 1, 1)

# beg_date = datetime.date(2017, 11, 16)
# end_date = datetime.date(2017, 12, 1)
engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
options_mktdata_daily = Table('options_mktdata', metadata, autoload=True)
futures_mktdata_daily = Table('futures_mktdata', metadata, autoload=True)
futures_dominants = Table('futures_dominants', metadata, autoload=True)
# futures_institution_positions = Table('futures_institution_positions', metadata, autoload=True)


# data = w.wsd("SR.CZC", "trade_hiscode", beg_date, end_date, "")
# data = w.wsd("RB.SHF", "trade_hiscode", beg_date, end_date, "")
# data = w.wsd("J.DCE", "trade_hiscode", beg_date, end_date, "")
#
# for idx,dt in enumerate(data.Times):
#     date = dt
#     name_contract = 'J.DCE'
#     a = data.Data[0][idx].lower()
#     # id_instrument = a[0:2]+'_1'+a[2:5]
#     id_instrument = a[0:1]+'_'+a[1:5]
#     db_data = {'dt_date':date,'name_contract':name_contract,'id_instrument':id_instrument}
#     try:
#         conn.execute(futures_dominants.insert(), db_data)
#         print('inserted into data base succefully')
#     except Exception as e:
#         print(dt)
#         print(e)
#         continue

date_range = w.tdays(beg_date, end_date, "").Data[0]
for dt in date_range:

    dt_date = dt.date().strftime("%Y-%m-%d")
    res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
                                        & (options_mktdata_daily.c.name_code == '50etf')).execute()
    if res.rowcount > 0: continue
    print(dt_date)
    db_data = table_options.wind_data_50etf_option(dt_date)
    if len(db_data) == 0: continue
    try:
        conn.execute(options_mktdata_daily.insert(), db_data)
        print('inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue


i = 0
while i < len(date_range):
    # crawd and insert into db 5-day data at a time
    begdate = date_range[i]
    if i+5 < len(date_range): enddate = date_range[i+5]
    else : enddate = date_range[-1]
    print(begdate,enddate)
    # dce option data (type = 1), day
    ds = dce.spider_mktdata_day(begdate, enddate, 1)
    for dt in ds.keys():
        data = ds[dt]
        if len(data) == 0: continue
        db_data = table_options.dce_day(dt, data)
        if len(db_data) == 0 : continue
        try:
            conn.execute(options_mktdata_daily.insert(), db_data)
            print('inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
    # dce option data (type = 1), night
    ds = dce.spider_mktdata_night(begdate, enddate, 1)
    for dt in ds.keys():
        data = ds[dt]
        if len(data) == 0: continue
        db_data = table_options.dce_night(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(options_mktdata_daily.insert(), db_data)
            print('inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
    # czce option data
    ds = czce.spider_option(begdate, enddate)
    for dt in ds.keys():
        data = ds[dt]
        if len(data) == 0: continue
        db_data = table_options.czce_daily(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(options_mktdata_daily.insert(), db_data)
            print('inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
    # dce futures data (type = 0), day
    ds = dce.spider_mktdata_day(begdate, enddate, 0)
    for dt in ds.keys():
        data = ds[dt]
        db_data = table_futures.dce_day(dt,data)
        if len(db_data) == 0 : continue
        try:
            conn.execute(futures_mktdata_daily.insert(), db_data)
        except Exception as e:
            print(dt)
            print(e)
            continue
    # dce futures data (type = 0), night
    ds = dce.spider_mktdata_night(begdate, enddate, 0)
    for dt in ds.keys():
        data = ds[dt]
        db_data = table_futures.dce_night(dt,data)
        if len(db_data) == 0 : continue
        try:
            conn.execute(futures_mktdata_daily.insert(), db_data)
        except Exception as e:
            print(dt)
            print(e)
            continue
    # sfe futures data
    ds = sfe.spider_mktdata(begdate, enddate)
    for dt in ds.keys():
        data = ds[dt]
        db_data = table_futures.sfe_daily(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(futures_mktdata_daily.insert(), db_data)
        except Exception as e:
            print(dt)
            print(e)
            continue
    # czce futures data
    ds = czce.spider_future(begdate, enddate)
    for dt in ds.keys():
        data = ds[dt]
        db_data = table_futures.czce_daily(dt, data)
        # print(db_data)
        if len(db_data) == 0:
            print('czce futures data -- no data')
            continue
        try:
            conn.execute(futures_mktdata_daily.insert(), db_data)
            print('czce futures data -- inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
    i += 6

