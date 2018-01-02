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
evalDate = datetime.date(2017,12,8)
ql_evalDate = ql.Date(evalDate.day,evalDate.month,evalDate.year)
rf = 0.03
engineType = 'AnalyticEuropeanEngine'
dt = 1.0/12
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
evaluation = Evaluation(ql_evalDate,daycounter,calendar)
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
df_option = df_option[df_option['pct_implied_vol'] > 0 ].reset_index()
print(len(df_option))


df_option_call = df_option[df_option['cd_option_type'] == 'call' ].reset_index()
print(df_option_call)
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

black_var_surface = ql.BlackVarianceSurface(ql_evalDate, calendar,ql_maturities,
                                            strikes,matrix, daycounter)
print(strikes)
vol_t1 = black_var_surface.blackVol(0.03,2.8)
print(vol_t1)

plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})

plot_years = np.arange(0.1,0.4,0.01)
plot_strikes = np.arange(strikes[0],strikes[-1],0.01)
fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))
surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.2)
ax.set_xlabel('strikes')
ax.set_ylabel('maturities')
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()
