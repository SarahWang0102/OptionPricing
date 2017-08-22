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
call_trading_volum_dic = {}
put_trading_volum_dic = {}
while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    spreads_avg = []
    callvol_avg = []
    putvol_avg = []
    trading_volums_call = []
    trading_volums_put = []
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
            call_amount_strikesum = 0.0
            put_amount_strikesum = 0.0
            amount_strikesum = 0.0
            for k in call_vol_dict_sorted.keys():
                strikes.append(k)
                call_amount = call_vol_dict_sorted.get(k)[1]
                put_amount = put_vol_dict_sorted.get(k)[1]
                amount              = call_amount  + put_amount
                spread_weight       = (call_vol_dict_sorted.get(k)[0] - put_vol_dict_sorted.get(k)[0])*amount
                spread_weightsum    = spread_weightsum  + spread_weight
                callvol_weightsum   = callvol_weightsum + call_vol_dict_sorted.get(k)[0] * call_amount
                putvol_weightsum    = putvol_weightsum  + put_vol_dict_sorted.get(k)[0] * put_amount
                amount_strikesum    = amount_strikesum  + amount
                call_amount_strikesum = call_amount_strikesum + call_amount
                put_amount_strikesum = put_amount_strikesum + put_amount
            weighted_avg_callvol = callvol_weightsum/call_amount_strikesum
            weighted_avg_pullvol = putvol_weightsum/put_amount_strikesum
            weighted_avg_spread = weighted_avg_callvol-weighted_avg_pullvol
            spreads_avg.append(weighted_avg_spread)
            callvol_avg.append(weighted_avg_callvol)
            putvol_avg.append(weighted_avg_pullvol)
            trading_volums_call.append(call_amount_strikesum/1000000)
            trading_volums_put.append(put_amount_strikesum / 1000000)
        spreads_avg_ts.update({evalDate:spreads_avg})
        call_trading_volum_dic.update({evalDate:trading_volums_call})
        put_trading_volum_dic.update({evalDate: trading_volums_put})
        callvol_avg_ts.update({evalDate:callvol_avg})
        putvol_avg_ts.update({evalDate:putvol_avg})
        print('evalDate ',evalDate, ' finished')
    except:
        print('Warning:',evalDate,' get Spread failed')
        continue
#print('spreads_avg_ts : ',spreads_avg_ts)

dates = []
spread_this_month = []
spread_next_month = []
spread_this_season = []
spread_next_season = []

callvol_months_avg = []
putvol_months_avg = []

underlying_chg = []
underlying_close = []

call_volum_months_sum = []
put_volum_months_sum = []

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
    call_volum_months_sum.append(sum(call_trading_volum_dic.get(key)))
    put_volum_months_sum.append(sum(put_trading_volum_dic.get(key)))

print('dates = ',dates)
#print('underlying_chg =',underlying_chg)
print('spread_this_month = ',spread_this_month)
print('spread_next_month = ',spread_next_month)
print('spread_this_season = ', spread_this_season)
print('spread_next_season = ',spread_next_season)
print('call_volum_months_sum = ',call_volum_months_sum)
print('put_volum_months_sum = ',put_volum_months_sum)
print('callvol_months_avg = ',callvol_months_avg)
print('putvol_months_avg = ',putvol_months_avg)
print('underlying_close =',underlying_close)
