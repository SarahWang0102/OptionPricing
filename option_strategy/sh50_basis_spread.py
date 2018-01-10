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
engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
options_mkt = Table('options_mktdata', metadata, autoload=True)
futures_mkt = Table('futures_mktdata', metadata, autoload=True)
options = Table('option_contracts', metadata, autoload=True)
index_mkt = Table('indexes_mktdata', metadata, autoload=True)
futuremkt_table = dbt.FutureMkt
optionmkt_table = dbt.OptionMkt
options_table = dbt.Options
indexmkt_table = dbt.IndexMkt
############################################################################################
# Eval Settings
evalDate = datetime.date(2017, 12, 22).strftime("%Y-%m-%d")  # Set as Friday
# start_date = w.tdaysoffset(-1, evalDate, "Period=M").Data[0][0].strftime("%Y-%m-%d")
# hist_date = w.tdaysoffset(-60, start_date, "").Data[0][0].strftime("%Y-%m-%d")
hist_date = datetime.date(2017, 1, 1).strftime("%Y-%m-%d")
# evalDate_1week = w.tdaysoffset(-1, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
# evalDate_2week = w.tdaysoffset(-2, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
# evalDate_3week = w.tdaysoffset(-3, evalDate, "Period=W").Data[0][0].strftime("%Y-%m-%d")
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 11})
flagNight = 0
nameCode = 'sr'
contracts = ['1803', '1805', '1807', '1809']
#############################################################################################

#################### Index Hist Vol and Realised Vol

query_index = sess.query(indexmkt_table.id_instrument,indexmkt_table.dt_date,indexmkt_table.amt_close)\
    .filter(indexmkt_table.dt_date >= hist_date)\
    .filter(indexmkt_table.dt_date <= evalDate)\

index_df = pd.read_sql(query_index.statement,query_index.session.bind)

# underlying_df = pd.DataFrame({'date': data.Times, 'code_core': data.Data[0]})

futuredataset = sess.query(futuremkt_table) \
    .filter(futuremkt_table.dt_date >= hist_date) \
    .filter(futuremkt_table.dt_date <= evalDate) \
    .filter(futuremkt_table.name_code == nameCode).all()

index300sh_df = index_df[index_df['id_instrument']=='index_300sh'].reset_index(drop=True)
for (idx,row) in index300sh_df.iterrows():
    if idx == 0: r=0.0
    else:
        r = np.log(float(row['amt_close']) / float(index300sh_df.loc[idx-1,'amt_close']))
    index300sh_df.loc[idx,'yield'] = r

for idx_v in range(61, len(index300sh_df)):
    index300sh_df.loc[idx_v,'histvol_60'] = np.std(index300sh_df['yield'][idx_v-60:idx_v])*np.sqrt(252)*100
    index300sh_df.loc[idx_v,'histvol_30'] = np.std(index300sh_df['yield'][idx_v-30:idx_v])*np.sqrt(252)*100
    index300sh_df.loc[idx_v,'histvol_20'] = np.std(index300sh_df['yield'][idx_v-20:idx_v])*np.sqrt(252)*100
    index300sh_df.loc[idx_v,'histvol_10'] = np.std(index300sh_df['yield'][idx_v-10:idx_v])*np.sqrt(252)*100
    index300sh_df.loc[idx_v,'histvol_5'] = np.std(index300sh_df['yield'][idx_v-5:idx_v])*np.sqrt(252)*100

index300sh_df = index300sh_df.loc[61:,:]
print(index300sh_df)
volcone_df = pd.DataFrame()
histvols_60 = index300sh_df['histvol_60'].tolist()
histvols_30 = index300sh_df['histvol_30'].tolist()
histvols_20 = index300sh_df['histvol_20'].tolist()
histvols_10 = index300sh_df['histvol_10'].tolist()
histvols_5 = index300sh_df['histvol_5'].tolist()
max_vols = [max(histvols_60), max(histvols_30), max(histvols_20), max(histvols_10),max(histvols_5)]
min_vols = [min(histvols_60), min(histvols_30), min(histvols_20), min(histvols_10),min(histvols_5)]
median_vols = [np.median(histvols_60), np.median(histvols_30), np.median(histvols_20),
               np.median(histvols_10),np.median(histvols_5)]
p75_vols = [np.percentile(histvols_60, 75), np.percentile(histvols_30, 75),
            np.percentile(histvols_20, 75), np.percentile(histvols_10, 75), np.percentile(histvols_5, 75)]
p25_vols = [np.percentile(histvols_60, 25), np.percentile(histvols_30, 25),
            np.percentile(histvols_20, 25), np.percentile(histvols_10, 25), np.percentile(histvols_5, 25)]
current_vols = [histvols_60[-1], histvols_30[-1], histvols_20[-1], histvols_10[-1],histvols_5[-1]]
print('current_vols : ', current_vols)
histvolcone = [current_vols, max_vols, min_vols, median_vols, p75_vols, p25_vols]
x = [60, 30, 20, 10, 5]

f2, ax2 = plt.subplots()
ldgs = ['当前水平', '最大值', '最小值', '中位数', '75分位数', '25分位数']
for cont2, y in enumerate(histvolcone):
    pu.plot_line(ax2, cont2, x, y, ldgs[cont2], '时间窗口', '波动率（%）')
ax2.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)
# f2.savefig('../save_figure/hist_vols_' + str(evalDate) + '.png', dpi=300, format='png')
plt.show()