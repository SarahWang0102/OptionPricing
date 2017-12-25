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
futurescodes = ['IF.CFE','IH.CFE','IC.CFE']
indexid = 'index_300sh'
futurescode = 'IF.CFE'
############################################################################################
# Eval Settings
evalDate = datetime.date(2017, 12, 22)
hist_date = datetime.date(2016, 1, 1)

#############################################################################################
data = w.wsd(futurescode, "trade_hiscode", hist_date.strftime('%Y-%m-%d'), evalDate.strftime('%Y-%m-%d'), "")
id_cores = []
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:2] + "_" + name[2:6]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
future_df = pd.DataFrame(id_cores)
print(future_df)
query_index = sess.query(IndexMkt.id_instrument,IndexMkt.dt_date,IndexMkt.amt_close)\
    .filter(IndexMkt.dt_date >= hist_date)\
    .filter(IndexMkt.dt_date <= evalDate)\


index_df = pd.read_sql(query_index.statement,query_index.session.bind)

indexsh_df = index_df[index_df['id_instrument']==indexid].reset_index()

print(indexsh_df.set_index('dt_date'))
merged_df = future_df.merge(indexsh_df,left_on='dt_date',right_on='dt_date',how='left')
print(merged_df)
merged_df2 = future_df.join(indexsh_df.set_index('dt_date'),on='dt_date',how='left')
print(merged_df2)