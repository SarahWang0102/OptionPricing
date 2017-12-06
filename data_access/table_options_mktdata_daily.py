# encoding: utf-8

from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime
import pandas as pd
import os
from data_access import db_utilities as du
from data_access import spider_api_dce as dce
from data_access import spider_api_sfe as sfe
from data_access import spider_api_czce as czce

def czce_daily(dt, data):
    db_data = []
    # print(data)
    cd_exchange = 'czce'
    flag_night = -1
    for column in data.columns.values:
        product = data[column]
        product_name = product.loc['品种代码'].lower()
        dt_date = dt
        name_code = product_name[0:2]
        underlying = '1' + product_name[2:5]
        option_type = product_name[5]
        strike = product_name[-4:].replace(',', '').replace(' ', '')
        id_instrument = name_code + '_' + underlying + '_' + option_type + '_' + strike
        id_underlying = name_code + '_' + underlying
        amt_strike = float(strike)
        if option_type == 'c':
            cd_option_type = 'call'
        else:
            cd_option_type = 'put'
        amt_last_close = 0.0
        amt_last_settlement = product.loc['昨结算'].replace(',', '')
        amt_open = product.loc['今开盘'].replace(',', '')
        amt_high = product.loc['最高价'].replace(',', '')
        amt_low = product.loc['最低价'].replace(',', '')
        amt_close = product.loc['今收盘'].replace(',', '')
        amt_settlement = product.loc['今结算'].replace(',', '')
        amt_trading_volume = product.loc['成交量(手)'].replace(',', '')
        amt_trading_value = product.loc['成交额(万元)'].replace(',', '')
        amt_holding_volume = 0.0
        amt_bid = 0.0
        amt_ask = 0.0
        amt_exercised = product.loc['行权量'].replace(',', '')
        amt_implied_vol = product.loc['隐含波动率'].replace(',', '')
        amt_delta = product.loc['DELTA'].replace(',', '')
        db_row = {'dt_date': dt_date,
                  'id_instrument': id_instrument.encode('utf-8'),
                  'flag_night': flag_night,
                  'name_code': name_code,
                  'id_underlying': id_underlying.encode('utf-8'),
                  'amt_strike': amt_strike,
                  'cd_option_type': cd_option_type.encode('utf-8'),
                  'amt_last_close': amt_last_close,
                  'amt_last_settlement': amt_last_settlement,
                  'amt_open': amt_open,
                  'amt_high': amt_high,
                  'amt_low': amt_low,
                  'amt_close': amt_close,
                  'amt_settlement': amt_settlement,
                  'amt_bid': amt_bid,
                  'amt_ask': amt_ask,
                  'pct_implied_vol': amt_implied_vol,
                  'amt_delta': amt_delta,
                  'amt_trading_volume': amt_trading_volume,
                  'amt_trading_value': amt_trading_value,
                  'amt_holding_volume': amt_holding_volume,
                  'amt_exercised': amt_exercised,
                  'cd_exchange': cd_exchange,
                  'timestamp': datetime.datetime.today()
                  }
        # print(db_data)
        db_data.append(db_row)
    return db_data

def dce_day(dt, data):
    db_data = []
    # print(data)
    cd_exchange = 'dce'
    flag_night = 0
    for column in data.columns.values:
        product = data[column]
        product_name = product.loc['合约名称'].lower()
        dt_date = dt
        name_code = product_name[0:product_name.index('1')]
        id_underlying = name_code +'_'+ product_name[product_name.index('1'):product_name.index('1')+4]
        option_type = product_name[product_name.index('-')+1]
        strike = product_name[-4:].replace(',', '').replace(' ', '')
        id_instrument = id_underlying + '_' + option_type + '_' + strike
        amt_strike = float(strike)
        if option_type == 'c':
            cd_option_type = 'call'
        else:
            cd_option_type = 'put'
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
        amt_bid = 0.0
        amt_ask = 0.0
        amt_exercised = product.loc['行权量'].replace(',', '')
        amt_implied_vol = 0.0
        amt_delta = product.loc['Delta'].replace(',', '')
        db_row = {'dt_date': dt_date,
                  'id_instrument': id_instrument.encode('utf-8'),
                  'flag_night': flag_night,
                  'name_code': name_code,
                  'id_underlying': id_underlying.encode('utf-8'),
                  'amt_strike': amt_strike,
                  'cd_option_type': cd_option_type.encode('utf-8'),
                  'amt_last_close': amt_last_close,
                  'amt_last_settlement': amt_last_settlement,
                  'amt_open': amt_open,
                  'amt_high': amt_high,
                  'amt_low': amt_low,
                  'amt_close': amt_close,
                  'amt_settlement': amt_settlement,
                  'amt_bid': amt_bid,
                  'amt_ask': amt_ask,
                  'pct_implied_vol': amt_implied_vol,
                  'amt_delta': amt_delta,
                  'amt_trading_volume': amt_trading_volume,
                  'amt_trading_value': amt_trading_value,
                  'amt_holding_volume': amt_holding_volume,
                  'amt_exercised': amt_exercised,
                  'cd_exchange': 'dce',
                  'timestamp': datetime.datetime.today()
                  }
        # print(db_data)
        db_data.append(db_row)
    return db_data

