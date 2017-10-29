from sqlalchemy import create_engine, MetaData, Table, Column
from WindPy import w

w.start()


def row_data(idinstruemnt, datetime, close):
    rows = []
    for idx, dt in enumerate(datetime):
        row = {'datetime': dt, 'id_instrument': idinstruemnt, 'close': close[idx]}
        rows.append(row)
    return rows

def batch_insert_winddata(conn,table,begdate,enddate):
    data = w.wsi("510050.SH", "close", begdate + " 09:30:00", enddate + " 15:01:00", "Fill=Previous")
    closes = data.Data[0]
    datetimes = data.Times
    rows = row_data('510050.SH', datetimes, closes)
    conn.execute(table.insert(), rows)

engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)

table = Table('stock_index_intraday', metadata, autoload=True)


batch_insert_winddata(conn,table,begdate="2017-07-06",enddate="2017-07-06")


