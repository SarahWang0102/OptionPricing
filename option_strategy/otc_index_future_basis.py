from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mpl_toolkits.mplot3d import Axes3D
import matplotlib as mpl
from matplotlib import cm as plt_cm
from mpl_toolkits.axes_grid1 import host_subplot
import datetime
import pandas as pd
import numpy as np
from WindPy import w
from data_access.db_tables import DataBaseTables as dbt
import matplotlib.pyplot as plt
from Utilities.PlotUtil import PlotUtil
import QuantLib as ql

###########################################################################################
w.start()
pu = PlotUtil()
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 11})
engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
index_mkt = Table('indexes_mktdata', metadata, autoload=True)
future_mkt = Table('futures_mktdata', metadata, autoload=True)
FutureMkt = dbt.FutureMkt
IndexMkt = dbt.IndexMkt
index_ids = ['index_300sh','index_50sh','index_500sh']
future_codes = ['IF','IH','IC']
index_names = ['沪深300指数','上证50指数','中证500指数']
# indexid = 'index_300sh'
# futurescode = 'IF'
############################################################################################
# Eval Settings
eval_date = datetime.date(2017, 12, 22)
evalDate = eval_date.strftime("%Y-%m-%d")

hist_date = datetime.date(2016, 1, 1)

#############################################################################################
for idx_index,indexid in enumerate(index_ids):
    futurescode = future_codes[idx_index]
    data = w.wsd(futurescode+'.CFE', "trade_hiscode", hist_date.strftime('%Y-%m-%d'), evalDate.strftime('%Y-%m-%d'), "")
    id_cores = []
    for idx,dt in enumerate(data.Times):
        name = data.Data[0][idx]
        id_core = name[0:2] + "_" + name[2:6]
        id_cores.append({'dt_date':dt,'id_instrument':id_core})
    future_df = pd.DataFrame(id_cores)
    query_index = sess.query(IndexMkt.id_instrument,IndexMkt.dt_date,IndexMkt.amt_close)\
        .filter(IndexMkt.dt_date >= hist_date)\
        .filter(IndexMkt.dt_date <= evalDate)

    query_future = sess.query(FutureMkt.id_instrument,FutureMkt.dt_date,FutureMkt.amt_close)\
        .filter(FutureMkt.dt_date >= hist_date)\
        .filter(FutureMkt.dt_date <= evalDate)\
        .filter(FutureMkt.flag_night == -1)\
        .filter(FutureMkt.datasource == 'wind')\
        .filter(FutureMkt.name_code == futurescode[0:2])


    index_df = pd.read_sql(query_index.statement,query_index.session.bind)
    futuremkt_df = pd.read_sql(query_future.statement,query_future.session.bind)
    # print(index_df)
    # print(futuremkt_df)
    indexsh_df = index_df[index_df['id_instrument']==indexid].reset_index()
    indexsh_df = indexsh_df.rename(columns = {'id_instrument':'id_index','amt_close':'amt_index_price'})

    future_df = future_df.merge(futuremkt_df,left_on=['id_instrument','dt_date'],right_on=['id_instrument','dt_date'],
                                how='left')
    future_df = future_df.rename(columns = {'id_instrument':'id_future','amt_close':'amt_future_price'})

    basis_df = future_df.join(indexsh_df.set_index('dt_date'),on='dt_date',how='left')
    basis_df['basis'] = basis_df['amt_index_price']-basis_df['amt_future_price']
    basis_df['pct_basis'] = basis_df['basis']/basis_df['amt_index_price']

    basis_df_c = basis_df[basis_df['dt_date']==eval_date]
    print(indexid,' basis : ',basis_df_c)
    x = basis_df['dt_date'].tolist()
    basis_set = [basis_df['amt_future_price'].tolist(),
                basis_df['amt_index_price'].tolist(),
                basis_df['basis'].tolist()]
    indexname = index_names[idx_index]
    ldgs = [futurescode+'主力合约价格', indexname+'价格', '基差(右)']

    fig1 = plt.figure()
    host = host_subplot(111)
    par = host.twinx()
    host.set_xlabel("日期")
    p1, = host.plot(x, basis_set[0], label=ldgs[0],color=pu.colors[0],linestyle=pu.lines[0], linewidth=2)
    p2, = host.plot(x, basis_set[1], label=ldgs[1],color=pu.colors[1],linestyle=pu.lines[1], linewidth=2)
    # basis_max = max(basis_set[2])
    par.fill_between(x, 0, basis_set[2],label=ldgs[2],color=pu.colors[2])

    host.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
               ncol=3, mode="expand", borderaxespad=0.)
    fig1.set_size_inches((8, 6))
    fig1.savefig('../save_figure/otc_basis_' + indexid + '_' + str(hist_date) + ' - ' + str(evalDate) + '.png', dpi=300,
               format='png')

plt.show()