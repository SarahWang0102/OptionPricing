from sqlalchemy import create_engine, MetaData, Table, Column,TIMESTAMP
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from WindPy import w
import datetime
import pandas as pd
import math


def wind_option_codes(datestr):
    engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                           echo=False)
    FutureContracts = dbt.Futures
    Session = sessionmaker(bind=engine)
    sess = Session()
    query = sess.query(FutureContracts.id_instrument,FutureContracts.windcode) \
        .filter(datestr >= FutureContracts.dt_listed) \
        .filter(datestr <= FutureContracts.dt_maturity)
    df_windcode = pd.read_sql(query.statement, query.session.bind)
    return df_windcode


def wind_index_future_tick(datestr, id_instrument, windcode):
    db_data = []
    datasource = 'wind'
    tickdata = w.wst(windcode,
                     "last,volume,amt,oi,limit_up,limit_down,ask1,ask2,ask3,ask4,ask5,"
                     "bid1,bid2,bid3,bid4,bid5",datestr + " 09:25:00", datestr + " 15:01:00", "")
    if tickdata.ErrorCode != 0 :
        print('wind get data error ',datestr,',errorcode : ',tickdata.ErrorCode)
        return []
    df_tickdata = pd.DataFrame()
    for i, f in enumerate(tickdata.Fields):
        df_tickdata[f] = tickdata.Data[i]
    df_tickdata['dt_datetime'] = tickdata.Times
    df_tickdata = df_tickdata.fillna(0.0)
    last_datetime = None
    for (idx, row_tickdata) in df_tickdata.iterrows():
        dt = row_tickdata['dt_datetime']
        dt_datetime = datetime.datetime(dt.year,dt.month,dt.day,dt.hour,dt.minute,dt.second)
        if dt_datetime == last_datetime : continue
        last_datetime = dt_datetime
        price = row_tickdata['last']
        volume = row_tickdata['volume']
        trading_value = row_tickdata['amount']
        position = row_tickdata['position']
        amt_bid1 = row_tickdata['bid1']
        amt_ask1 = row_tickdata['ask1']
        amt_bid2 = row_tickdata['bid2']
        amt_ask2 = row_tickdata['ask2']
        amt_bid3 = row_tickdata['bid3']
        amt_ask3 = row_tickdata['ask3']
        amt_bid4 = row_tickdata['bid4']
        amt_ask4 = row_tickdata['ask4']
        amt_bid5 = row_tickdata['bid5']
        amt_ask5 = row_tickdata['ask5']
        db_row = {'dt_datetime': dt_datetime,
                  'id_instrument': id_instrument,
                  'datasource': datasource,
                  'code_instrument': windcode,
                  'amt_price': price,
                  'amt_trading_volume': volume,
                  'amt_trading_value': trading_value,
                  'amt_holding_volume': position,
                  'amt_bid1': amt_bid1,
                  'amt_ask1': amt_ask1,
                  'amt_bid2': amt_bid2,
                  'amt_ask2': amt_ask2,
                  'amt_bid3': amt_bid3,
                  'amt_ask3': amt_ask3,
                  'amt_bid4': amt_bid4,
                  'amt_ask4': amt_ask4,
                  'amt_bid5': amt_bid5,
                  'amt_ask5': amt_ask5,
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data

#
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
