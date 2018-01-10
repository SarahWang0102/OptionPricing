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
start_date = datetime.date(2017,7,21)
end_date = datetime.date(2017,7,28)
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
calendar = ql.China()
daycounter = ql.ActualActual()

##################################################################################################
trading_book = []
df_open_trades = pd.DataFrame()
date_rage = w.tdays(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "Period=D").Data[0]
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
                              Option_mkt.amt_holding_volume,
                              Option_mkt.pct_implied_vol,
                              Option_contracts.nbr_multiplier)\
                        .join(Option_contracts,Option_mkt.id_instrument==Option_contracts.id_instrument)\
                        .filter(Option_mkt.dt_date == evalDate)\
                        .filter(Option_mkt.flag_night == -1)\
                        .filter(Option_mkt.datasource == 'wind')
    query_etf = sess.query(Index_mkt.amt_close)\
                    .filter(Index_mkt.dt_date == evalDate)\
                    .filter(Index_mkt.id_instrument == 'index_50etf')

    df_option = pd.read_sql(query_option.statement,query_option.session.bind)
    # print('No of options : ',len(df_option))
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

    df_option = df_option[df_option['cd_option_type'] == 'call' ].reset_index()
    # print('No of calls : ',len(df_option))
    maturity_dates = df_option['dt_maturity'].unique().tolist()
    print('maturity_dates : ', maturity_dates)
    print('df_option')
    print(df_option)
    df_option = df_option[df_option['nbr_multiplier']==10000]
    ##############################################################################################
    ql_maturities = []
    maturity_dates = df_option['dt_maturity'].unique().tolist()
    print('maturity_dates : ',maturity_dates)

    df_mdt1 = df_option[df_option['dt_maturity'] == maturity_dates[0]][['dt_maturity','pct_implied_vol','amt_strike']]\
        .set_index('amt_strike').rename(columns={'dt_maturity':'dt_maturity_1','pct_implied_vol':'pct_implied_vol_1'})
    df_mdt2 = df_option[df_option['dt_maturity'] == maturity_dates[1]][['dt_maturity','pct_implied_vol','amt_strike']]\
        .set_index('amt_strike').rename(columns={'dt_maturity':'dt_maturity_2','pct_implied_vol':'pct_implied_vol_2'})
    df_mdt3 = df_option[df_option['dt_maturity'] == maturity_dates[2]][['dt_maturity','pct_implied_vol','amt_strike']]\
        .set_index('amt_strike').rename(columns={'dt_maturity':'dt_maturity_3','pct_implied_vol':'pct_implied_vol_3'})
    if len(maturity_dates) == 4 :
        df_mdt4 = df_option[df_option['dt_maturity'] == maturity_dates[3]][['dt_maturity','pct_implied_vol','amt_strike']]\
            .set_index('amt_strike').rename(columns={'dt_maturity':'dt_maturity_4','pct_implied_vol':'pct_implied_vol_4'})

    if len(maturity_dates) == 4:
        df_vol = pd.concat([df_mdt1,df_mdt2,df_mdt3,df_mdt4],axis=1,join='inner')
    else:
        df_vol = pd.concat([df_mdt1, df_mdt2, df_mdt3], axis=1, join='inner')
    # print('df_vol')
    # print(df_vol)
    # print(df_vol['dt_maturity_2'])
    strikes = df_vol.index.tolist()
    # print(strikes)
    vol1 = df_vol['pct_implied_vol_1'].tolist()
    # matrix = ql.Matrix(len(strikes), len(maturity_dates))
    volset = [df_vol['pct_implied_vol_1'].tolist(),
              df_vol['pct_implied_vol_2'].tolist(),
              df_vol['pct_implied_vol_3'].tolist()]
    if len(maturity_dates) == 4: volset.append(df_vol['pct_implied_vol_4'].tolist())

