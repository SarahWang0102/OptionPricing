from VolatilityData_readpkl import *
from SVI_CalibrationFun import *
import math
import matplotlib.pyplot as plt
import datetime
import operator
from mpl_toolkits.axes_grid1 import host_subplot
import mpl_toolkits.axisartist as AA
import plot_util as pu
from SVI_Calibration_Util import *

#w.start()
# Evaluation Settings
calendar   = ql.China()
daycounter = ql.ActualActual()

#endDate = ql.Date(4,8,2016)
endDate  = ql.Date(20,7,2017)
#evalDate = endDate
evalDate = ql.Date(1,6,2017)
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
begDate  = evalDate

spotprice_dic = get_underlying_ts()
print('spotprice_dic : ',spotprice_dic)
#spot_last_close = spotprice_dic.get(begDate)

spreads_avg_ts = {}
while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Weeks))
    spreads_avg = []
    ql.Settings.instance().evaluationDate = evalDate
    try:
        curve = get_curve_treasuryBond(evalDate, daycounter)
        cal_vols_data, put_vols_data = get_call_put_impliedVols(evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
        # Loop through contract months
        for idx_month,call_vol_dict in enumerate(cal_vols_data):
            put_vol_dict = put_vols_data[idx_month]
            call_volatilities = []
            put_volatilities = []
            vol_spreads = []
            strikes = []
            call_sorted = sorted(call_vol_dict.items(), key=operator.itemgetter(0))
            call_vol_dict_sorted = dict(call_sorted)
            put_sorted = sorted(put_vol_dict.items(), key=operator.itemgetter(0))
            put_vol_dict_sorted = dict(put_sorted)
            for k in call_vol_dict_sorted.keys():
                strikes.append(k)
                call_volatilities.append(call_vol_dict_sorted.get(k))
                put_volatilities.append(put_vol_dict_sorted.get(k))
                spread = put_vol_dict_sorted.get(k) - call_vol_dict_sorted.get(k)
                vol_spreads.append(spread)
            spreads_avg.append(sum(vol_spreads)/len(vol_spreads))
            #print(call_vol_dict_sorted.keys())
            #print(call_volatilities)
            #.figure(idx_month)
            #plt.plot(strikes,call_volatilities,'b*-')
            #plt.plot(strikes, put_volatilities,'r*-')
        spreads_avg_ts.update({evalDate:spreads_avg})
        print('evalDate ',evalDate, ' finished')
        plt.show()
    except:
        print('E:',evalDate,' get data failed')
        continue
print('spreads_avg_ts : ',spreads_avg_ts)

spread_next_month = []
spread_far_month = []
spread_this_month = []
spread_next_season = []
dates = []
underlying_chg = []
spot_last_close = spotprice_dic.get(begDate)

for key in spreads_avg_ts.keys():
    if key not in spotprice_dic.keys(): continue
    dt_pd = datetime.date(key.year(), key.month(), key.dayOfMonth())
    dates.append(dt_pd)
    spread_this_month.append(spreads_avg_ts.get(key)[0])
    spread_next_month.append(spreads_avg_ts.get(key)[1])
    spread_next_season.append(spreads_avg_ts.get(key)[2])
    spread_far_month.append(spreads_avg_ts.get(key)[3])
    underlying_chg.append((spotprice_dic.get(key) - spot_last_close)/spot_last_close)
    spot_last_close = spotprice_dic.get(key)

'''
for key in spreads_avg_ts.keys():
    if key not in spotprice_dic.keys(): continue
    spread_far_month.append(spreads_avg_ts.get(key)[3])

for key in spreads_avg_ts.keys():
    if key not in spotprice_dic.keys(): continue
    spread_this_month.append(spreads_avg_ts.get(key)[0])

for key in spreads_avg_ts.keys():
    if key not in spotprice_dic.keys(): continue
    spread_next_season.append(spreads_avg_ts.get(key)[2])
'''

print('dates: ',dates)
print('underlying_chg:',underlying_chg)
print('spread_this_month: ',spread_this_month)
print('spread_next_month: ',spread_next_month)
print('spread_far_month: ', spread_far_month)
print('spread_next_season: ',spread_next_season)


host = host_subplot(111, axes_class=AA.Axes)
plt.subplots_adjust(right=0.75)
par1 = host.twinx()

#host.set_xlim(0, 2)
#host.set_ylim(-1, 1)
#par1.set_ylim(-1, 1)

host.set_xlabel("Date")
host.set_ylabel("Underlying")
par1.set_ylabel("Spread")
#dash = [8,2,3,2]
line1, = host.plot(dates, underlying_chg, color = pu.c1,linestyle = pu.l1,linewidth = 2,label="Underlying")
line2, = par1.plot(dates, spread_next_month, color = pu.c2,linestyle = pu.l2,linewidth = 2,label="Spread next month")
line3, = par1.plot(dates, spread_far_month,color = pu.c3,linestyle = pu.l3,linewidth = 2,label="Spread far month")
line4, = par1.plot(dates,spread_next_season,color = pu.c4,linestyle = pu.l4,linewidth = 2,label = "Spread next season")
line4.set_dashes(pu.dash)

host.legend()

host.axis["left"].label.set_color(line1.get_color())
par1.axis["right"].label.set_color(line2.get_color())


plt.draw()
plt.show()
'''
plt.figure(1)
l2,= plt.plot(dates,spread_next_month,'b--')
l1,= plt.plot(dates,underlying_chg, 'k-')
l3,= plt.plot(dates,spread_far_month,'r--')
l4,= plt.plot(dates,spread_this_month,'g--')
l5,= plt.plot(dates,spread_next_season,'y--')

a1 = 'underlying price change'
a2 = 'put call spread next month'
a3 = 'put call spread far month'
a4 = 'put call spread this month'
a5 = 'put call spread next season'
plt.title('spreads')
plt.legend([l1,l4,l2,l5,l3],[a1,a4,a2,a5,a3])
plt.show()
'''
