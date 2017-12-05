# encoding: utf-8

from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime
import pandas as pd
from WindPy import w
import os

# import data_access.table_options_mktdata_daily as table_options
import data_access.table_equity_index_intraday as table_EI
import data_access.table_option_contracts as table_options

w.start()
# tradetype = 0  # 0:期货，1：期权
# beg_date = datetime.date(2017, 11, 1)
# end_date = datetime.date(2017, 12, 4)

engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
option_contracts = Table('option_contracts', metadata, autoload=True)

# db_datas = table_options.wind_options_50etf()
# for db_data in db_datas:
#     try:
#         conn.execute(option_contracts.insert(), db_data)
#     except Exception as e:
#         print(e)
#         print(db_data)
#         continue

# db_datas = table_options.wind_options_m()
# for db_data in db_datas:
#     try:
#         conn.execute(option_contracts.insert(), db_data)
#     except Exception as e:
#         print(e)
#         print(db_data)
#         continue

db_datas = table_options.wind_options_sr()
for db_data in db_datas:
    try:
        conn.execute(option_contracts.insert(), db_data)
    except Exception as e:
        print(e)
        print(db_data)
        continue