#     # print(matrix)
#     for mdate in maturity_dates:
#         c1 = df_option['dt_maturity'] == mdate
#         implied_vols = df_option[c1]['pct_implied_vol'].tolist()
#         if len(strikes) == 0 : strikes = df_option[c1]['amt_strike'].tolist()
#         ql_maturities.append(ql.Date(mdate.day,mdate.month,mdate.year))
#         volset.append(implied_vols)
#     matrix = ql.Matrix(len(strikes), len(maturity_dates))
#     vol_bvs = []
#     for i in range(matrix.rows()):
#         for j in range(matrix.columns()):
#             matrix[i][j] = volset[j][i]
#     print(ql_maturities)
#     black_var_surface = ql.BlackVarianceSurface(ql_evalDate, calendar,ql_maturities,strikes,matrix, daycounter)
#
#     ##############################################################################################
#     carry_results = []
#     for (idx,row) in df_option.iterrows():
#         optiontype = row['cd_option_type']
#         if optiontype == 'call': ql_optiontype = ql.Option.Call
#         else: ql_optiontype = ql.Option.Put
#         if row['amt_strike'] not in strikes : continue
#         mdt = row['dt_maturity']
#         ql_mdt = ql.Date(mdt.day, mdt.month, mdt.year)
#         strike = row['amt_strike']
#         spot = row['underlying_price']
#         close = row['amt_close']
#         euro_option = OptionPlainEuropean(strike, ql_mdt, ql_optiontype)
#         option_metrics = OptionMetrics(euro_option)
#         implied_vol = option_metrics.implied_vol(evaluation, rf, spot, close)
#         theta = option_metrics.theta(evaluation,rf, spot, close,engineType,implied_vol)
#         vega = option_metrics.vega(evaluation,rf, spot, close,engineType,implied_vol)
#         ttm = (mdt-evalDate).days/365.0
#         if ttm <= dt : continue
#         try:
#             implied_vol_t1 = black_var_surface.blackVol(ttm-dt,strike)
#             option_carry = (-theta + vega * (implied_vol_t1 - implied_vol)) / close - rf
#             df_option.loc[idx,'option_carry'] = option_carry
#         except Exception as e :
#             print(e)
#     df_call_carry = df_option.dropna().sort_values(by='option_carry', ascending=False)
#
#     df_buy = df_call_carry[:4]
#     df_sell = df_call_carry[-4:]
#
#     # 平仓
#     total_earning = 0
#     if len(df_open_trades) != 0:
#         for (idx,row) in df_open_trades.iterrows():
#             df = df_option[df_option['id_instrument'] == row['id_instrument']]
#             # close = df['close']
#             # print(df)
#             # print(df['amt_close'].values[0])
#             # print(row['amt_cost'])
#             earning = df['amt_close'].values[0] - row['amt_cost']
#             # df_open_trades.loc[idx,'amt_earning'] = earning
#             total_earning += earning
#     # total_earning = sum(df_open_trades['amt_earning'])
#     # print(total_earning)
#     fund += total_earning
#     # print('df_open_trades')
#     # print(df_open_trades)
#
#     # 开仓
#     amt_weight = fund / 8.0
#     for (i,row) in df_buy.iterrows():
#         trade = {
#             'dt_trade_start': evalDate,
#             'id_instrument': row['id_instrument'],
#             'flag_open': True,
#             'cd_trade_type': 1, # buy
#             'amt_cost': row['amt_close'],
#             'amt_unit': amt_weight/row['amt_close'],
#             'amt_earning': 0.0
#         }
#         open_trades.append(trade)
#     for (i,row) in df_sell.iterrows():
#         trade = {
#             'dt_trade_start': evalDate,
#             'id_instrument': row['id_instrument'],
#             'flag_open': True,
#             'cd_trade_type': -1, # sell
#             'amt_cost': row['amt_close'],
#             'amt_unit': amt_weight/row['amt_close'],
#             'amt_earning': 0.0
#         }
#         open_trades.append(trade)
#     df_open_trades = pd.DataFrame(open_trades)
#     # print(df_open_trades)
#     trading_book.append({'dt_date':evalDate,'net_value':fund/init_fund})
#     # trading_book.loc[idx_date,'dt_date'] = evalDate
#     # trading_book.loc[idx_date,'net_value'] = fund/init_fund
# # print(trading_book)
#
# for tb in trading_book:
#     print(tb['dt_date'],' : ',tb['net_value'])





