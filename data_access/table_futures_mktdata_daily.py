from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime
import pandas as pd
import os
from data_access import db_utilities as du
from data_access import spider_api_dce as dce


def orgnise_data_night(dt,data):
    db_data = []
    for column in data.columns.values:
        product = data[column]
        codename = du.get_codename(product.loc['商品名称'])
        id_instrument = codename + product.loc['交割月份']
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
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data


def orgnise_data_day(dt,data):
    db_data = []
    for column in data.columns.values:
        product = data[column]
        codename = du.get_codename(product.loc['商品名称'])
        id_instrument = codename + product.loc['交割月份']
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
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data

tradetype = 0  # 0:期货，1：期权
begdate = datetime.date(2017, 10, 30)
enddate = datetime.date(2017, 11, 3)
ds = dce.spider_mktdata_day(begdate, enddate, tradetype)
ds2 = dce.spider_mktdata_night(begdate, enddate, tradetype)
# date = datetime.date(2017,6,13)
# jsondata = pd.read_json(os.path.abspath('..') + '\marketdata\m_future_mkt_'+str(date.year)+'-'+str(date.month)+'-'+str(date.day) +'.json')
# db_data = orgnise_data(codename,{date:jsondata})


engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
table = Table('futures_mktdata_daily', metadata, autoload=True)

# Delete
for dt in ds2.keys():
    data = ds2[dt]
    db_data = orgnise_data_night(dt,data)
    try:
        conn.execute(table.insert(), db_data)
    except Exception as e:
        print(dt)
        print(e)
        continue

for dt in ds.keys():
    data = ds[dt]
    db_data = orgnise_data_night(dt,data)
    try:
        conn.execute(table.insert(), db_data)
    except Exception as e:
        print(dt)
        print(e)
        continue

