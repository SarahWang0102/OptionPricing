from sqlalchemy import create_engine, MetaData, Table, Column
from WindPy import w
import datetime


def wind_data_50etf(windcode,date):
    db_data = []
    id_instrument = 'index_50etf'
    datasource = 'wind'
    data = w.wsi(windcode, "close,volume,amt", date + " 09:00:00", date + " 15:01:00", "Fill=Previous")
    datetimes = data.Times
    prices = data.Data[0]
    volumes = data.Data[1]
    trading_values = data.Data[2]
    for idx, dt in enumerate(datetimes):
        price = prices[idx]
        volume = volumes[idx]
        trading_value = trading_values[idx]
        db_row = {'dt_datetime': dt,
                  'id_instrument': id_instrument,
                  'datasource': datasource,
                  'windcode': windcode,
                  'amt_price': price,
                  'amt_trading_volume': volume,
                  'amt_trading_value': trading_value,
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data

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