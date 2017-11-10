# encoding: utf-8

from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime
import pandas as pd
import os
from data_access import db_utilities as du
from data_access import spider_api_dce as dce
from data_access import spider_api_sfe as sfe


def dce_night(dt,data):
    db_data = []
    for column in data.columns.values:
        product = data[column]
        codename = du.get_codename(product.loc['商品名称'])
        id_instrument = codename +'_'+ product.loc['交割月份']
        dt_date = dt
        flag_night = 1
        name_code = codename
        amt_last_close = 0.0
        amt_last_settlement = product.loc['前结算价'].replace(',', '')
        amt_open = product.loc['开盘价'].replace(',', '')
        amt_high = product.loc['最高价'].replace(',', '')
        amt_low = product.loc['最低价'].replace(',', '')
        amt_close = product.loc['最新价'].replace(',', '')
        amt_settlement = 0.0
        amt_trading_volume = product.loc['成交量'].replace(',', '')
        amt_trading_value = product.loc['成交额'].replace(',', '')
        amt_holding_volume = product.loc['持仓量'].replace(',', '')
        db_row = {'dt_date': dt_date,
                  'id_instrument': id_instrument,
                  'flag_night': flag_night,
                  'name_code': name_code,
                  'amt_last_close': amt_last_close,
                  'amt_last_settlement': amt_last_settlement,
                  'amt_open': amt_open,
                  'amt_high': amt_high,
                  'amt_low': amt_low,
                  'amt_close': amt_close,
                  'amt_settlement': amt_settlement,
                  'amt_trading_volume': amt_trading_volume,
                  'amt_trading_value': amt_trading_value,
                  'amt_holding_volume': amt_holding_volume,
                  'cd_exchange':'dce',
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data


def dce_day(dt,data):
    db_data = []
    for column in data.columns.values:
        product = data[column]
        codename = du.get_codename(product.loc['商品名称'])
        id_instrument = codename +'_' + product.loc['交割月份']
        dt_date = dt
        flag_night = 0
        name_code = codename
        amt_last_close = 0.0
        amt_last_settlement = product.loc['前结算价'].replace(',', '')
        amt_open = product.loc['开盘价'].replace(',', '')
        amt_high = product.loc['最高价'].replace(',', '')
        amt_low = product.loc['最低价'].replace(',', '')
        amt_close = product.loc['收盘价'].replace(',', '')
        amt_settlement = product.loc['结算价'].replace(',', '')
        amt_trading_volume = product.loc['成交量'].replace(',', '')
        amt_trading_value = product.loc['成交额'].replace(',', '')
        amt_holding_volume = product.loc['持仓量'].replace(',', '')
        db_row = {'dt_date': dt_date,
                  'id_instrument': id_instrument,
                  'flag_night':flag_night,
                  'name_code': name_code,
                  'amt_last_close': amt_last_close,
                  'amt_last_settlement': amt_last_settlement,
                  'amt_open': amt_open,
                  'amt_high': amt_high,
                  'amt_low': amt_low,
                  'amt_close': amt_close,
                  'amt_settlement': amt_settlement,
                  'amt_trading_volume': amt_trading_volume,
                  'amt_trading_value': amt_trading_value,
                  'amt_holding_volume': amt_holding_volume,
                  'cd_exchange': 'dce',
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data


def sfe_daily(dt,data):
    key_map = du.key_map_sfe()
    data_dict1 = data['o_curinstrument']
    db_data = []
    for dict in data_dict1:
        name = dict[key_map['codename']].replace(' ', '')
        contractmonth = dict[key_map['contractmonth']].replace(' ', '')
        if name == '总计' or contractmonth =='小计':continue
        try:
            name_code = name[0:name.index('_')]
        except:
            print(name)
            continue
        id_instrument = (name_code + '_' + contractmonth).encode('utf-8')
        dt_date = dt
        flag_night = -1
        amt_last_close = dict[key_map['amt_last_close']]
        amt_last_settlement = dict[key_map['amt_last_settlement']]
        amt_open = dict[key_map['amt_open']]
        amt_high = dict[key_map['amt_high']]
        amt_low = dict[key_map['amt_low']]
        amt_close = dict[key_map['amt_close']]
        amt_settlement = dict[key_map['amt_settlement']]
        amt_trading_volume = dict[key_map['amt_trading_volume']]
        amt_trading_value = 0.0
        amt_holding_volume = dict[key_map['amt_holding_volume']]
        if amt_last_close == '' : amt_last_close = 0.0
        if amt_last_settlement == '' : amt_last_settlement = 0.0
        if amt_open == '' : amt_open = 0.0
        if amt_high == '' : amt_high = 0.0
        if amt_low == '' : amt_low = 0.0
        if amt_close == '' : amt_close = 0.0
        if amt_settlement == '' : amt_settlement = 0.0
        if amt_trading_volume == '' : amt_trading_volume = 0.0
        if amt_trading_value == '' : amt_trading_value = 0.0
        if amt_holding_volume == '' : amt_holding_volume = 0.0

        db_row = {'dt_date': dt_date,
                  'id_instrument': id_instrument,
                  'flag_night': flag_night,
                  'name_code': name_code,
                  'amt_last_close': amt_last_close,
                  'amt_last_settlement': amt_last_settlement,
                  'amt_open': amt_open,
                  'amt_high': amt_high,
                  'amt_low': amt_low,
                  'amt_close': amt_close,
                  'amt_settlement': amt_settlement,
                  'amt_trading_volume': amt_trading_volume,
                  'amt_trading_value': amt_trading_value,
                  'amt_holding_volume': amt_holding_volume,
                  'cd_exchange': 'sfe',
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data
tradetype = 0  # 0:期货，1：期权
begdate = datetime.date(2017, 9, 21)
enddate = datetime.date(2017, 10, 1)


engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
table = Table('futures_mktdata_daily', metadata, autoload=True)

# ds_day = dce.spider_mktdata_day(begdate, enddate, tradetype)
# for dt in ds_day.keys():
#     data = ds_day[dt]
#     db_data = dce_day(dt,data)
#     try:
#         conn.execute(table.insert(), db_data)
#     except Exception as e:
#         print(dt)
#         print(e)
#         continue
# ds_day = None
#
# ds_night = dce.spider_mktdata_night(begdate, enddate, tradetype)
# for dt in ds_night.keys():
#     data = ds_night[dt]
#     db_data = dce_night(dt,data)
#     try:
#         conn.execute(table.insert(), db_data)
#     except Exception as e:
#         print(dt)
#         print(e)
#         continue
# ds_night = None

ds =sfe.spider_mktdata(begdate,enddate)
for dt in ds.keys():
    data = ds[dt]
    db_data = sfe_daily(dt,data)
    try:
        conn.execute(table.insert(), db_data)
    except Exception as e:
        print(dt)
        print(e)
        continue
ds = None


