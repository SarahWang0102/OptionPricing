import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
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
from OptionStrategyLib.OptionPricing.Evaluation import Evaluation
from OptionStrategyLib.OptionPricing.OptionMetrics import OptionMetrics
from OptionStrategyLib.OptionPricing.Options import OptionPlainEuropean
w.start()

##################################################################################################
start_date = datetime.date(2017,3,8)
end_date = datetime.date(2017,6,8)
# evalDate = datetime.date(2017,12,8)

rf = 0.03
engineType = 'AnalyticEuropeanEngine'
dt = 1.0/12
init_fund = 10000

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
# svicalibration = SVICalibration(evalDate)
calendar = ql.China()
daycounter = ql.ActualActual()

##################################################################################################
trading_book = pd.DataFrame()
df_open_trades = pd.DataFrame()
date_rage = w.tdays(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "Period=W").Data[0]
for idx_date,date in enumerate(date_rage):
    evalDate = date.date()
    ql_evalDate = ql.Date(evalDate.day, evalDate.month, evalDate.year)
    evaluation = Evaluation(ql_evalDate,daycounter,calendar)
    print(evalDate)
    fund = init_fund
    open_trades = []
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
    # df_option = df_option[df_option['id_instrument'].str[-1] != 'A']
    df_50etf = pd.read_sql(query_etf.statement,query_etf.session.bind)
    df_option['underlying_price'] = [df_50etf['amt_close'].iloc[0]]*len(df_option)
    df_option['risk_free_rate'] = [rf]*len(df_option)
    for (idx,row) in df_option.iterrows():
        optiontype = row['cd_option_type']
        if optiontype == 'call': ql_optiontype = ql.Option.Call
        else: ql_optiontype = ql.Option.Put
        id = row['id_instrument']
        mdt = row['dt_maturity']
        ql_mdt = ql.Date(mdt.day,mdt.month,mdt.year)
        strike = row['amt_strike']
        spot = row['underlying_price']
        close = row['amt_close']
        euro_option = OptionPlainEuropean(strike,ql_mdt,ql_optiontype)
        option_metrics = OptionMetrics(euro_option)
        implied_vol = option_metrics.implied_vol(evaluation, rf, spot, close)
        df_option['pct_implied_vol'].loc[idx] = implied_vol
        df_option['amt_strike'].loc[idx] = strike
    print(len(df_option))
    print('df_option : ')
    print(df_option)
    df_option = df_option[df_option['pct_implied_vol'] > 0 ].reset_index()
    print(len(df_option))
    df_option_call = df_option[df_option['cd_option_type'] == 'call' ].reset_index()

    ##############################################################################################

    ql_maturities = []
    volset = []
    strikes = []
    maturity_dates = df_option_call['dt_maturity'].unique().tolist()
    for mdate in maturity_dates:
        c1 = df_option_call['dt_maturity'] == mdate
        implied_vols = df_option_call[c1]['pct_implied_vol'].tolist()
        if len(strikes) == 0 : strikes = df_option_call[c1]['amt_strike'].tolist()
        ql_maturities.append(ql.Date(mdate.day,mdate.month,mdate.year))
        volset.append(implied_vols)
    matrix = ql.Matrix(len(strikes), len(maturity_dates))
    vol_bvs = []
    for i in range(matrix.rows()):
        for j in range(matrix.columns()):
            matrix[i][j] = volset[j][i]

    black_var_surface = ql.BlackVarianceSurface(ql_evalDate, calendar,ql_maturities,strikes,matrix, daycounter)

    ##############################################################################################
    # print(df_option_call)
    carry_results = []
    for (idx,row) in df_option_call.iterrows():
        optiontype = row['cd_option_type']
        if optiontype == 'call': ql_optiontype = ql.Option.Call
        else: ql_optiontype = ql.Option.Put
        mdt = row['dt_maturity']
        ql_mdt = ql.Date(mdt.day, mdt.month, mdt.year)
        strike = row['amt_strike']
        spot = row['underlying_price']
        close = row['amt_close']
        euro_option = OptionPlainEuropean(strike, ql_mdt, ql_optiontype)
        option_metrics = OptionMetrics(euro_option)
        implied_vol = option_metrics.implied_vol(evaluation, rf, spot, close)
        theta = option_metrics.theta(evaluation,rf, spot, close,engineType,implied_vol)
        vega = option_metrics.vega(evaluation,rf, spot, close,engineType,implied_vol)
        ttm = (mdt-evalDate).days/365.0
        if ttm <= dt : continue
        try:
            implied_vol_t1 = black_var_surface.blackVol(ttm-dt,strike)
            option_carry = (-theta + vega * (implied_vol_t1 - implied_vol)) / close - rf
            df_option_call.loc[idx,'option_carry'] = option_carry
        except Exception as e :
            print(e)
    print(df_option_call)
    df_call_carry = df_option_call.dropna().sort_values(by='option_carry', ascending=False)

    print(df_call_carry)

    df_buy = df_call_carry[:4]
    df_sell = df_call_carry[-4:]
    print(df_buy)
    print(df_sell)

    # 平仓
    if len(df_open_trades) != 0:
        for (idx,row) in df_open_trades.iterrows():
            df = df_option_call[df_option_call['id_instrument'] == row['id_instrument']]
            # close = df['close']
            earning = df['close'] - row['close']
            df_open_trades.loc[idx,'amt_earning'] = earning
    total_earning = sum(df_open_trades['amt_earning'])
    fund += total_earning
    print(df_open_trades)

    # 开仓
    amt_weight = fund / 8.0
    for (i,row) in df_buy.iterrows():
        trade = {
            'dt_trade_start': evalDate,
            'id_instrument': row['id_instrument'],
            'flag_open': True,
            'cd_trade_type': 1, # buy
            'amt_cost': row['amt_close'],
            'amt_unit': amt_weight/row['amt_close'],
            'amt_earning': 0.0
        }
        open_trades.append(trade)
    for (i,row) in df_sell.iterrows():
        trade = {
            'dt_trade_start': evalDate,
            'id_instrument': row['id_instrument'],
            'flag_open': True,
            'cd_trade_type': -1, # sell
            'amt_cost': row['amt_close'],
            'amt_unit': amt_weight/row['amt_close'],
            'amt_earning': 0.0
        }
        open_trades.append(trade)
    df_open_trades = pd.DataFrame(open_trades)
    print(df_open_trades)
    trading_book.loc[idx_date,'dt_date'] = evalDate
    trading_book.loc[idx_date,'net_value'] = fund/init_fund
print(trading_book)







