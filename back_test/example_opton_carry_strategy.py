import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import QuantLib as ql
import datetime
import os
import pickle
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from data_access.db_tables import DataBaseTables as dbt
from OptionStrategyLib.calibration import SVICalibration
from OptionStrategyLib.OptionPricing.Evaluation import Evaluation
from OptionStrategyLib.OptionPricing.OptionMetrics import OptionMetrics
from OptionStrategyLib.OptionPricing.Options import OptionPlainEuropean
from back_test.bkt_option import BktOption
from back_test.bkt_option_set import OptionSet


start_date = datetime.date(2017, 12, 28)
end_date = datetime.date(2017, 12, 31)
evalDate = datetime.date(2017, 6, 21)

rf = 0.03
engineType = 'AnalyticEuropeanEngine'
dt = 1.0 / 12
init_fund = 10000

engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
engine2 = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata_intraday', echo=False)
conn2 = engine2.connect()
metadata2 = MetaData(engine2)
Session2 = sessionmaker(bind=engine2)
sess2 = Session2()
Index_mkt = dbt.IndexMkt
Option_mkt = dbt.OptionMkt
option_intd = dbt.OptionMktIntraday
options = dbt.Options
calendar = ql.China()
daycounter = ql.ActualActual()

fund = init_fund
open_trades = []
query_intd = sess2.query(option_intd.dt_datetime,
                          option_intd.id_instrument,
                          option_intd.amt_close,
                          option_intd.amt_trading_volume
                          ) \
    .filter(option_intd.dt_datetime >= start_date) \
    .filter(option_intd.dt_datetime <= end_date) \
    .filter(option_intd.datasource == 'wind')

query_option = sess.query(options.id_instrument,
                          options.cd_option_type,
                          options.amt_strike,
                          options.dt_maturity,
                          options.nbr_multiplier) \
    .filter(and_(options.dt_listed <= end_date,options.dt_maturity >= start_date))


query_etf = sess.query(Index_mkt.dt_date,Index_mkt.amt_close) \
    .filter(Index_mkt.dt_date >= start_date) \
    .filter(Index_mkt.dt_date <= end_date) \
    .filter(Index_mkt.id_instrument == 'index_50etf')

df_mkt = pd.read_sql(query_intd.statement, query_intd.session.bind)
df_contract = pd.read_sql(query_option.statement, query_option.session.bind)
df_50etf = pd.read_sql(query_etf.statement, query_etf.session.bind).rename(columns={'amt_close':'underlying_price'})
df_option = df_mkt.join(df_contract.set_index('id_instrument'),how='left',on='id_instrument')
for (idx,row) in df_option.iterrows():
    df_option.loc[idx,'dt_date'] = row['dt_datetime'].date()
df_option = df_option.join(df_50etf.set_index('dt_date'),how='left',on='dt_date')
print(df_option)

# id_list = df_option['id_instrument'].unique()
# df_option1 = df_option[df_option['id_instrument'] == id_list[0]].reset_index()
# bkt_option = BktOption('daily', df_option1)
#
# bkt_option.start()
# df = bkt_option.current_state
# print(df)
#
# bkt_option.next()
# df = bkt_option.current_state
# print(df)
#
# bkt_option.reset()
# df = bkt_option.current_state
# print(df)


bkt_optionset = OptionSet('daily',df_option)

bkt_optionset.start()

bktoption_list = bkt_optionset.bktoption_list
print(bktoption_list)
print(bkt_optionset.start_date)
print(bkt_optionset.end_date)


bkt_optionset.next()


bktoption_list = bkt_optionset.bktoption_list
print(bktoption_list)

print(bkt_optionset.start_date)
print(bkt_optionset.end_date)

























