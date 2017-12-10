# encoding: utf-8

from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP,select
import datetime
from WindPy import w
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
    datasource = 'czce'
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
        amt_holding_volume = product.loc['空盘量'].replace(',', '')
        amt_bid = 0.0
        amt_ask = 0.0
        amt_exercised = product.loc['行权量'].replace(',', '')
        amt_implied_vol = product.loc['隐含波动率'].replace(',', '')
        amt_delta = product.loc['DELTA'].replace(',', '')
        db_row = {'dt_date': dt_date,
                  'id_instrument': id_instrument.encode('utf-8'),
                  'flag_night': flag_night,
                  'datasource': datasource,
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
    datasource = 'dce'
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
                  'datasource': datasource,
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

def dce_night(dt, data):
    db_data = []
    # print(data)
    cd_exchange = 'dce'
    datasource = 'dce'
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
                  'datasource': datasource,
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


def wind_data_50etf_option(datestr):

    db_data = []
    id_underlying = 'index_50etf'
    name_code = '50etf'
    windcode_underlying = '510050.SH'
    datasource = 'wind'
    cd_exchange = 'sse'
    flag_night = -1

    optionchain = w.wset("optionchain","date="+datestr+";us_code=510050.SH;option_var=全部;call_put=全部")
    df_optionchain = pd.DataFrame()
    for i, f in enumerate(optionchain.Fields):
        df_optionchain[f] = optionchain.Data[i]

    data = w.wset("optiondailyquotationstastics",
                  "startdate="+datestr+";enddate="+datestr+";exchange=sse;windcode=510050.SH")
    df_mktdatas = pd.DataFrame()
    for i1, f1 in enumerate(data.Fields):
        df_mktdatas[f1] = data.Data[i1]
    df_mktdatas = df_mktdatas.fillna(-999.0)
    for (i2, df_mktdata) in df_mktdatas.iterrows():
        dt_date = datetime.datetime.strptime(datestr,"%Y-%m-%d").date()
        windcode = df_mktdata['option_code'] + '.SH'
        criterion = df_optionchain['option_code'].map(lambda x: x == windcode)
        option_info = df_optionchain[criterion]
        amt_strike = option_info['strike_price'].values[0]
        contract_month = str(option_info['month'].values[0])[-4:]
        sec_name = option_info['option_name'].values[0]
        if option_info['call_put'].values[0] == '认购' : cd_option_type = 'call'
        elif option_info['call_put'].values[0] == '认沽' : cd_option_type = 'put'
        else :
            cd_option_type = 'none'
            print('error in call_or_put')
        if sec_name[-1] == 'A':
            id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6] + '_A'
        else:
            id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]

        amt_last_settlement = df_mktdata['pre_settle']
        amt_open = df_mktdata['open']
        amt_high = df_mktdata['highest']
        amt_low = df_mktdata['lowest']
        amt_close = df_mktdata['close']
        amt_settlement = df_mktdata['settlement_price']
        amt_delta = df_mktdata['delta']
        amt_gamma = df_mktdata['gamma']
        amt_vega = df_mktdata['vega']
        amt_theta = df_mktdata['theta']
        amt_rho = df_mktdata['rho']
        amt_trading_volume = df_mktdata['volume']
        amt_trading_value = df_mktdata['amount']
        amt_holding_volume = df_mktdata['position']
        db_row = {'dt_date': dt_date,
                  'id_instrument': id_instrument,
                  'flag_night': flag_night,
                  'datasource': datasource,
                  'code_instrument': windcode,
                  'name_code': name_code,
                  'id_underlying': id_underlying,
                  'amt_strike': float(amt_strike),
                  'cd_option_type': cd_option_type,
                  'amt_last_settlement': float(amt_last_settlement),
                  'amt_open': float(amt_open),
                  'amt_high': float(amt_high),
                  'amt_low': float(amt_low),
                  'amt_close': float(amt_close),
                  'amt_settlement': float(amt_settlement),
                  'amt_delta': float(amt_delta),
                  'amt_gamma': float(amt_gamma),
                  'amt_vega': float(amt_vega),
                  'amt_theta': float(amt_theta),
                  'amt_rho': float(amt_rho),
                  'amt_trading_volume': float(amt_trading_volume),
                  'amt_trading_value': float(amt_trading_value),
                  'amt_holding_volume': float(amt_holding_volume),
                  'cd_exchange': cd_exchange,
                  'timestamp': datetime.datetime.today()
                  }
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
