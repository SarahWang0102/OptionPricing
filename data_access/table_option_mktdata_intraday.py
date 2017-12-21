from sqlalchemy import create_engine, MetaData, Table, Column
from WindPy import w
import datetime
import pandas as pd
import math


def wind_option_chain(datestr):
    optionchain = w.wset("optionchain", "date=" + datestr + ";us_code=510050.SH;option_var=全部;call_put=全部")
    df_optionchain = pd.DataFrame()
    for i, f in enumerate(optionchain.Fields):
        df_optionchain[f] = optionchain.Data[i]
    return df_optionchain


def wind_data_50etf_option_intraday(datestr, df_optionchain_row):
    db_data = []
    datasource = 'wind'
    windcode = df_optionchain_row['option_code']
    amt_strike = df_optionchain_row['strike_price']
    contract_month = str(df_optionchain_row['month'])[-4:]
    sec_name = df_optionchain_row['option_name']
    if df_optionchain_row['call_put'] == '认购':
        cd_option_type = 'call'
    elif df_optionchain_row['call_put'] == '认沽':
        cd_option_type = 'put'
    if sec_name[-1] == 'A':
        id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6] + '_A'
    else:
        id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]
    data = w.wsi(windcode, "close,volume,amt", datestr + " 09:00:00", datestr + " 15:01:00", "Fill=Previous")
    datetimes = data.Times
    prices = data.Data[0]
    volumes = data.Data[1]
    trading_values = data.Data[2]
    for idx, dt in enumerate(datetimes):
        price = prices[idx]
        volume = volumes[idx]
        trading_value = trading_values[idx]
        if math.isnan(price): continue
        if math.isnan(volume): volume = 0.0
        if math.isnan(trading_value): trading_value = 0.0
        db_row = {'dt_datetime': dt,
                  'id_instrument': id_instrument,
                  'datasource': datasource,
                  'code_instrument': windcode,
                  'amt_price': price,
                  'amt_trading_volume': volume,
                  'amt_trading_value': trading_value,
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data

# engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata_intraday',
#                        echo=False)
# conn = engine.connect()
# metadata = MetaData(engine)
# equity_index_intraday = Table('equity_index_mktdata_intraday', metadata, autoload=True)
#
# class Equity_index_intraday(object):
#     pass
#
#

# w.start()
# begdate="2017-07-06"
# enddate="2017-07-06"
# windcode = "510050.SH"
# engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata_intraday',
#                        echo=False)
# conn = engine.connect()
# metadata = MetaData(engine)
#
# table = Table('equity_index_50etf_intraday', metadata, autoload=True)
# db_data = wind_data_50etf(windcode,begdate)
# try:
#     conn.execute(table.insert(), db_data)
# except Exception as e:
#     print(begdate)
#     print(e)


# data = w.wsi(windcode, "close,volume,amt", begdate + " 09:00:00", enddate + " 15:01:00", "Fill=Previous")
# # batch_insert_winddata(conn,table,begdate="2017-07-06",enddate="2017-07-06")
# print(data)
#
# dt_datetime = data.Times
# prices = data.Data[0]
# volumes = data.Data[1]
# values = data.Data[2]
