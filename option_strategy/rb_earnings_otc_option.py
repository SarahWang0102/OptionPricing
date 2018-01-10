from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import datetime
import pandas as pd
from WindPy import w
from data_access.db_tables import DataBaseTables as dbt
from Utilities.PlotUtil import PlotUtil
import numpy as np
##################################################################################################
w.start()
engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
options_mkt = Table('options_mktdata', metadata, autoload=True)
futures_mkt = Table('futures_mktdata', metadata, autoload=True)
options = Table('option_contracts', metadata, autoload=True)
Future_mkt = dbt.FutureMkt
Option_mkt = dbt.OptionMkt
Options_c = dbt.Options
##################################################################################################


# Construct rb earnings index
# 钢厂利润指数 = 1单位螺纹钢主力合约价格-1.65单位铁矿石(I)主力合约价格-0.5单位焦炭(J)主力合约价格

# start_date = datetime.date(2016,1,1)
start_date = datetime.date(2017,1,1)
end_date = datetime.date(2017,12,13)
# end_date = datetime.date(2017,11,3)
id_cores = []
data = w.wsd("RB.SHF", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:2].lower() + "_" + name[2:6]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
data = w.wsd("J.DCE", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:1].lower() + "_" + name[1:5]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
data = w.wsd("I.DCE", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx, dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:1].lower() + "_" + name[1:5]
    id_cores.append({'dt_date': dt, 'id_instrument': id_core})
coreids_df = pd.DataFrame(id_cores)


query_rb = sess.query(Future_mkt.dt_date,Future_mkt.name_code,Future_mkt.id_instrument,Future_mkt.amt_close)\
    .filter(Future_mkt.dt_date >= start_date) \
    .filter(Future_mkt.dt_date <= end_date) \
    .filter(or_(Future_mkt.name_code == 'rb',Future_mkt.name_code == 'j',Future_mkt.name_code == 'i'))\
    .filter(or_(Future_mkt.flag_night == 0,Future_mkt.flag_night == -1))
futuredata_df = pd.read_sql(query_rb.statement,query_rb.session.bind)
# print(futuredata_df)
core_mktdata = pd.merge(coreids_df,futuredata_df,on=['id_instrument','dt_date'],how='left')
rb_data = core_mktdata[core_mktdata['name_code']=='rb']
i_data = core_mktdata[core_mktdata['name_code']=='i']
j_data = core_mktdata[core_mktdata['name_code']=='j']
a = pd.merge(rb_data,i_data,on='dt_date')
earningsdata = pd.merge(a,j_data,on='dt_date')
earningsdata['amt_earning'] = earningsdata['amt_close_x']-1.65*earningsdata['amt_close_y']-0.5*earningsdata['amt_close']

print(earningsdata)

pu = PlotUtil()

f, ax = plt.subplots()

count = 0
pu.plot_line(ax,0,earningsdata['dt_date'],earningsdata['amt_earning'],lgd='钢厂利润指数')
pu.plot_line(ax,1,earningsdata['dt_date'],earningsdata['amt_close_x'],lgd='螺纹钢')
pu.plot_line(ax,2,earningsdata['dt_date'],earningsdata['amt_close_y'],lgd='铁矿石')
pu.plot_line(ax,3,earningsdata['dt_date'],earningsdata['amt_close'],lgd='焦炭')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3, ncol=4, mode="expand", borderaxespad=0.)
ax.set_xticklabels(earningsdata['dt_date'],rotation=90)
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
f.savefig('../save_figure/rbc_earnings.png', dpi=300, format='png', bbox_inches='tight')

f2, ax2 = plt.subplots()
cont1 = 0
pu.plot_line(ax2,0,np.arange(len(earningsdata['amt_earning'])),earningsdata['amt_earning'],lgd='2017')
cont1 += 1

start_date = datetime.date(2016,1,1)
end_date = datetime.date(2016,12,31)
# end_date = datetime.date(2017,11,3)
id_cores = []
data = w.wsd("RB.SHF", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:2].lower() + "_" + name[2:6]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
data = w.wsd("J.DCE", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:1].lower() + "_" + name[1:5]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
data = w.wsd("I.DCE", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx, dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:1].lower() + "_" + name[1:5]
    id_cores.append({'dt_date': dt, 'id_instrument': id_core})
coreids_df = pd.DataFrame(id_cores)


query_rb = sess.query(Future_mkt.dt_date,Future_mkt.name_code,Future_mkt.id_instrument,Future_mkt.amt_close)\
    .filter(Future_mkt.dt_date >= start_date) \
    .filter(Future_mkt.dt_date <= end_date) \
    .filter(or_(Future_mkt.name_code == 'rb',Future_mkt.name_code == 'j',Future_mkt.name_code == 'i'))\
    .filter(or_(Future_mkt.flag_night == 0,Future_mkt.flag_night == -1))
futuredata_df = pd.read_sql(query_rb.statement,query_rb.session.bind)
# print(futuredata_df)
core_mktdata = pd.merge(coreids_df,futuredata_df,on=['id_instrument','dt_date'],how='left')
rb_data = core_mktdata[core_mktdata['name_code']=='rb']
i_data = core_mktdata[core_mktdata['name_code']=='i']
j_data = core_mktdata[core_mktdata['name_code']=='j']
a = pd.merge(rb_data,i_data,on='dt_date')
earningsdata1 = pd.merge(a,j_data,on='dt_date')
earningsdata1['amt_earning'] = earningsdata1['amt_close_x']-1.65*earningsdata1['amt_close_y']-0.5*earningsdata1['amt_close']

