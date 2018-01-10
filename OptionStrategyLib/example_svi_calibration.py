import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import pickle
import QuantLib as ql
from WindPy import w
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from OptionStrategyLib.calibration import SVICalibration
w.start()

##################################################################################################
evalDate = datetime.date(2017,12,8)
ql_evalDate = ql.Date(evalDate.day,evalDate.month,evalDate.year)
rf = 0.03
##################################################################################################

engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
options_mkt = Table('options_mktdata', metadata, autoload=True)
futures_mkt = Table('futures_mktdata', metadata, autoload=True)
options = Table('option_contracts', metadata, autoload=True)
Index_mkt = dbt.IndexMkt
Option_mkt = dbt.OptionMkt
Option_contracts = dbt.Options
svicalibration = SVICalibration(evalDate)
calendar = ql.China()
daycounter = ql.ActualActual()
ql.Settings.instance().evaluationDate = ql_evalDate
##################################################################################################
query_option = sess.query(Option_mkt.id_instrument,
                          Option_mkt.cd_option_type,
                          Option_mkt.amt_strike,
                          Option_contracts.dt_maturity,
                          Option_mkt.amt_close,
                          Option_mkt.pct_implied_vol)\
                    .join(Option_contracts,Option_mkt.id_instrument==Option_contracts.id_instrument)\
                    .filter(Option_mkt.dt_date == evalDate)\
                    .filter(Option_mkt.flag_night == -1)\
                    .filter(Option_mkt.datasource == 'wind')

query_etf = sess.query(Index_mkt.amt_close)\
                .filter(Index_mkt.dt_date == evalDate)\
                .filter(Index_mkt.id_instrument == 'index_50etf')

df_option = pd.read_sql(query_option.statement,query_option.session.bind)
df_option = df_option[df_option['id_instrument'].str[-1] != 'A']
df_50etf = pd.read_sql(query_etf.statement,query_etf.session.bind)
df_option['underlying_prices'] = [df_50etf['amt_close'].iloc[0]]*len(df_option)
df_option['risk_free_rates'] = [rf]*len(df_option)
# df_option['add'] = df_option['id_instrument'][-1]

for (idx,row) in df_option.iterrows():
    optiontype = row['cd_option_type']
    if optiontype == 'call': ql_optiontype = ql.Option.Call
    else: ql_optiontype = ql.Option.Put
    id = row['id_instrument']
    mdt = row['dt_maturity']
    ql_mdt = ql.Date(mdt.day,mdt.month,mdt.year)
    strike = row['amt_strike']
    spot = row['underlying_prices']
    close = row['amt_close']
    exercise = ql.EuropeanExercise(ql_mdt)
    payoff = ql.PlainVanillaPayoff(ql_optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)
    flat_vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql_evalDate, calendar, 0.0, daycounter))
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_evalDate, 0.0, daycounter))
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_evalDate, row['risk_free_rates'], daycounter))
    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,
                                           flat_vol_ts)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))

    try:
        implied_vol = option.impliedVolatility(close, process, 1.0e-4, 300, 0.0, 10.0)
    except RuntimeError:
        implied_vol = 0.0
    df_option['pct_implied_vol'].loc[idx] = implied_vol

print(df_option)
df_option = df_option[df_option['pct_implied_vol'] > 0 ]
# c1 = (df_option['cd_option_type'] == 'call') & (df_option['amt_strike']>=df_option['underlying_prices'])
# c2 = (df_option['cd_option_type'] == 'put') & (df_option['amt_strike']<=df_option['underlying_prices'])
# df_option = df_option[c1|c2]

df_option = df_option[df_option['cd_option_type']=='call']
params_dict = svicalibration.calibrate_rawsvi(df_option['amt_strike'],
                                              df_option['dt_maturity'],
                                              df_option['underlying_prices'],
                                              df_option['amt_close'],
                                              df_option['pct_implied_vol'],
                                              df_option['risk_free_rates'])
print(params_dict)






