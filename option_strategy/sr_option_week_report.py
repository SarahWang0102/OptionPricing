from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
from matplotlib import cm as plt_cm
import datetime
import pandas as pd
import numpy as np
from WindPy import w
from data_access.db_tables import DataBaseTables as dbt
import matplotlib.pyplot as plt
from Utilities.PlotUtil import PlotUtil
import QuantLib as ql

w.start()
pu = PlotUtil()
engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
options_mkt = Table('options_mktdata', metadata, autoload=True)
futures_mkt = Table('futures_mktdata', metadata, autoload=True)
options = Table('option_contracts', metadata, autoload=True)
futuremkt_table = dbt.FutureMkt
optionmkt_table = dbt.OptionMkt
options_table = dbt.Options

# Eval Settings
evalDate = datetime.date(2018, 1, 19).strftime("%Y-%m-%d")  # Set as Friday
start_date = w.tdaysoffset(-1, evalDate, "Period=M").Data[0][0].strftime("%Y-%m-%d")
hist_date = w.tdaysoffset(-2, evalDate, "Period=Y").Data[0][0].strftime("%Y-%m-%d")
# hist_date = w.tdaysoffset(-60, start_date, "").Data[0][0].strftime("%Y-%m-%d")
# hist_date = datetime.date(2017, 1, 1).strftime("%Y-%m-%d")
evalDate_1week = w.tdaysoffset(-1, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
evalDate_2week = w.tdaysoffset(-2, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
evalDate_3week = w.tdaysoffset(-3, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
evalDate_4week = w.tdaysoffset(-4, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
evalDate_5week = w.tdaysoffset(-5, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
flagNight = 0
nameCode = 'sr'
contracts = ['1803', '1805', '1807', '1809']

# print(optionivs_df['date'].unique())

################ # ATM Implied Vols

dates = [evalDate, evalDate_1week, evalDate_2week, evalDate_3week,evalDate_4week,evalDate_5week]
optiondata_df = pd.DataFrame()
columns = [
    'date', 'id_instrument', 'implied_vol', 'contract_month',
    'option_type', 'strike', 'underlying_price', 'atm_dif']
optiondata_atm_df = pd.DataFrame(columns=columns)
idx_o = 0
for date in dates:
    optiondataset = sess.query(optionmkt_table, options_table, futuremkt_table) \
        .join(futuremkt_table, optionmkt_table.id_underlying == futuremkt_table.id_instrument) \
        .join(options_table, optionmkt_table.id_instrument == options_table.id_instrument) \
        .filter(optionmkt_table.dt_date == date) \
        .filter(optionmkt_table.datasource == 'czce') \
        .filter(futuremkt_table.dt_date == date) \
        .filter(futuremkt_table.name_code == nameCode) \
        .all()

    contract_months = []
    for optiondata in optiondataset:
        if optiondata.Options.cd_option_type == 'put': continue
        if optiondata.Options.name_contract_month not in contracts: continue
        optiondata_df.loc[idx_o, 'date'] = date
        optiondata_df.loc[idx_o, 'id_instrument'] = optiondata.OptionMkt.id_instrument
        optiondata_df.loc[idx_o, 'implied_vol'] = optiondata.OptionMkt.pct_implied_vol
        optiondata_df.loc[idx_o, 'contract_month'] = optiondata.Options.name_contract_month
        optiondata_df.loc[idx_o, 'option_type'] = optiondata.Options.cd_option_type
        optiondata_df.loc[idx_o, 'strike'] = optiondata.Options.amt_strike
        optiondata_df.loc[idx_o, 'underlying_price'] = optiondata.FutureMkt.amt_settlement
        optiondata_df.loc[idx_o, 'atm_dif'] = abs(
            optiondata.Options.amt_strike - optiondata.FutureMkt.amt_settlement)
        cm = optiondata.Options.name_contract_month
        if optiondata.Options.name_contract_month not in contract_months:
            # if cm[-1] not in ['1', '5', '9']: continue
            contract_months.append(optiondata.Options.name_contract_month)
        idx_o += 1

    for cm1 in contract_months:
        c = optiondata_df['contract_month'].map(lambda x: x == cm1)
        c1 = optiondata_df['date'].map(lambda x: x == date)
        critiron = c & c1
        df = optiondata_df[critiron]
        idx = df['atm_dif'].idxmin()
        optiondata_atm_df = optiondata_atm_df.append(df.loc[idx], ignore_index=True)
print('atm_implied_vols')
print(optiondata_atm_df)
f1, ax1 = plt.subplots()
cont = 0
for d in dates:
    c2 = optiondata_atm_df['date'].map(lambda a: a == d)
    df = optiondata_atm_df[c2]
    pu.plot_line(ax1, cont, df['contract_month'], df['implied_vol'], d, '合约月份', '波动率(%)')
    cont += 1
ax1.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
           ncol=3, mode="expand", borderaxespad=0.,frameon=False)
f1.savefig('../save_figure/implied_vols_' + str(evalDate) + '.png', dpi=300, format='png')

#################### Futures and Realised Vol
# Get core contract mktdata
data = w.wsd("SR.CZC", "trade_hiscode", hist_date, evalDate, "")
underlying_df = pd.DataFrame({'date': data.Times, 'code_core': data.Data[0]})

futuredataset = sess.query(futuremkt_table) \
    .filter(futuremkt_table.dt_date >= hist_date) \
    .filter(futuremkt_table.dt_date <= evalDate) \
    .filter(futuremkt_table.name_code == nameCode).all()

id_instruments = []
future_closes = []

for idx in underlying_df.index:
    row = underlying_df.loc[idx]
    dt_date = row['date']
    code_instrument = row['code_core']
    id_instrument = 'sr_1' + code_instrument[2:5]
    id_instruments.append(id_instrument)
    amt_close = 0.0
    for future in futuredataset:
        if future.dt_date == dt_date and future.id_instrument == id_instrument:
            amt_close = future.amt_settlement
    future_closes.append(amt_close)
underlying_df['id_core'] = id_instruments
underlying_df['price'] = future_closes

future_yields = []
for idx_c, price in enumerate(future_closes):
    if idx_c == 0:
        r = 0.0
    else:
        price = float(price)
        future_close = float(future_closes[idx_c - 1])
        if price == 0.0 or future_close == 0.0: r = 0.0
        else : r = np.log(price/future_close)
    future_yields.append(r)
underlying_df['yield'] = future_yields
underlying_df = underlying_df[underlying_df['yield'] != 0.0].reset_index()
# print(underlying_df)

histvols_6 = []
histvols_3 = []
histvols_2 = []
histvols_1 = []
for idx_v in range(121, len(underlying_df['price'])):
    histvols_6.append(np.std(underlying_df['yield'][idx_v - 120:idx_v]) * np.sqrt(252) * 100)
    histvols_3.append(np.std(underlying_df['yield'][idx_v - 60:idx_v]) * np.sqrt(252) * 100)
    histvols_2.append(np.std(underlying_df['yield'][idx_v - 40:idx_v]) * np.sqrt(252) * 100)
    histvols_1.append(np.std(underlying_df['yield'][idx_v - 20:idx_v]) * np.sqrt(252) * 100)
underlying_df.loc[121:, 'histvol_6'] = histvols_6
underlying_df.loc[121:, 'histvol_3'] = histvols_3
underlying_df.loc[121:, 'histvol_2'] = histvols_2
underlying_df.loc[121:, 'histvol_1'] = histvols_1
# print(underlying_df)
volcone_df = pd.DataFrame()
max_vols = [max(histvols_6), max(histvols_3), max(histvols_2), max(histvols_1)]
min_vols = [min(histvols_6), min(histvols_3), min(histvols_2), min(histvols_1)]
median_vols = [np.median(histvols_6), np.median(histvols_3), np.median(histvols_2),
               np.median(histvols_1)]
p75_vols = [np.percentile(histvols_6, 75), np.percentile(histvols_3, 75),
            np.percentile(histvols_2, 75), np.percentile(histvols_1, 75)]
p25_vols = [np.percentile(histvols_6, 25), np.percentile(histvols_3, 25),
            np.percentile(histvols_2, 25), np.percentile(histvols_1, 25)]
current_vols = [histvols_6[-1], histvols_3[-1], histvols_2[-1], histvols_1[-1]]
print('current_vols : ', current_vols)
histvolcone = [current_vols, max_vols, min_vols, median_vols, p75_vols, p25_vols]
x = [6, 3, 2, 1]
histvols = []
f2, ax2 = plt.subplots()
ldgs = ['当前水平', '最大值', '最小值', '中位数', '75分位数', '25分位数']
for cont2, y in enumerate(histvolcone):
    pu.plot_line(ax2, cont2, x, y, ldgs[cont2], '时间：月', '波动率（%）')
ax2.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
           ncol=4, mode="expand", borderaxespad=0.,frameon=False)
f2.savefig('../save_figure/hist_vols_' + str(evalDate) + '.png', dpi=300, format='png')

################ #Implied Vol Surface
# dates_week = w.tdays(w.tdaysoffset(-5, evalDate, "").Data[0][0].strftime("%Y-%m-%d"),evalDate, "").Data[0]
# date_a_week = w.tdaysoffset(-5, evalDate, "").Data[0][0].strftime("%Y-%m-%d")
dates_week = [evalDate,w.tdaysoffset(-5, evalDate, "").Data[0][0].strftime("%Y-%m-%d")]
# idx_ivs = 0
black_var_surfaces = []
for dt in dates_week:
    optionivs_df = pd.DataFrame()
    date = evalDate
    dt_eval = datetime.datetime.strptime(evalDate, '%Y-%m-%d').date()
    ql_evalDate = ql.Date(dt_eval.day, dt_eval.month, dt_eval.year)
    calendar = ql.China()
    daycounter = ql.ActualActual()
    optiondataset = sess.query(optionmkt_table, options_table) \
        .join(options_table, optionmkt_table.id_instrument == options_table.id_instrument) \
        .filter(optionmkt_table.dt_date == date) \
        .filter(optionmkt_table.datasource == 'czce') \
        .all()
    contract_months = []
    idx_ivs = 0
    for optiondata in optiondataset:
        if optiondata.Options.cd_option_type == 'put': continue
        if optiondata.Options.name_contract_month not in contracts: continue
        optionivs_df.loc[idx_ivs, 'id_instrument'] = optiondata.OptionMkt.id_instrument
        optionivs_df.loc[idx_ivs, 'pct_implied_vol'] = float(optiondata.OptionMkt.pct_implied_vol)
        optionivs_df.loc[idx_ivs, 'dt_maturity'] = optiondata.Options.dt_maturity
        optionivs_df.loc[idx_ivs, 'amt_strike'] = float(optiondata.Options.amt_strike)
        idx_ivs += 1

    maturities = optionivs_df['dt_maturity'].unique()
    strikes = optionivs_df['amt_strike'].unique()
    volset = []
    year_fracs = []
    core_strikes = []
    ql_maturities = []
    for k in strikes:
        nbr_k = len(optionivs_df[optionivs_df['amt_strike'].map(lambda x: x == k)])
        if nbr_k == maturities.size:
            core_strikes.append(k)
    for dt_m in maturities:
        c0 = optionivs_df['dt_maturity'].map(lambda x: x == dt_m)
        volset.append(optionivs_df[c0]['pct_implied_vol'].values.tolist())
        year_fracs.append((dt_m - dt_eval).days / 365.0)
        ql_maturities.append(ql.Date(dt_m.day, dt_m.month, dt_m.year))

    implied_vols = ql.Matrix(len(core_strikes), len(maturities))
    for i in range(implied_vols.rows()):
        for j in range(implied_vols.columns()):
            implied_vols[i][j] = volset[j][i]
    plot_years = np.arange(min(year_fracs), max(year_fracs), 0.01)
    plot_strikes = np.arange(min(core_strikes), max(core_strikes), 10.0)
    black_var_surface = ql.BlackVarianceSurface(
        ql_evalDate, calendar, ql_maturities, core_strikes, implied_vols,
        daycounter)
    black_var_surfaces.append(black_var_surface)

fig1 = plt.figure()
ax_ivs = fig1.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([black_var_surfaces[0].blackVol(y, x)
              for xr, yr in zip(X, Y)
              for x, y in zip(xr, yr)]
             ).reshape(len(X), len(X[0]))
Z5 = np.array([black_var_surfaces[1].blackVol(y, x)
              for xr, yr in zip(X, Y)
              for x, y in zip(xr, yr)]
             ).reshape(len(X), len(X[0]))
Z_hist = np.array([current_vols[-1]
               for xr, yr in zip(X, Y)
               for x, y in zip(xr, yr)]
              ).reshape(len(X), len(X[0]))
surf = ax_ivs.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=plt_cm.coolwarm, linewidth=0.1)
ax_ivs.plot_surface(X, Y, Z_hist, rstride=1, cstride=1, cmap=plt_cm.coolwarm, linewidth=0.1)

fake2Dline = mpl.lines.Line2D([0], [0], linestyle="none", c='r', marker='s')
fake2Dline2 = mpl.lines.Line2D([0], [0], linestyle="none", c='b', marker='s')
ax_ivs.legend([fake2Dline, fake2Dline2], ['隐含波动率', '已实现波动率'], numpoints=1)
ax_ivs.set_xlabel('行权价')
ax_ivs.set_ylabel('期限')
ax_ivs.set_zlabel('波动率（%）')
fig1.colorbar(surf, shrink=0.5, aspect=5)

fig2 = plt.figure()
ax_ivs2 = fig2.gca(projection='3d')
surf2 = ax_ivs2.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=plt_cm.coolwarm, linewidth=0.1)
# ax_ivs2.plot_surface(X, Y, Z5, rstride=1, cstride=1, color='b', linewidth=0.1)
# ax_ivs2.legend([fake2Dline, fake2Dline2], ['当前隐含波动率', '上周隐含波动率'], numpoints=1)
ax_ivs2.set_xlabel('行权价')
ax_ivs2.set_ylabel('期限')
ax_ivs2.set_zlabel('波动率（%）')
fig2.colorbar(surf2, shrink=0.5, aspect=5)


fig1.savefig('../save_figure/iv_surface_' + str(evalDate) + '.png', dpi=300, format='png')
fig2.savefig('../save_figure/iv_surface_2_' + str(evalDate) + '.png', dpi=300, format='png')
plt.show()
