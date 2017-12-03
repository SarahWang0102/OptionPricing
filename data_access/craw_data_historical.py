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
from data_access import table_options_mktdata_daily as table_option

w.start()
# tradetype = 0  # 0:期货，1：期权
beg_date = datetime.date(2017, 1, 1)
end_date = datetime.date(2017, 12, 2)

engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
table = Table('options_mktdata_daily', metadata, autoload=True)

date_range = w.tdays(beg_date, end_date, "").Data[0]

i = 0
while i < len(date_range):
    begdate = date_range[i]
    if i+5 < len(date_range): enddate = date_range[i+5]
    else : enddate = date_range[-1]
    print(begdate,enddate)
    ds = dce.spider_mktdata_day(begdate, enddate, 1)
    for dt in ds.keys():
        data = ds[dt]
        if len(data) == 0: continue
        db_data = table_option.dce_day(dt, data)
        if len(db_data) == 0 : continue
        try:
            conn.execute(table.insert(), db_data)
            print('inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
    # ds = None
    ds = dce.spider_mktdata_night(begdate, enddate, 1)
    for dt in ds.keys():
        data = ds[dt]
        if len(data) == 0: continue
        db_data = table_option.dce_night(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(table.insert(), db_data)
            print('inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
    # ds = None
    ds = czce.spider_option(begdate, enddate)
    for dt in ds.keys():
        data = ds[dt]
        if len(data) == 0: continue
        db_data = table_option.czce_daily(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(table.insert(), db_data)
            print('inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
    # ds = None
    i += 6

