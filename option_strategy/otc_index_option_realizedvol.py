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
engine1 = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata_intraday',echo=False)
engine2 = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata',echo=False)
metadata1 = MetaData(engine1)
Session1 = sessionmaker(bind=engine1)
sess1 = Session1()
metadata2 = MetaData(engine2)
Session2 = sessionmaker(bind=engine2)
sess2 = Session2()
index_intraday = Table('equity_index_mktdata_intraday', metadata1, autoload=True)
EquityIndexIntraday = dbt.EquityIndexIntraday
IndexMkt = dbt.IndexMkt
############################################################################################
# Eval Settings
evalDate = datetime.date(2017, 12, 22)
startDate = datetime.date(2017, 1, 1)
# hist_date = datetime.date(2016, 5, 1)
hist_date = w.tdaysoffset(-7, startDate, "Period=M").Data[0][0].date()
# index_ids = ['index_300sh','index_50sh','index_500sh']
index_ids = ['index_500sh']
#############################################################################################

for indexid in index_ids:

    query1 = sess1.query(EquityIndexIntraday.id_instrument,
                             EquityIndexIntraday.dt_datetime,
                             EquityIndexIntraday.amt_price) \
        .filter(EquityIndexIntraday.dt_datetime >= startDate) \
        .filter(EquityIndexIntraday.dt_datetime <= evalDate) \
        .filter(EquityIndexIntraday.id_instrument == indexid) \
        .filter(EquityIndexIntraday.datasource == 'wind')

    query2 = sess2.query(IndexMkt.id_instrument, IndexMkt.dt_date, IndexMkt.amt_close) \
        .filter(IndexMkt.dt_date >= hist_date) \
        .filter(IndexMkt.dt_date <= evalDate) \
        .filter(IndexMkt.id_instrument == indexid)

    query2_1 = sess2.query(IndexMkt.id_instrument, IndexMkt.dt_date, IndexMkt.amt_close) \
        .filter(IndexMkt.dt_date >= startDate) \
        .filter(IndexMkt.dt_date <= evalDate) \
        .filter(IndexMkt.id_instrument == 'index_cvix')


    intraday_df = pd.read_sql(query1.statement, query1.session.bind)
    index_df = pd.read_sql(query2.statement, query2.session.bind)
    cvix_df = pd.read_sql(query2_1.statement, query2_1.session.bind)


    for i in range(len(intraday_df)):
        intraday_df.loc[i, 'dt_date'] = intraday_df.loc[i, 'dt_datetime'].date()

    print(intraday_df)

    rv_dict = []
    date_range = w.tdays(startDate, evalDate, "").Data[0]
    for dt in date_range:
        date = dt.date()
        df = intraday_df[intraday_df['dt_date'] == date].reset_index()
        if len(df) == 0:
            print(dt, ' no data')
            continue
        yields = []
        for i in range(len(df)):
            if i == 0: continue
            r = np.log(float(df.loc[i, 'amt_price']) / float(df.loc[i - 1, 'amt_price']))
            yields.append(r)
        RV = 0.0
        for i in range(len(yields) - 1):
            RV += (yields[i + 1] - yields[i]) ** 2
        sigma = np.sqrt(RV * 252)*100
        rv_dict.append({'dt_date': date, 'intraday_vol': sigma})
    rv_df = pd.DataFrame(rv_dict)
    print(rv_df)



    for (idx, row) in index_df.iterrows():
        if idx == 0: r = 0.0
        else:
            r = np.log(float(row['amt_close']) / float(index_df.loc[idx - 1, 'amt_close']))
            index_df.loc[idx, 'yield'] = r

    for idx_v in range(len(index_df)):
        if idx_v >= 120:
            index_df.loc[idx_v, 'histvol_120'] = np.std(index_df['yield'][idx_v-120:idx_v])*np.sqrt(252)*100
        if idx_v >= 60:
            index_df.loc[idx_v, 'histvol_60'] = np.std(index_df['yield'][idx_v-60:idx_v])*np.sqrt(252)*100
        if idx_v >= 20:
            index_df.loc[idx_v, 'histvol_20'] = np.std(index_df['yield'][idx_v-20:idx_v])*np.sqrt(252)*100

    print(index_df)
    merged_df=rv_df.join(index_df.set_index('dt_date'),on='dt_date')
    mergedvix_df=rv_df.join(cvix_df.set_index('dt_date'),on='dt_date')

    print(merged_df)

    x = merged_df['dt_date'].tolist()
    vol_set = [merged_df['intraday_vol'].tolist(),
               merged_df['histvol_120'].tolist(),
               merged_df['histvol_60'].tolist(),
               merged_df['histvol_20'].tolist(),
               mergedvix_df['amt_close'].tolist()
               ]
    f2, ax2 = plt.subplots()
    ldgs = ['已实现波动率RV', '历史波动率6M', '历史波动率3M', '历史波动率1M','中国波指IVIX']
    for cont2, y in enumerate(vol_set):
        pu.plot_line(ax2, cont2, x, y, ldgs[cont2], '日期', '波动率（%）')
    ax2.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
               ncol=3, mode="expand", borderaxespad=0.)
    f2.savefig('../save_figure/otc_realizedvol_' + indexid + '_' + str(startDate) + ' - ' + str(evalDate) + '.png', dpi=300,
               format='png')

    # x = mergedvix_df['dt_date'].tolist()
    # vol_set = [mergedvix_df['intraday_vol'].tolist(),
    #            mergedvix_df['amt_close'].tolist()
    #            ]
    # f3, ax3 = plt.subplots()
    # ldgs = ['已实现波动率RV', '中国波指IVIX']
    # for cont2, y in enumerate(vol_set):
    #     pu.plot_line(ax3, cont2, x, y, ldgs[cont2], '日期', '波动率（%）')
    # ax3.legend(bbox_to_anchor=(0., 1.02, 1., .102), loc=3,
    #            ncol=3, mode="expand", borderaxespad=0.)
    # f3.savefig('../save_figure/otc_rv_ivix_' + indexid + '_' + str(startDate) + ' - ' + str(evalDate) + '.png', dpi=300,
    #            format='png')

plt.show()
















