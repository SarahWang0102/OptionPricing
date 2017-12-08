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
import data_access.table_equity_index_intraday as table_index
import data_access.table_option_mktdata_intraday as table_option_intraday

w.start()

# date = datetime.datetime.today().date()
date = datetime.date(2017, 12, 7)

engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
options_mktdata_daily = Table('options_mktdata', metadata, autoload=True)
futures_mktdata_daily = Table('futures_mktdata', metadata, autoload=True)
futures_institution_positions = Table('futures_institution_positions', metadata, autoload=True)

engine_intraday = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata_intraday', echo=False)
conn_intraday = engine_intraday.connect()
metadata_intraday = MetaData(engine_intraday)
equity_index_intraday = Table('equity_index_mktdata_intraday', metadata_intraday, autoload=True)
option_mktdata_intraday = Table('option_mktdata_intraday', metadata_intraday, autoload=True)

#####################table_options_mktdata_daily######################################
# wind 50ETF option
dt_date = date.strftime("%Y-%m-%d")
print(dt_date)
db_data = table_options.wind_data_50etf_option(dt_date)
if len(db_data) == 0: print('no data')
try:
    conn.execute(options_mktdata_daily.insert(), db_data)
    print('wind 50ETF option -- inserted into data base succefully')
except Exception as e:
    print(e)

# dce option data (type = 1), day
ds = dce.spider_mktdata_day(date, date, 1)
for dt in ds.keys():
    data = ds[dt]
    if len(data) == 0: continue
    db_data = table_options.dce_day(dt, data)
    if len(db_data) == 0: continue
    try:
        conn.execute(options_mktdata_daily.insert(), db_data)
        print('dce option data -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue
# dce option data (type = 1), night
ds = dce.spider_mktdata_night(date, date, 1)
for dt in ds.keys():
    data = ds[dt]
    if len(data) == 0: continue
    db_data = table_options.dce_night(dt, data)
    if len(db_data) == 0: continue
    try:
        conn.execute(options_mktdata_daily.insert(), db_data)
        print('dce option data -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue
# czce option data
ds = czce.spider_option(date, date)
for dt in ds.keys():
    data = ds[dt]
    if len(data) == 0: continue
    db_data = table_options.czce_daily(dt, data)
    if len(db_data) == 0: continue
    try:
        conn.execute(options_mktdata_daily.insert(), db_data)
        print('czce option data -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue

#####################futures_mktdata_daily######################################

# dce futures data (type = 0), day
ds = dce.spider_mktdata_day(date, date, 0)
for dt in ds.keys():
    data = ds[dt]
    db_data = table_futures.dce_day(dt, data)
    if len(db_data) == 0: continue
    try:
        conn.execute(futures_mktdata_daily.insert(), db_data)
        print('dce futures data -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue
# dce futures data (type = 0), night
ds = dce.spider_mktdata_night(date, date, 0)
for dt in ds.keys():
    data = ds[dt]
    db_data = table_futures.dce_night(dt, data)
    if len(db_data) == 0: continue
    try:
        conn.execute(futures_mktdata_daily.insert(), db_data)
        print('dce futures data -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue
# sfe futures data
ds = sfe.spider_mktdata(date, date)
for dt in ds.keys():
    data = ds[dt]
    db_data = table_futures.sfe_daily(dt, data)
    if len(db_data) == 0: continue
    try:
        conn.execute(futures_mktdata_daily.insert(), db_data)
        print('sfe futures data -- inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue

#####################equity_index_intraday######################################
dt_date = date.strftime("%Y-%m-%d")
windcode = "510050.SH"
db_data = table_index.wind_data_equity_index("510050.SH", dt_date)
try:
    conn_intraday.execute(equity_index_intraday.insert(), db_data)
    print('equity_index_intraday -- inserted into data base succefully')
except Exception as e:
    print(e)


#####################option_mktdata_intraday######################################
dt_date = date.strftime("%Y-%m-%d")
db_data = table_option_intraday.wind_data_50etf_option_intraday(dt_date)
try:
    conn_intraday.execute(option_mktdata_intraday.insert(), db_data)
    print('option_mktdata_intraday -- inserted into data base succefully')
except Exception as e:
    print(e)