def dce_night(dt, data):
    db_data = []
    # print(data)
    cd_exchange = 'dce'
    flag_night = 1
    for column in data.columns.values:
        product = data[column]
        product_name = product.loc['合约名称'].lower()
        dt_date = dt
        name_code = product_name[0:product_name.index('1')]
        id_underlying = name_code +'_'+ product_name[product_name.index('1'):product_name.index('1')+4]
        option_type = product_name[product_name.index('-')+1]
        strike = product_name[-4:].replace(',', '').replace(' ', '')
        id_instrument = id_underlying + '_' + option_type + '_' + strike
        amt_strike = float(strike)
        if option_type == 'c':
            cd_option_type = 'call'
        else:
            cd_option_type = 'put'
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
        amt_bid = 0.0
        amt_ask = 0.0
        amt_exercised = 0.0
        amt_implied_vol = 0.0
        amt_delta = 0.0
        db_row = {'dt_date': dt_date,
                  'id_instrument': id_instrument.encode('utf-8'),
                  'flag_night': flag_night,
                  'name_code': name_code,
                  'id_underlying': id_underlying.encode('utf-8'),
                  'amt_strike': amt_strike,
                  'cd_option_type': cd_option_type.encode('utf-8'),
                  'amt_last_close': amt_last_close,
                  'amt_last_settlement': amt_last_settlement,
                  'amt_open': amt_open,
                  'amt_high': amt_high,
                  'amt_low': amt_low,
                  'amt_close': amt_close,
                  'amt_settlement': amt_settlement,
                  'amt_bid': amt_bid,
                  'amt_ask': amt_ask,
                  'pct_implied_vol': amt_implied_vol,
                  'amt_delta': amt_delta,
                  'amt_trading_volume': amt_trading_volume,
                  'amt_trading_value': amt_trading_value,
                  'amt_holding_volume': amt_holding_volume,
                  'amt_exercised': amt_exercised,
                  'cd_exchange': 'dce',
                  'timestamp': datetime.datetime.today()
                  }
        # print(db_data)
        db_data.append(db_row)
    return db_data

# # tradetype = 0  # 0:期货，1：期权
# begdate = datetime.date(2017, 12, 1)
# enddate = datetime.date(2017, 12, 2)
#
# engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
#                        echo=False)
# conn = engine.connect()
# metadata = MetaData(engine)
# table = Table('options_mktdata_daily', metadata, autoload=True)
#
# ds =dce.spider_mktdata_day(begdate,enddate,1)
# for dt in ds.keys():
#     data = ds[dt]
#     db_data = dce_day(dt,data)
#     try:
#         conn.execute(table.insert(), db_data)
#     except Exception as e:
#         print(dt)
#         print(e)
#         continue
# ds = None
#
# ds =dce.spider_mktdata_night(begdate,enddate,1)
# for dt in ds.keys():
#     data = ds[dt]
#     db_data = dce_night(dt,data)
#     try:
#         conn.execute(table.insert(), db_data)
#     except Exception as e:
#         print(dt)
#         print(e)
#         continue
# ds = None
#
#
# ds =czce.spider_option(begdate,enddate)
# for dt in ds.keys():
#     data = ds[dt]
#     db_data = czce_daily(dt,data)
#     try:
#         conn.execute(table.insert(), db_data)
#     except Exception as e:
#         print(dt)
#         print(e)
#         continue
# ds = None
