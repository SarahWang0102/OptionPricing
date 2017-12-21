from sqlalchemy import create_engine, MetaData, Table, Column
from WindPy import w
import datetime
import pandas as pd



def wind_data_index(windcode,date,id_instrument):
    db_data = []
    datasource = 'wind'
    data = w.wsd(windcode, "open,high,low,close,volume,amt",
                 date,date, "Fill=Previous")
    df = pd.DataFrame()
    for i, f in enumerate(data.Fields):
        df[f] = data.Data[i]
    df['times'] = data.Times
    for (idx, row) in df.iterrows():
        open_price = row['OPEN']
        dt = row['times']
        high = row['HIGH']
        low = row['LOW']
        close = row['CLOSE']
        volume = row['VOLUME']
        amt = row['AMT']
        db_row = {'dt_date': dt,
                  'id_instrument': id_instrument,
                  'datasource': datasource,
                  'code_instrument': windcode,
                  'amt_last_close': close,
                  'amt_open': open_price,
                  'amt_high': high,
                  'amt_low': low,
                  'amt_trading_volume': volume,
                  'amt_trading_value': amt,
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data
