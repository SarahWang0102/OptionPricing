from sqlalchemy import create_engine, MetaData, Table, Column
from WindPy import w
import datetime


def wind_data_equity_index(windcode,date,id_instrument):
    db_data = []
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
                  'code_instrument': windcode,
                  'amt_price': price,
                  'amt_trading_volume': volume,
                  'amt_trading_value': trading_value,
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data
