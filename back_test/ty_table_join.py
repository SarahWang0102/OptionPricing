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
engine2 = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/metrics', echo=False)
conn2 = engine2.connect()
metadata2 = MetaData(engine2)
Session2 = sessionmaker(bind=engine2)
sess2 = Session2()
Index_mkt = dbt.IndexMkt
Option_mkt = dbt.OptionMkt
option_intd = dbt.OptionMktIntraday
carry1 = Table('carry1', metadata2, autoload=True)
options = dbt.Options
calendar = ql.China()
daycounter = ql.ActualActual()
fund = init_fund
open_trades = []
query_mkt = sess.query(Option_mkt.dt_date,
                        Option_mkt.id_instrument,
                        Option_mkt.code_instrument,
                        Option_mkt.amt_close,
                        Option_mkt.amt_settlement,
                        Option_mkt.amt_last_close,
                        Option_mkt.amt_last_settlement,
                        Option_mkt.amt_trading_volume
                          ) \
    .filter(Option_mkt.dt_date >= start_date) \
    .filter(Option_mkt.dt_date <= end_date) \
    .filter(Option_mkt.datasource == 'wind')

df_mkt = pd.read_sql(query_mkt.statement, query_mkt.session.bind)

print(df_mkt.loc[0,'amt_last_close'])

if df_mkt.loc[0,'amt_last_close'] == None:
    print('T')