pu.plot_line(ax2,cont1,np.arange(len(earningsdata1['amt_earning'])),earningsdata1['amt_earning'],lgd='2016')
cont1 += 1

start_date = datetime.date(2015,1,1)
end_date = datetime.date(2015,12,31)
# end_date = datetime.date(2017,11,3)
id_cores = []
data = w.wsd("RB.SHF", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:2].lower() + "_" + name[2:6]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
data = w.wsd("J.DCE", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:1].lower() + "_" + name[1:5]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
data = w.wsd("I.DCE", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx, dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:1].lower() + "_" + name[1:5]
    id_cores.append({'dt_date': dt, 'id_instrument': id_core})
coreids_df = pd.DataFrame(id_cores)


query_rb = sess.query(Future_mkt.dt_date,Future_mkt.name_code,Future_mkt.id_instrument,Future_mkt.amt_close)\
    .filter(Future_mkt.dt_date >= start_date) \
    .filter(Future_mkt.dt_date <= end_date) \
    .filter(or_(Future_mkt.name_code == 'rb',Future_mkt.name_code == 'j',Future_mkt.name_code == 'i'))\
    .filter(or_(Future_mkt.flag_night == 0,Future_mkt.flag_night == -1))
futuredata_df = pd.read_sql(query_rb.statement,query_rb.session.bind)
# print(futuredata_df)
core_mktdata = pd.merge(coreids_df,futuredata_df,on=['id_instrument','dt_date'],how='left')
rb_data = core_mktdata[core_mktdata['name_code']=='rb']
i_data = core_mktdata[core_mktdata['name_code']=='i']
j_data = core_mktdata[core_mktdata['name_code']=='j']
a = pd.merge(rb_data,i_data,on='dt_date')
earningsdata2 = pd.merge(a,j_data,on='dt_date')
earningsdata2['amt_earning'] = earningsdata2['amt_close_x']-1.65*earningsdata2['amt_close_y']-0.5*earningsdata2['amt_close']

pu.plot_line(ax2,cont1,np.arange(len(earningsdata2['amt_earning'])),earningsdata2['amt_earning'],lgd='2015')
cont1 += 1

start_date = datetime.date(2014,1,1)
end_date = datetime.date(2014,12,31)
# end_date = datetime.date(2017,11,3)
id_cores = []
data = w.wsd("RB.SHF", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:2].lower() + "_" + name[2:6]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
data = w.wsd("J.DCE", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx,dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:1].lower() + "_" + name[1:5]
    id_cores.append({'dt_date':dt,'id_instrument':id_core})
data = w.wsd("I.DCE", "trade_hiscode", start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'), "")
for idx, dt in enumerate(data.Times):
    name = data.Data[0][idx]
    id_core = name[0:1].lower() + "_" + name[1:5]
    id_cores.append({'dt_date': dt, 'id_instrument': id_core})
coreids_df = pd.DataFrame(id_cores)


query_rb = sess.query(Future_mkt.dt_date,Future_mkt.name_code,Future_mkt.id_instrument,Future_mkt.amt_close)\
    .filter(Future_mkt.dt_date >= start_date) \
    .filter(Future_mkt.dt_date <= end_date) \
    .filter(or_(Future_mkt.name_code == 'rb',Future_mkt.name_code == 'j',Future_mkt.name_code == 'i'))\
    .filter(or_(Future_mkt.flag_night == 0,Future_mkt.flag_night == -1))
futuredata_df = pd.read_sql(query_rb.statement,query_rb.session.bind)
# print(futuredata_df)
core_mktdata = pd.merge(coreids_df,futuredata_df,on=['id_instrument','dt_date'],how='left')
rb_data = core_mktdata[core_mktdata['name_code']=='rb']
i_data = core_mktdata[core_mktdata['name_code']=='i']
j_data = core_mktdata[core_mktdata['name_code']=='j']
a = pd.merge(rb_data,i_data,on='dt_date')
earningsdata3 = pd.merge(a,j_data,on='dt_date')
earningsdata3['amt_earning'] = earningsdata3['amt_close_x']-1.65*earningsdata3['amt_close_y']-0.5*earningsdata3['amt_close']

pu.plot_line(ax2,cont1,np.arange(len(earningsdata3['amt_earning'])),earningsdata3['amt_earning'],lgd='2014')
cont1 += 1





plt.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3, ncol=4, mode="expand", borderaxespad=0.)
ticks = np.arange(0,len(earningsdata3['amt_earning']),
                         (len(earningsdata3['amt_earning'])-0)/12.1)
months = ['            1月','            2月','            3月','            4月',
          '            5月','            6月',
          '            7月','            8月','            9月','           10月',
          '           11月','           12月']
print(ticks)
ax2.set_xticks(ticks)
ax2.set_xticklabels(months)
# ax2.xaxis.set_major_formatter(mdates.DateFormatter('%m'))
plt.show()
f2.savefig('../save_figure/rbc_earnings_hist.png', dpi=300, format='png', bbox_inches='tight')













