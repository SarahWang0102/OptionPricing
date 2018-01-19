import pandas as pd
import QuantLib as ql
import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt


# start_date = datetime.date(2015, 3, 31)
start_date = datetime.date(2017, 10, 1)
end_date = datetime.date(2017, 10, 10)
# end_date = datetime.date(2017, 12, 31)
# evalDate = datetime.date(2017, 6, 21)

rf = 0.03
engineType = 'AnalyticEuropeanEngine'
dt = 1.0 / 12
init_fund = 10000

engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
engine2 = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata', echo=False)
conn2 = engine2.connect()
metadata2 = MetaData(engine2)
Session2 = sessionmaker(bind=engine2)
sess2 = Session2()
Index_mkt = dbt.IndexMkt
Option_mkt = dbt.OptionMkt
option_intd = dbt.OptionMktIntraday
opt_mkt = Table('options_mktdata', metadata2, autoload=True)
opt_mkt_old = Table('options_mktdata_old', metadata2, autoload=True)


query_mkt = sess.query(opt_mkt_old) \
    .filter(Option_mkt.id_underlying != 'index_50etf')\
    .filter(Option_mkt.dt_date == '2018-01-19')

df_mkt = pd.read_sql(query_mkt.statement, query_mkt.session.bind)
for (idx,row) in df_mkt.iterrows():
    dic_mkt = row.to_dict()

    print(dic_mkt)

