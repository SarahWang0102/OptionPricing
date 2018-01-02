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
indexmkt_table = dbt.IndexMkt
index_ids = ['index_300sh','index_50sh','index_500sh']
############################################################################################
# Eval Settings
eval_date = datetime.date(2017, 12, 28)
evalDate = eval_date.strftime("%Y-%m-%d")

hist_date = datetime.date(2016, 1, 1).strftime("%Y-%m-%d")

#############################################################################################


query_index = sess.query(indexmkt_table.id_instrument,indexmkt_table.dt_date,indexmkt_table.amt_close)\
    .filter(indexmkt_table.dt_date >= hist_date)\
    .filter(indexmkt_table.dt_date <= evalDate)\

index_df = pd.read_sql(query_index.statement,query_index.session.bind)

for indexid in index_ids:

    index300sh_df = index_df[index_df['id_instrument']==indexid].reset_index(drop=True)
    for (idx,row) in index300sh_df.iterrows():
        if idx == 0: r=0.0
        else:
            r = np.log(float(row['amt_close']) / float(index300sh_df.loc[idx-1,'amt_close']))
        index300sh_df.loc[idx,'yield'] = r

    for idx_v in range(len(index300sh_df)):
        if idx_v >= 120:
            index300sh_df.loc[idx_v,'histvol_120'] = np.std(index300sh_df['yield'][idx_v-120:idx_v])*np.sqrt(252)*100
        if idx_v >= 60:
            index300sh_df.loc[idx_v,'histvol_60'] = np.std(index300sh_df['yield'][idx_v-60:idx_v])*np.sqrt(252)*100
        if idx_v >= 20:
            index300sh_df.loc[idx_v,'histvol_20'] = np.std(index300sh_df['yield'][idx_v-20:idx_v])*np.sqrt(252)*100
        if idx_v >= 10:
            index300sh_df.loc[idx_v,'histvol_10'] = np.std(index300sh_df['yield'][idx_v-10:idx_v])*np.sqrt(252)*100
        if idx_v >= 5:
            index300sh_df.loc[idx_v,'histvol_5'] = np.std(index300sh_df['yield'][idx_v-5:idx_v])*np.sqrt(252)*100

    # print(index300sh_df)
    volcone_df = pd.DataFrame()
    histvols_60 = index300sh_df['histvol_120'].dropna().tolist()
    histvols_30 = index300sh_df['histvol_60'].dropna().tolist()
    histvols_20 = index300sh_df['histvol_20'].dropna().tolist()
    histvols_10 = index300sh_df['histvol_10'].dropna().tolist()
    histvols_5 = index300sh_df['histvol_5'].dropna().tolist()
    max_vols = [max(histvols_60),max(histvols_30),max(histvols_20),max(histvols_10),max(histvols_5)]
    min_vols = [min(histvols_60), min(histvols_30), min(histvols_20), min(histvols_10),min(histvols_5)]
    median_vols = [np.median(histvols_60), np.median(histvols_30), np.median(histvols_20),
                   np.median(histvols_10),np.median(histvols_5)]
    p75_vols = [np.percentile(histvols_60, 75), np.percentile(histvols_30, 75),
                np.percentile(histvols_20, 75), np.percentile(histvols_10, 75), np.percentile(histvols_5, 75)]
    p25_vols = [np.percentile(histvols_60, 25), np.percentile(histvols_30, 25),
                np.percentile(histvols_20, 25), np.percentile(histvols_10, 25), np.percentile(histvols_5, 25)]
    # print(evalDate)
    index300sh_df_c = index300sh_df[index300sh_df['dt_date']==eval_date]
    current_vols = [float(index300sh_df_c['histvol_120']),
                    float(index300sh_df_c['histvol_60']),
                    float(index300sh_df_c['histvol_20']),
                    float(index300sh_df_c['histvol_10']),
                    float(index300sh_df_c['histvol_5'])]
    print(indexid,' current_vols : ', current_vols)
    histvolcone = [current_vols, max_vols, min_vols, median_vols, p75_vols, p25_vols]
    x = [120, 60, 20, 10, 5]
    x_labels = ['1W', '2W', '1M', '3M', '6M']

    f2, ax2 = plt.subplots()
    ldgs = ['当前水平', '最大值', '最小值', '中位数', '75分位数', '25分位数']
    for cont2, y in enumerate(histvolcone):
        pu.plot_line(ax2, cont2, x, y, ldgs[cont2], '时间窗口', '波动率（%）')
    ax2.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
               ncol=4, mode="expand", borderaxespad=0.)
    ax2.set_xticks([5,10,20,60,120])
    ax2.set_xticklabels(x_labels)
    f2.set_size_inches((8, 6))
    f2.savefig('../save_figure/otc_histvols_'+indexid+'_' + str(hist_date)+' - '+ str(evalDate) + '.png', dpi=300, format='png')



plt.show()

