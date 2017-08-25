import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.dates import date2num
import Utilities.plot_util as pu
import os

exceldata     = pd.read_excel(os.path.abspath('..') +'/excel_data/option_volume.xlsx',sheetname ='volume')
print(exceldata)
print(exceldata.index)

etf = exceldata.loc[['ETF'],:].values[0]/1000000
print(etf)
index = exceldata.loc[['Index'],:].values[0]/1000000
equity = exceldata.loc[['Equity'],:].values[0]/1000000

dates = exceldata.axes[1]
dates = dates.strftime("%m/%y")

ratio_equity = equity/etf
ratio_index = index/etf
print('ratio_index = ',ratio_index)
print('ratio_equity = ',ratio_equity)
#print('avg ratio_index = ',sum(ratio_index)/len(ratio_index))
#print('avg ratio_equity = ',sum(ratio_equity)/len(ratio_equity))
print(dates)
print(etf)
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
x = np.arange(len(dates))
w = 0.2
print(x)
print(x+w)
f, axarr  = plt.subplots()
axarr.bar(x,etf,width =w, color=pu.c1,label = 'ETF期权')
axarr.bar(x,equity,width =w, color=pu.c2,bottom=etf,label = '个股期权')
axarr.bar(x,index,width =w, color=pu.c3,bottom=equity,label = '指数期权')
axarr.set_xticks(x)
axarr.set_xticklabels(dates)
axarr.set_ylabel('成交额（百万美元）')
# Hide the right and top spines
axarr.spines['right'].set_visible(False)
axarr.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
axarr.yaxis.set_ticks_position('left')
axarr.xaxis.set_ticks_position('bottom')
lgd = axarr.legend(bbox_to_anchor=(0., 1.02, 1.1, .102), loc=3,
           ncol=3, borderaxespad=0.,columnspacing=1.5,frameon=False)
for label in axarr.get_xmajorticklabels() :
    label.set_rotation(30)
    label.set_horizontalalignment("right")
f.savefig('volume_us.png', dpi=300, format='png', bbox_extra_artists=(lgd,), bbox_inches='tight')
plt.show()
