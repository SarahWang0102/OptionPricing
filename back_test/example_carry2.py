import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import QuantLib as ql
from WindPy import w
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
from back_test.account import Account


# start_date = datetime.date(2015, 12, 31)
start_date = datetime.date(2016, 3, 27)
end_date = datetime.date(2016, 5, 31)
# end_date = datetime.date(2017, 12, 31)
# evalDate = datetime.date(2017, 6, 21)

rf = 0.03
engineType = 'AnalyticEuropeanEngine'
dt = 1.0 / 12
init_fund = 10000
hp = 1 # week

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
Option_mkt = dbt.OptionMkt
carry = Table('carry', metadata2, autoload=True)
options = dbt.Options

w.start()
calendar = ql.China()
daycounter = ql.ActualActual()
fund = init_fund



query = sess2.query(carry)
df_carry = pd.read_sql(query.statement,query.session.bind)
query_optioninfo = sess.query(options)
df_optioninfo = pd.read_sql(query_optioninfo.statement,query_optioninfo.session.bind)
# print(df_carry)

df_carry = df_carry[df_carry['amt_carry'] != -999.0].reset_index()

date_range = w.tdays(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "Period=W").Data[0]

bkt = Account()
# net_values = []
# df_trading_book = pd.DataFrame()
# df_open_trades = pd.DataFrame()
evalDate = start_date
while evalDate < end_date:
    evalDate = w.tdaysoffset(1, evalDate, "Period=W").Data[0][0].date()
    mdt_next = w.tdaysoffset(1, evalDate, "Period=W").Data[0][0].date()
    df_metric = df_carry[df_carry['dt_date']==evalDate]
    df_put = df_metric[df_metric['cd_option_type']=='put']
    df_call = df_metric[df_metric['cd_option_type']=='call']\
                .sort_values(by='amt_carry',ascending=False).reset_index()
    df_call_t5 = df_call.loc[0:4]
    df_call_b5 = df_call.loc[len(df_call)-5:]
    print(df_call_t5)
    print(df_call_b5)

    # 平仓：持有期限为hp
    realized_earning = 0.0
    if len(bkt.df_holdings) != 0:
        for (idx,row) in bkt.df_holdings.iterrows():
            id_instrument = row['id_instrument']
            long_short = row['long_short']
            idx_carry = (df_carry['id_instrument']==id_instrument)&(df_carry['dt_date']==evalDate)
            mkt_price = df_carry[idx_carry]['amt_option_price'].values[0]
            mdt = df_carry[idx_carry]['dt_maturity']
            multiplier = df_optioninfo[df_optioninfo['id_instrument']==id_instrument]['nbr_multiplier'].values[0]
            if mdt <= mdt_next or mdt_next>=end_date:
                bkt.liquidite_position(evalDate, id_instrument,mkt_price)
            else:
                if long_short==1 and id_instrument in df_call_t5['id_instrument']:continue
                if long_short==-1 and id_instrument in df_call_b5['id_instrument']: continue
                bkt.liquidite_position(evalDate,id_instrument,mkt_price)

    # 开仓/调仓：
    if mdt_next < end_date:
        cash = bkt.cash
        n=1+2+3+4+5
        for (idx,row) in df_call_t5.iterrows():
            id_instrument = row['id_instrument']
            mkt_price = row['amt_option_price']
            trading_fund = cash*float(n-idx-1)/n
            if id_instrument in bkt.df_holdings['id_instrument']:
                bkt.adjust_unit(evalDate,id_instrument,mkt_price,trading_fund)
            else:
                bkt.open_long(evalDate,id_instrument,mkt_price,trading_fund)

        for (idx,row) in df_call_b5.iterrows():
            id_instrument = row['id_instrument']
            mkt_price = row['amt_option_price']
            trading_fund = cash*float(n-idx-1)/n
            if id_instrument in bkt.df_holdings['id_instrument']:
                bkt.adjust_unit(evalDate,id_instrument,mkt_price,trading_fund)
            else:
                bkt.open_short(evalDate,id_instrument,mkt_price,trading_fund)

    df_metric = df_carry[df_carry['dt_date']==evalDate]
    bkt.mkm_update(evalDate,df_metric)
    print(bkt.df_account)































































