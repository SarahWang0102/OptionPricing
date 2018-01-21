from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mpl_toolkits.axes_grid1 import host_subplot
from matplotlib.dates import date2num
import matplotlib.dates as mdates
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
FutureMkt = dbt.FutureMkt
OptionMkt = dbt.OptionMkt
Options = dbt.Options

# Eval Settings
dt_date = datetime.date(2018, 1, 19)  # Set as Friday
dt_last_week = datetime.date(2018, 1, 12)
evalDate = dt_date.strftime("%Y-%m-%d")  # Set as Friday
start_date = w.tdaysoffset(-1, evalDate, "Period=M").Data[0][0].strftime("%Y-%m-%d")
hist_date = datetime.date(2017, 1, 1).strftime("%Y-%m-%d")
evalDate_1week = w.tdaysoffset(-1, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
evalDate_2week = w.tdaysoffset(-2, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
evalDate_3week = w.tdaysoffset(-3, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 11})
flagNight = 0
nameCode = 'sr'
contracts = ['1803', '1805', '1807', '1809']
core_instrumentid = 'sr_1805'

################################ 当日成交持仓量 #################################################
query_volume = sess.query(options_mkt.c.dt_date,
                          options_mkt.c.cd_option_type,
                          options_mkt.c.amt_strike,
                          options_mkt.c.amt_holding_volume,
                          options_mkt.c.amt_trading_volume,
                          options_mkt.c.amt_close,
                          options_mkt.c.pct_implied_vol
                          ) \
    .filter(or_(options_mkt.c.dt_date == evalDate,options_mkt.c.dt_date == dt_last_week)) \
    .filter(options_mkt.c.id_underlying == core_instrumentid)



df_2d = pd.read_sql(query_volume.statement, query_volume.session.bind)
df = df_2d[df_2d['dt_date'] == dt_date].reset_index()
df_lw = df_2d[df_2d['dt_date'] == dt_last_week].reset_index()
df_call = df[df['cd_option_type']=='call'].reset_index()
df_put = df[df['cd_option_type']=='put'].reset_index()
dflw_call = df_lw[df_lw['cd_option_type']=='call'].reset_index()
dflw_put = df_lw[df_lw['cd_option_type']=='put'].reset_index()
call_deltas = []
put_deltas = []
for idx,row in df_call.iterrows():
    row_put = df_put.loc[idx]
    strike = row['amt_strike']
    rowlw_call = dflw_call[dflw_call['amt_strike'] == strike]
    rowlw_put = dflw_put[dflw_put['amt_strike'] == strike]
    last_holding_call = 0.0
    last_holding_put = 0.0
    try:
        last_holding_call = rowlw_call['amt_holding_volume'].values[0]
    except:
        pass
    try:
        last_holding_put = rowlw_put['amt_holding_volume'].values[0]
    except:
        pass
    call_delta = row['amt_holding_volume']- last_holding_call
    put_delta = row_put['amt_holding_volume']- last_holding_put
    call_deltas.append(call_delta)
    put_deltas.append(put_delta)
w = 30
strikes = df_call['amt_strike'].tolist()
strikes1 = df_call['amt_strike']+w
holding_call = df_call['amt_holding_volume'].tolist()
holding_put = df_put['amt_holding_volume'].tolist()
trading_call = df_call['amt_trading_volume'].tolist()
trading_put = df_put['amt_trading_volume'].tolist()
dataset = [holding_call,holding_put,trading_call,trading_put]

df_results = pd.DataFrame({
    '0 call iv':df_call['pct_implied_vol'].tolist(),
    '1 call delta_holding':call_deltas,
    '2 call holding':df_call['amt_holding_volume'].tolist(),
    '3 call trading':df_call['amt_trading_volume'].tolist(),
    '4 call price':df_call['amt_close'].tolist(),
    '5 strikes':df_put['amt_strike'].tolist(),
    '6 put price': df_put['amt_close'].tolist(),
    '7 put trading': df_put['amt_trading_volume'].tolist(),
    '8 put holding': df_put['amt_holding_volume'].tolist(),
    '9 put delta_holding': put_deltas,
    '91 put iv': df_put['pct_implied_vol'].tolist()
})
df_results.to_csv('../save_figure/sr_holdings_'+evalDate+'.csv')

ldgs = ['持仓量（看涨）','持仓量（看跌）','成交量（看涨）','成交量（看跌）']

f3, ax3 = plt.subplots()
# for cont2, y in enumerate(dataset):
#     pu.plot_line(ax3, cont2, strikes, y, ldgs[cont2], '日期', '波动率（%）')
p1 = ax3.bar(strikes, holding_call,width=w, color=pu.colors[0])
p2 = ax3.bar(strikes1, holding_put,width=w, color=pu.colors[1])
p3, = ax3.plot(strikes, trading_call, color=pu.colors[2], linestyle=pu.lines[2], linewidth=2)
p4, = ax3.plot(strikes, trading_put, color=pu.colors[3], linestyle=pu.lines[3], linewidth=2)

ax3.legend([p1,p2,p3,p4],ldgs,bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
           ncol=2, mode="expand", borderaxespad=0.,frameon=False)
ax3.spines['top'].set_visible(False)
ax3.spines['right'].set_visible(False)
ax3.yaxis.set_ticks_position('left')
ax3.xaxis.set_ticks_position('bottom')
f3.savefig('../save_figure/sr_holdings_' + evalDate + '.png', dpi=300,
             format='png',bbox_inches='tight')

################################# 成交持仓认沽认购比P/C #################################################
query_volume = sess.query(options_mkt.c.dt_date, options_mkt.c.cd_option_type,
                          func.sum(options_mkt.c.amt_holding_volume).label('total_holding_volume'),
                          func.sum(options_mkt.c.amt_trading_volume).label('total_trading_volume')
                          ) \
    .filter(options_mkt.c.dt_date <= evalDate) \
    .filter(options_mkt.c.dt_date >= start_date) \
    .filter(options_mkt.c.name_code == nameCode) \
    .group_by(options_mkt.c.cd_option_type, options_mkt.c.dt_date)

query_future = sess.query(futures_mkt.c.dt_date, futures_mkt.c.amt_close.label('future_close')) \
    .filter(futures_mkt.c.dt_date <= evalDate) \
    .filter(futures_mkt.c.dt_date >= start_date) \
    .filter(futures_mkt.c.id_instrument == core_instrumentid)

df = pd.read_sql(query_volume.statement, query_volume.session.bind)
df_future = pd.read_sql(query_future.statement, query_future.session.bind)
print(df)
# print(df_future)

df_call = df[df['cd_option_type'] == 'call'].reset_index()
df_put = df[df['cd_option_type'] == 'put'].reset_index()
pc_ratio = []
for idx, row in df_call.iterrows():
    row_put = df_put[df_put['dt_date'] == row['dt_date']]
    pcr_trading = row_put['total_trading_volume'].values[0] / row['total_trading_volume']
    pcr_holding = row_put['total_holding_volume'].values[0] / row['total_holding_volume']
    pc_ratio.append({'dt_date': row['dt_date'], 'pcr_trading': pcr_trading, 'pcr_holding': pcr_holding})

df_pcr = pd.DataFrame(pc_ratio)
# print(df_pcr)

df_pcr = df_pcr.join(df_future.set_index('dt_date'), on='dt_date')
print(df_pcr[df_pcr['dt_date'] == dt_date])
print(df_pcr)
dates  =df_pcr['dt_date'].tolist()
datesnum = [date2num(date) for date in dates]
dates = [date.strftime("%d/%m/%Y") for date in dates]
xticks = np.arange(min(datesnum),max(datesnum),(max(datesnum)-min(datesnum))/len(datesnum))
fig1 = plt.figure()
host = host_subplot(111)
par = host.twinx()
ldgs = [ '持仓量P/C', '成交量P/C','期货价格（左）']

p1, = par.plot(df_pcr['dt_date'].tolist(), df_pcr['pcr_holding'].tolist(),
        color = pu.colors[0], linestyle = pu.lines[0], linewidth = 2)
p2, = par.plot(df_pcr['dt_date'].tolist(), df_pcr['pcr_trading'].tolist(),
        color=pu.colors[1], linestyle=pu.lines[1], linewidth=2)
p3, = host.plot(df_pcr['dt_date'].tolist(), df_pcr['future_close'].tolist(),
        color=pu.colors[2], linestyle=pu.lines[2], linewidth=2)
host.legend([p1,p2,p3],ldgs,bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
            ncol=3, mode="expand", borderaxespad=0.,frameon=False)
host.spines['top'].set_visible(False)
host.yaxis.set_ticks_position('left')
host.xaxis.set_ticks_position('bottom')
plt.setp(host,xticks = xticks,xticklabels=dates)
# host.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m/%Y"))
for label in host.get_xmajorticklabels():
    label.set_rotation(270)
    label.set_horizontalalignment("right")
fig1.savefig('../save_figure/sr_holdings_pcr_' + evalDate + '.png', dpi=300,
             format='png',bbox_inches='tight')
plt.show()
