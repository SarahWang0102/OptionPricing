import matplotlib.pyplot as plt
import operator
import plot_util as pu
import svi_calibration_utility as svi_util
import svi_prepare_vol_data as svi_data
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
#evalDate = ql.Date(7,1,2015)
evalDate = ql.Date(7,7,2017)

spotprice_dic = svi_util.get_underlying_ts()

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
        curve = svi_util.get_curve_treasury_bond(evalDate, daycounter)
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

spread_this_month = []
spread_next_month = []
spread_this_season = []
spread_next_season = []
callvol_next_month = []
callvol_this_season = []
callvol_next_season = []
putvol_next_month = []
putvol_this_season = []
putvol_next_season = []
dates = []
underlying_chg = []
underlying_close = []
volum_next_month = []
volum_this_season = []
volum_next_season = []
for key in spreads_avg_ts.keys():
    if key not in spotprice_dic.keys(): continue
    dt_pd = datetime.date(key.year(), key.month(), key.dayOfMonth())
    dates.append(dt_pd)
    spread_this_month.append(spreads_avg_ts.get(key)[0])
    spread_next_month.append(spreads_avg_ts.get(key)[1])
    spread_this_season.append(spreads_avg_ts.get(key)[2])
    spread_next_season.append(spreads_avg_ts.get(key)[3])
    underlying_close.append(spotprice_dic.get(key))
    callvol_next_month.append(callvol_avg_ts.get(key)[1])
    putvol_next_month.append(putvol_avg_ts.get(key)[1])
    volum_next_month.append(trading_volum_dic.get(key)[1])


print('dates = ',dates)
print('underlying_chg =',underlying_chg)
print('spread_this_month = ',spread_this_month)
print('spread_next_month = ',spread_next_month)
print('spread_this_season = ', spread_this_season)
print('spread_next_season = ',spread_next_season)
print('volum_next_month = ',volum_next_month)
print('callvol_next_month = ',callvol_next_month)
print('putvol_next_month = ',putvol_next_month)
print('underlying_close =',underlying_close)

f, axarr = plt.subplots(4, sharex=True)

line1, = axarr[0].stackplot(dates, underlying_close,color = pu.c3)
axarr[0].set_title('Underlying v.s. CPIV')
line2, = axarr[1].plot(dates, spread_next_month, color = pu.c1,linestyle = pu.l1,linewidth = 2,label="CPIV next month")
line3, = axarr[1].plot(dates, spread_this_season,color = pu.c2,linestyle = pu.l2,linewidth = 2,label = "CPIV this season")
line4, = axarr[1].plot(dates, spread_next_season,color = pu.c3,linestyle = pu.l3,linewidth = 2,label="CPIV next season")
line5, = axarr[1].plot(dates,[0]*len(dates),color = (0,0,0),linestyle = pu.l5,linewidth = 1)
axarr[2].bar(dates,volum_next_month,2,color = pu.c2)
line6, = axarr[3].plot(dates, callvol_next_month,color = pu.c4,linestyle = pu.l4,linewidth = 2,label="Call IV next month")
line7, = axarr[3].plot(dates, putvol_next_month,color = pu.c5,linestyle = pu.l5,linewidth = 2,label="Put IV next month")
line6.set_dashes(pu.dash)
axarr[0].set_ylim(min(underlying_close),max(underlying_close))
axarr[0].legend(['50 ETF'])
axarr[1].legend()
axarr[2].legend(['Trading Volume(million)'])
axarr[3].legend()
axarr[1].grid()
axarr[0].grid()
axarr[3].grid()
plt.draw()
plt.show()
