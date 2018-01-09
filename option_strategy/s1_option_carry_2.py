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


def get_black_vol_surface():
    balck_vol_surface = None
    return balck_vol_surface


##################################################################################################
start_date = datetime.date(2017, 6, 21)
end_date = datetime.date(2017, 12, 22)
# evalDate = datetime.date(2017,12,8)

rf = 0.03
engineType = 'AnalyticEuropeanEngine'
dt = 1.0 / 12
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
net_values = []
df_trading_book = pd.DataFrame()
df_open_trades = pd.DataFrame()
date_rage = w.tdays(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "Period=W").Data[0]
for idx_date,date in enumerate(date_rage):
    evalDate = date.date()
    # evalDate = datetime.date(2017, 11, 28)
    ql_evalDate = ql.Date(evalDate.day, evalDate.month, evalDate.year)
    evaluation = Evaluation(ql_evalDate, daycounter, calendar)
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
                              Option_contracts.nbr_multiplier) \
        .join(Option_contracts, Option_mkt.id_instrument == Option_contracts.id_instrument) \
        .filter(Option_mkt.dt_date == evalDate) \
        .filter(Option_mkt.flag_night == -1) \
        .filter(Option_mkt.datasource == 'wind')
    query_etf = sess.query(Index_mkt.amt_close) \
        .filter(Index_mkt.dt_date == evalDate) \
        .filter(Index_mkt.id_instrument == 'index_50etf')

    df_option = pd.read_sql(query_option.statement, query_option.session.bind)
    df_50etf = pd.read_sql(query_etf.statement, query_etf.session.bind)
    df_option['underlying_price'] = [df_50etf['amt_close'].iloc[0]] * len(df_option)
    df_option['risk_free_rate'] = [rf] * len(df_option)
    for (idx, row) in df_option.iterrows():
        optiontype = row['cd_option_type']
        if optiontype == 'call':
            ql_optiontype = ql.Option.Call
        else:
            ql_optiontype = ql.Option.Put
        id = row['id_instrument']
        mdt = row['dt_maturity']
        ql_mdt = ql.Date(mdt.day, mdt.month, mdt.year)
        nbr_multiplier = row['nbr_multiplier']
        strike = round(row['amt_strike'] * nbr_multiplier / 10000, 2)
        spot = row['underlying_price']
        close = row['amt_close']
        euro_option = OptionPlainEuropean(strike, ql_mdt, ql_optiontype)
        option_metrics = OptionMetrics(euro_option)
        implied_vol = option_metrics.implied_vol(evaluation, rf, spot, close)
        df_option['pct_implied_vol'].loc[idx] = implied_vol
        df_option['amt_strike'].loc[idx] = strike
    df_option = df_option[df_option['dt_maturity'] > evalDate]
    df_option = df_option[df_option['cd_option_type'] == 'call'].reset_index()

    ##############################################################################################
    ql_maturities = []
    maturity_dates = df_option['dt_maturity'].unique().tolist()

    name_columes = ['dt_maturity', 'pct_implied_vol', 'amt_strike','amt_holding_volume']

    df_mdt1 = df_option[df_option['dt_maturity'] == maturity_dates[0]][name_columes] \
        .rename(columns={'pct_implied_vol': 'pct_implied_vol_1'})\
        .sort_values(by='amt_holding_volume', ascending=False)\
        .drop_duplicates(subset='amt_strike')\
        .set_index('amt_strike').sort_index()
    df_mdt2 = df_option[df_option['dt_maturity'] == maturity_dates[1]][name_columes] \
        .rename(columns={'pct_implied_vol': 'pct_implied_vol_2'})\
        .sort_values(by='amt_holding_volume', ascending=False)\
        .drop_duplicates(subset='amt_strike')\
        .set_index('amt_strike').sort_index()
    df_mdt3 = df_option[df_option['dt_maturity'] == maturity_dates[2]][name_columes] \
        .rename(columns={'pct_implied_vol': 'pct_implied_vol_3'})\
        .sort_values(by='amt_holding_volume', ascending=False)\
        .drop_duplicates(subset='amt_strike')\
        .set_index('amt_strike').sort_index()
    if len(maturity_dates) == 4:
        df_mdt4 = df_option[df_option['dt_maturity'] == maturity_dates[3]][name_columes] \
            .rename(columns={'pct_implied_vol': 'pct_implied_vol_4'})\
            .sort_values(by='amt_holding_volume', ascending=False)\
            .drop_duplicates(subset='amt_strike')\
            .set_index('amt_strike').sort_index()
    if len(maturity_dates) == 4:
        df_vol = pd.concat([df_mdt1, df_mdt2, df_mdt3, df_mdt4], axis=1, join='inner')
    else:
        df_vol = pd.concat([df_mdt1, df_mdt2, df_mdt3], axis=1, join='inner')
    strikes = df_vol.index.tolist()
    volset = [df_vol['pct_implied_vol_1'].tolist(),
              df_vol['pct_implied_vol_2'].tolist(),
              df_vol['pct_implied_vol_3'].tolist()]
    if len(maturity_dates) == 4:
        volset.append(df_vol['pct_implied_vol_4'].tolist())
    for mdate in maturity_dates:
        ql_maturities.append(ql.Date(mdate.day, mdate.month, mdate.year))
    vol_matrix = ql.Matrix(len(strikes), len(maturity_dates))
    for i in range(vol_matrix.rows()):
        for j in range(vol_matrix.columns()):
            vol_matrix[i][j] = volset[j][i]
    # print(ql_maturities)
    # print(vol_matrix)
    black_var_surface = ql.BlackVarianceSurface(
        ql_evalDate, calendar, ql_maturities, strikes, vol_matrix, daycounter)  #

    ##############################################################################################
    carry_results = []
    for (idx,row) in df_option.iterrows():
        optiontype = row['cd_option_type']
        if optiontype == 'call': ql_optiontype = ql.Option.Call
        else: ql_optiontype = ql.Option.Put
        if row['amt_strike'] not in strikes : continue
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
            option_carry = (-theta+vega*(implied_vol_t1-implied_vol))/close - rf
            df_option.loc[idx,'option_carry'] = option_carry
        except Exception as e :
            print(e)
    df_call_carry = df_option.dropna().sort_values(by='option_carry', ascending=False)

    df_buy = df_call_carry[:4]
    df_sell = df_call_carry[-4:]

    # 平仓
    total_earning = 0
    if len(df_open_trades) != 0:
        for (idx,row) in df_open_trades.iterrows():
            df = df_option[df_option['id_instrument'] == row['id_instrument']]
            earning = (df['amt_close'].values[0] - row['amt_cost'])*row['amt_unit']*row['cd_trade_type']
            df_open_trades.loc[idx,'amt_earning'] = earning
            df_open_trades.loc[idx,'dt_trade_end'] = evalDate
            df_open_trades.loc[idx,'flag_open'] = False
            df_open_trades.loc[idx,'amt_price'] = df['amt_close'].values[0]
            total_earning += earning
    fund += total_earning
    print('df_open_trades : ')
    print(df_open_trades)
    df_trading_book = df_trading_book.append(df_open_trades,ignore_index=True)
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

    net_values.append({'dt_date':evalDate,'net_value':fund/init_fund})
print(df_trading_book)
for tb in net_values:
    print(tb['dt_date'],' : ',tb['net_value'])
