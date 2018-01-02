from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mpl_toolkits.mplot3d import Axes3D
from mpl_toolkits.axes_grid1 import host_subplot

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
IndexMkt = dbt.IndexMkt

# Eval Settings
evalDate = datetime.date(2017, 12, 28).strftime("%Y-%m-%d")  # Set as Friday
start_date = datetime.date(2017,10, 28).strftime("%Y-%m-%d")

query = sess.query(IndexMkt.dt_date,IndexMkt.id_instrument,IndexMkt.amt_close)\
    .filter(IndexMkt.dt_date >= start_date)\
    .filter(IndexMkt.dt_date <= evalDate)\
    .filter(IndexMkt.id_instrument != 'index_50etf')

df = pd.read_sql(query.statement,query.session.bind)
print(df)

df_300sh = df[df['id_instrument']=='index_300sh'].reset_index()
df_50sh = df[df['id_instrument']=='index_50sh'].reset_index()
df_500sh = df[df['id_instrument']=='index_500sh'].reset_index()
df_vix = df[df['id_instrument']=='index_cvix'].reset_index()

dates = []
yield_300sh = []
yield_50sh = []
yield_500sh = []
for idx, row in df_300sh.iterrows():
    if idx == 0 : continue
    dates.append(row['dt_date'])
    r300 = (df_300sh.loc[idx,'amt_close']-df_300sh.loc[idx-1,'amt_close'])/df_300sh.loc[idx-1,'amt_close']
    r50 = (df_50sh.loc[idx,'amt_close']-df_50sh.loc[idx-1,'amt_close'])/df_50sh.loc[idx-1,'amt_close']
    r500 = (df_500sh.loc[idx,'amt_close']-df_500sh.loc[idx-1,'amt_close'])/df_500sh.loc[idx-1,'amt_close']
    yield_300sh.append(r300)
    yield_50sh.append(r50)
    yield_500sh.append(r500)


vix = df_vix['amt_close'].tolist()

fig1 = plt.figure()
host = host_subplot(111)
par = host.twinx()
host.set_xlabel("日期")
par.set_ylabel("")
ldgs = ['IVIX（右）','上证50收益率']
p1, = host.plot(dates, yield_50sh, label=ldgs[1], color=pu.colors[1], linestyle=pu.lines[1], linewidth=2)
# p2, = host.plot(dates, yield_50sh, label=ldgs[2], color=pu.colors[2], linestyle=pu.lines[2], linewidth=2)
# p3, = host.plot(dates, yield_500sh, label=ldgs[3], color=pu.colors[3], linestyle=pu.lines[3], linewidth=2)
p4, = par.plot(df_vix['dt_date'].tolist(), vix, label=ldgs[0], color=pu.colors[0], linestyle=pu.lines[0], linewidth=2)

host.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
            ncol=2, mode="expand", borderaxespad=0.)
fig1.set_size_inches((10, 6))
fig1.savefig('../save_figure/indexes_vix_yield_2M.png', dpi=300,
             format='png')

plt.show()