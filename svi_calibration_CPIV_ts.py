# -*- coding:utf-8 -*-
import matplotlib.pyplot as plt
import matplotlib
import operator
import plot_util as pu
import svi_calibration_utility as svi_util
import svi_prepare_vol_data as svi_data
import svi_read_data as raw_data
import QuantLib as ql
import datetime
from WindPy import w

w.start()
# Evaluation Settings
calendar   = ql.China()
daycounter = ql.ActualActual()

#endDate = ql.Date(4,8,2016)
endDate  = ql.Date(20,7,2017)
#evalDate = endDate
evalDate = ql.Date(7,1,2015)
#evalDate = ql.Date(1,7,2017)

spotprice_dic = raw_data.get_underlying_ts()

spreads_avg_ts = {}
callvol_avg_ts = {}
putvol_avg_ts = {}
trading_volum_dic = {}
while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    spreads_avg = []
    callvol_avg = []
    putvol_avg = []
    trading_volums = []
    ql.Settings.instance().evaluationDate = evalDate
    try:
        curve = raw_data.get_curve_treasury_bond(evalDate, daycounter)
        cal_vols_data, put_vols_data = svi_data.get_call_put_impliedVols_strikes(evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
        # Loop through contract months
        for idx_month,call_vol_dict in enumerate(cal_vols_data):
            put_vol_dict        = put_vols_data[idx_month]
            vol_spreads_weights = []
            strikes             = []
            call_sorted         = sorted(call_vol_dict.items(), key=operator.itemgetter(0))
            call_vol_dict_sorted = dict(call_sorted)
            put_sorted          = sorted(put_vol_dict.items(), key=operator.itemgetter(0))
            put_vol_dict_sorted = dict(put_sorted)
            spread_weightsum    = 0.0
            callvol_weightsum   = 0.0
            putvol_weightsum    = 0.0
            amount_strikesum    = 0.0
            for k in call_vol_dict_sorted.keys():
                strikes.append(k)
                amount              = call_vol_dict_sorted.get(k)[1]  + put_vol_dict_sorted.get(k)[1]
                spread_weight       = (call_vol_dict_sorted.get(k)[0] - put_vol_dict_sorted.get(k)[0])*amount
                spread_weightsum    = spread_weightsum  + spread_weight
                callvol_weightsum   = callvol_weightsum + call_vol_dict_sorted.get(k)[0] * amount
                putvol_weightsum    = putvol_weightsum  + put_vol_dict_sorted.get(k)[0] * amount
                amount_strikesum    = amount_strikesum  + amount
            spreads_avg.append(spread_weightsum  / amount_strikesum)
            callvol_avg.append(callvol_weightsum / amount_strikesum)
            putvol_avg.append(putvol_weightsum   / amount_strikesum)
            trading_volums.append(amount_strikesum/1000000)
        spreads_avg_ts.update({evalDate:spreads_avg})
        trading_volum_dic.update({evalDate:trading_volums})
        callvol_avg_ts.update({evalDate:callvol_avg})
        putvol_avg_ts.update({evalDate:putvol_avg})
        print('evalDate ',evalDate, ' finished')
    except:
        print('Warning:',evalDate,' get Spread failed')
        continue
print('spreads_avg_ts : ',spreads_avg_ts)

dates = []
spread_this_month = []
spread_next_month = []
spread_this_season = []
spread_next_season = []

callvol_months_avg = []
putvol_months_avg = []
'''
callvol_this_month = []
callvol_next_month = []
callvol_this_season = []
callvol_next_season = []
putvol_this_month = []
putvol_next_month = []
putvol_this_season = []
putvol_next_season = []
'''
underlying_chg = []
underlying_close = []

volum_months_sum = []
'''
volum_next_month = []
volum_this_season = []
volum_next_season = []
'''
for key in spreads_avg_ts.keys():
    if key not in spotprice_dic.keys(): continue
    dt_pd = datetime.date(key.year(), key.month(), key.dayOfMonth())
    dates.append(dt_pd)
    spread_this_month.append(spreads_avg_ts.get(key)[0])
    spread_next_month.append(spreads_avg_ts.get(key)[1])
    spread_this_season.append(spreads_avg_ts.get(key)[2])
    spread_next_season.append(spreads_avg_ts.get(key)[3])
    underlying_close.append(spotprice_dic.get(key))
    callvol_months_avg.append(sum(callvol_avg_ts.get(key))/len(callvol_avg_ts.get(key)))
    putvol_months_avg.append(sum(putvol_avg_ts.get(key))/len(putvol_avg_ts.get(key)))
    volum_months_sum.append(sum(trading_volum_dic.get(key)))


print('dates = ',dates)
#print('underlying_chg =',underlying_chg)
print('spread_this_month = ',spread_this_month)
print('spread_next_month = ',spread_next_month)
print('spread_this_season = ', spread_this_season)
print('spread_next_season = ',spread_next_season)
print('volum_months_sum = ',volum_months_sum)
print('callvol_months_avg = ',callvol_months_avg)
print('putvol_months_avg = ',putvol_months_avg)
print('underlying_close =',underlying_close)

plt.rcParams['font.sans-serif'] = ['STKaiti']
f, axarr = plt.subplots(3, sharex=True)
#axarr[0].set_title(u"看涨看跌期权隐含波动率差(CPIV)")
line1, = axarr[0].plot(dates, spread_this_month, color=pu.c1, linestyle=pu.l1, linewidth=2, label=u'CPIV当月')
line2, = axarr[0].plot(dates, spread_next_month, color=pu.c2, linestyle=pu.l2, linewidth=2, label=u'CPIV下月')
line3, = axarr[0].plot(dates, spread_this_season, color=pu.c3, linestyle=pu.l3, linewidth=2, label=u'CPIV当季')
line4, = axarr[0].plot(dates, spread_next_season, color=pu.c4, linestyle=pu.l4, linewidth=2, label=u'CPIV下季')
line4.set_dashes(pu.dash)
line5, = axarr[1].plot(dates, volum_months_sum, color=pu.c5, linestyle=pu.l5, linewidth=2, label=u"总成交量(百万)")

line6, = axarr[2].plot(dates, callvol_months_avg, color=pu.c6, linestyle=pu.l6, linewidth=2, label=u"隐含波动率-看涨")
line7, = axarr[2].plot(dates, putvol_months_avg, color=pu.c7, linestyle=pu.l7, linewidth=2, label=u"隐含波动率-看跌")

# Shrink current axis by 20%
box0 = axarr[0].get_position()
axarr[0].set_position([box0.x0, box0.y0, box0.width * 0.8, box0.height])
# Put a legend to the right of the current axis
lgd0 = axarr[0].legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)

box1 = axarr[1].get_position()
axarr[1].set_position([box1.x0, box1.y0, box1.width * 0.8, box1.height])
lgd1 = axarr[1].legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)

box2 = axarr[2].get_position()
axarr[2].set_position([box2.x0, box2.y0, box2.width * 0.8, box2.height])
lgd2 = axarr[2].legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)

f.savefig('image_output.png', dpi=300, format='png', bbox_extra_artists=(lgd0,lgd1,lgd2,), bbox_inches='tight')
#axarr[3].legend()
axarr[1].grid()
axarr[0].grid()
#axarr[3].grid()
plt.draw()
plt.show()

