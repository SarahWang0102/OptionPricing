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
from data_access.db_data_collection import DataCollection

w.start()

# date = datetime.datetime.today().date()
date = datetime.date(2018, 1, 12)
dt_date = date.strftime("%Y-%m-%d")
print(dt_date)

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
option_tick_data = Table('option_tick_data', metadata_intraday, autoload=True)
future_tick_data = Table('future_tick_data', metadata_intraday, autoload=True)
index_daily = Table('indexes_mktdata', metadata, autoload=True)
dc = DataCollection()

#####################table_options_mktdata_daily######################################
# wind 50ETF option
res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
                                   & (options_mktdata_daily.c.name_code == '50etf')).execute()
if res.rowcount == 0:
    db_data = dc.table_options().wind_data_50etf_option(dt_date)
    if len(db_data) == 0: print('no data')
    try:
        conn.execute(options_mktdata_daily.insert(), db_data)
        print('wind 50ETF option -- inserted into data base succefully')
    except Exception as e:
        print(e)
else:
    print('wind 50ETF option -- already exists')

# dce option data
res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
                                   & (options_mktdata_daily.c.cd_exchange == 'dce')).execute()
if res.rowcount == 0:
    # dce option data (type = 1), day
    ds = dce.spider_mktdata_day(date, date, 1)
    for dt in ds.keys():
        data = ds[dt]
        if len(data) == 0: continue
        db_data = dc.table_options().dce_day(dt, data)
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
        db_data = dc.table_options().dce_night(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(options_mktdata_daily.insert(), db_data)
            print('dce option data -- inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
else:
    print('dce option -- already exists')

# czce option data
res = options_mktdata_daily.select((options_mktdata_daily.c.dt_date == dt_date)
                                   & (options_mktdata_daily.c.cd_exchange == 'czce')).execute()
if res.rowcount == 0:
    ds = czce.spider_option(date, date)
    for dt in ds.keys():
        data = ds[dt]
        if len(data) == 0: continue
        db_data = dc.table_options().czce_daily(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(options_mktdata_daily.insert(), db_data)
            print('czce option data -- inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
else:
    print('czce option -- already exists')

#####################futures_mktdata_daily######################################
# equity index futures
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                   & (futures_mktdata_daily.c.cd_exchange == 'cfe')).execute()
if res.rowcount == 0:
    df = dc.table_future_contracts().get_future_contract_ids(dt_date)
    for (idx_oc, row) in df.iterrows():
        # print(row)
        db_data = dc.table_futures().wind_index_future_daily(dt_date, row['id_instrument'], row['windcode'])
        # print(db_data)
        try:
            conn.execute(futures_mktdata_daily.insert(), db_data)
            print(row)
            print('equity index futures -- inserted into data base succefully')
        except Exception as e:
            print(e)
else:
    print('equity index futures -- already exists')

# dce futures data
# dce futures data (type = 0), day
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                   & (futures_mktdata_daily.c.cd_exchange == 'dce')
                                   & (futures_mktdata_daily.c.flag_night == 0)).execute()
if res.rowcount == 0:
    ds = dce.spider_mktdata_day(date, date, 0)
    for dt in ds.keys():
        data = ds[dt]
        db_data = dc.table_futures().dce_day(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(futures_mktdata_daily.insert(), db_data)
            print('dce futures data 0 -- inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
else:
    print('dce future 0 -- already exists')
# dce futures data (type = 0), night
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                       & (futures_mktdata_daily.c.cd_exchange == 'dce')
                                        & (futures_mktdata_daily.c.flag_night == 1)).execute()
if res.rowcount == 0:
    ds = dce.spider_mktdata_night(date, date, 0)
    for dt in ds.keys():
        data = ds[dt]
        db_data = dc.table_futures().dce_night(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(futures_mktdata_daily.insert(), db_data)
            print('dce futures data 1 -- inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
else:
    print('dce future 1 -- already exists')

# sfe futures data
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                   & (futures_mktdata_daily.c.cd_exchange == 'sfe')).execute()
if res.rowcount == 0:
    ds = sfe.spider_mktdata(date, date)
    for dt in ds.keys():
        data = ds[dt]
        db_data = dc.table_futures().sfe_daily(dt, data)
        if len(db_data) == 0: continue
        try:
            conn.execute(futures_mktdata_daily.insert(), db_data)
            print('sfe futures data -- inserted into data base succefully')
        except Exception as e:
            print(dt)
            print(e)
            continue
else:
    print('sfe future -- already exists')

# czce futures data
res = futures_mktdata_daily.select((futures_mktdata_daily.c.dt_date == dt_date)
                                   & (futures_mktdata_daily.c.cd_exchange == 'czce')).execute()
if res.rowcount == 0:
    ds = czce.spider_future(date, date)
    for dt in ds.keys():
        data = ds[dt]
        db_data = dc.table_futures().czce_daily(dt, data)
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
else:
    print('czce future -- already exists')

#####################index_mktdata_daily######################################
res = index_daily.select((index_daily.c.dt_date == dt_date) &
                         (index_daily.c.id_instrument == 'index_50etf')).execute()
if res.rowcount == 0:
    windcode = "510050.SH"
    id_instrument = 'index_50etf'
    db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
    try:
        conn.execute(index_daily.insert(), db_data)
        print('equity_index-50etf -- inserted into data base succefully')
    except Exception as e:
        print(e)
res = index_daily.select((index_daily.c.dt_date == dt_date) &
                         (index_daily.c.id_instrument == 'index_50sh')).execute()
if res.rowcount == 0:
    windcode = "000016.SH"
    id_instrument = 'index_50sh'
    db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
    try:
        conn.execute(index_daily.insert(), db_data)
        print('equity_index-50etf -- inserted into data base succefully')
    except Exception as e:
        print(e)
res = index_daily.select((index_daily.c.dt_date == dt_date) &
                         (index_daily.c.id_instrument == 'index_300sh')).execute()
if res.rowcount == 0:
    windcode = "000300.SH"
    id_instrument = 'index_300sh'
    db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
    try:
        conn.execute(index_daily.insert(), db_data)
        print('equity_index-50etf -- inserted into data base succefully')
    except Exception as e:
        print(e)
res = index_daily.select((index_daily.c.dt_date == dt_date) &
                         (index_daily.c.id_instrument == 'index_500sh')).execute()
if res.rowcount == 0:
    windcode = "000905.SH"
    id_instrument = 'index_500sh'
    db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
    try:
        conn.execute(index_daily.insert(), db_data)
        print('equity_index-500sh -- inserted into data base succefully')
    except Exception as e:
        print(e)
else:
    print('index daily -- already exists')

res = index_daily.select((index_daily.c.dt_date == dt_date) &
                         (index_daily.c.id_instrument == 'index_cvix')).execute()
if res.rowcount == 0:
    windcode = "000188.SH"
    id_instrument = 'index_cvix'
    db_data = dc.table_index().wind_data_index(windcode, dt_date, id_instrument)
    try:
        conn.execute(index_daily.insert(), db_data)
        print('equity_index-cvix -- inserted into data base succefully')
    except Exception as e:
        print(e)
else:
    print('index daily -- already exists')

#####################equity_index_intraday######################################
res = equity_index_intraday.select((equity_index_intraday.c.dt_datetime == dt_date + " 09:30:00") &
                                   (equity_index_intraday.c.id_instrument == 'index_50etf')).execute()
if res.rowcount == 0:
    windcode = "510050.SH"
    id_instrument = 'index_50etf'
    db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
    try:
        conn_intraday.execute(equity_index_intraday.insert(), db_data)
        print('equity_index_intraday-50etf -- inserted into data base succefully')
    except Exception as e:
        print(e)
res = equity_index_intraday.select((equity_index_intraday.c.dt_datetime == dt_date + " 09:30:00") &
                                   (equity_index_intraday.c.id_instrument == 'index_50sh')).execute()
if res.rowcount == 0:
    windcode = "000016.SH"
    id_instrument = 'index_50sh'
    db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
    try:
        conn_intraday.execute(equity_index_intraday.insert(), db_data)
        print('equity_index_intraday-50sh -- inserted into data base succefully')
    except Exception as e:
        print(e)
res = equity_index_intraday.select((equity_index_intraday.c.dt_datetime == dt_date + " 09:30:00") &
                                   (equity_index_intraday.c.id_instrument == 'index_300sh')).execute()
if res.rowcount == 0:
    windcode = "000300.SH"
    id_instrument = 'index_300sh'
    db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
    try:
        conn_intraday.execute(equity_index_intraday.insert(), db_data)
        print('equity_index_intraday-300sh -- inserted into data base succefully')
    except Exception as e:
        print(e)
res = equity_index_intraday.select((equity_index_intraday.c.dt_datetime == dt_date + " 09:30:00") &
                                   (equity_index_intraday.c.id_instrument == 'index_500sh')).execute()
if res.rowcount == 0:
    windcode = "000905.SH"
    id_instrument = 'index_500sh'
    db_data = dc.table_index_intraday().wind_data_equity_index(windcode, dt_date, id_instrument)
    try:
        conn_intraday.execute(equity_index_intraday.insert(), db_data)
        print('equity_index_intraday-500sh -- inserted into data base succefully')
    except Exception as e:
        print(e)
else:
    print(
        'equity index intraday -- already exists')

####################option_mktdata_intraday######################################
res = option_mktdata_intraday.select(option_mktdata_intraday.c.dt_datetime == dt_date + " 09:30:00").execute()
if res.rowcount == 0:
    df = dc.table_option_tick().wind_option_chain(dt_date)
    for (idx_oc, row) in df.iterrows():
        db_data = dc.table_option_intraday().wind_data_50etf_option_intraday(dt_date, row)
        try:
            conn_intraday.execute(option_mktdata_intraday.insert(), db_data)
            print('option_mktdata_intraday -- inserted into data base succefully')
        except Exception as e:
            print(e)
else:
    print('option intraday -- already exists')

#####################future_tick_data######################################
# equity index futures
res = future_tick_data.select(future_tick_data.c.dt_datetime == dt_date + " 09:30:00").execute()
if res.rowcount == 0:
    df = dc.table_future_contracts().get_future_contract_ids(dt_date)
    for (idx_oc, row) in df.iterrows():
        # print(row)
        db_data = dc.table_future_tick().wind_index_future_tick(dt_date, row['id_instrument'], row['windcode'])
        # print(db_data)
        try:
            conn_intraday.execute(future_tick_data.insert(), db_data)
            print(row)
            print('future_tick_data -- inserted into data base succefully')
        except Exception as e:
            print(e)
else:
    print('future_tick_data -- already exists')

####################option_tick_data######################################
res = option_tick_data.select(option_tick_data.c.dt_datetime == dt_date + " 09:30:00").execute()
if res.rowcount == 0:
    df = dc.table_option_tick().wind_option_chain(dt_date)
    for (idx_oc, row) in df.iterrows():
        # print(row)
        db_data = dc.table_option_tick().wind_50etf_option_tick(dt_date, row)
        # print(db_data)
        try:
            conn_intraday.execute(option_tick_data.insert(), db_data)
            print(idx_oc)
            print('option_tick_data -- inserted into data base succefully')
        except Exception as e:
            print(e)
else:
    print('option_tick_data -- already exists')
