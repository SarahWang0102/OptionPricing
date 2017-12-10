from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
import datetime
import pandas as pd
from WindPy import w
from data_access.db_tables import DataBaseTables as dbt

w.start()
engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
options_mkt = Table('options_mktdata', metadata, autoload=True)
futures_mkt = Table('futures_mktdata', metadata, autoload=True)
futuremkt_table = dbt.FutureMkt
optionmkt_table = dbt.OptionMkt

# Eval Settings
start_date = datetime.date(2017, 3, 31).strftime("%Y-%m-%d")
end_date = datetime.date(2017, 12, 8).strftime("%Y-%m-%d")
hist_date = datetime.date(2017, 1, 1).strftime("%Y-%m-%d")
hist_date = w.tdaysoffset(1, hist_date, "").Data[0][0].date().strftime("%Y-%m-%d")
print(hist_date)
flagNight = 0
nameCode = 'm'
evalDate = start_date

# Get core contract mktdata
data = w.wsd("SR.CZC", "trade_hiscode", hist_date, end_date, "")
underlyingdata = pd.DataFrame({'date':data.Times,'id_core':data.Data[0]})
print(underlyingdata)

futuredata = sess.query(futuremkt_table)\
    .filter(futuremkt_table.dt_date >= hist_date)\
    .filter(futuremkt_table.dt_date <= end_date)\
    .filter(futuremkt_table.name_code == nameCode).all()


# optiondata = sess.query(optionmkt_table).filter(optionmkt_table.dt_date == evalDate)\
#     .filter(optionmkt_table.datasource == 'dce')\
#     .filter(optionmkt_table.flag_night == flagNight).all()
# print(optiondata)
#
# futuredata = sess.query(futuremkt_table)\
#     .filter(futuremkt_table.dt_date >= hist_date)\
#     .filter(futuremkt_table.dt_date <= end_date)\
#     .filter(futuremkt_table.name_code == nameCode).all()
# print(futuredata)

# res = sess.query(optionmkt_table,futuremkt_table)\
#     .join(futuremkt_table, optionmkt_table.id_underlying==futuremkt_table.id_instrument)\
#     .filter(optionmkt_table.dt_date == evalDate)\
#     .filter(futuremkt_table.dt_date == evalDate)\
#     .filter(optionmkt_table.datasource == 'dce')\
#     .all()
#
# print(res)