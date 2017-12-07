# encoding: utf-8

from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime
import pandas as pd
from WindPy import w
import os

# import data_access.table_options_mktdata_daily as table_options
import data_access.table_equity_index_intraday as table_index
import data_access.table_option_mktdata_intraday as table_option

w.start()
# tradetype = 0  # 0:期货，1：期权
beg_date = datetime.date(2017, 11, 1)
end_date = datetime.date(2017, 12, 4)

engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata_intraday',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
equity_index_intraday = Table('equity_index_mktdata_intraday', metadata, autoload=True)
option_mktdata_intraday = Table('option_mktdata_intraday', metadata, autoload=True)

date_range = w.tdays(beg_date, end_date, "").Data[0]

for dt in date_range:
    dt_date = dt.date().strftime("%Y-%m-%d")
    dt_datetime = dt_date+' 09:30:00'
    res = option_mktdata_intraday.select(option_mktdata_intraday.c.dt_datetime == dt_datetime).execute()
    if res.rowcount > 0: continue
    print(dt_date)
    db_data = table_option.wind_data_50etf_option_intraday(dt_date)
    if len(db_data) == 0: continue
    try:
        conn.execute(option_mktdata_intraday.insert(), db_data)
        print('inserted into data base succefully')
    except Exception as e:
        print(dt)
        print(e)
        continue

# for dt in date_range:
#     dt_date = dt.date().strftime("%Y-%m-%d")
#     print(dt_date)
#     windcode = "510050.SH"
#     db_data = table_index.wind_data_equity_index(windcode, dt_date)
#     if len(db_data) == 0: continue
#     try:
#         conn.execute(equity_index_intraday.insert(), db_data)
#         print('inserted into data base succefully')
#     except Exception as e:
#         print(dt)
#         print(e)
#         continue
