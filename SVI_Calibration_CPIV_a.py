from VolatilityData import *
from SVI_CalibrationFun import *
import math
import matplotlib.pyplot as plt
import datetime
import operator

w.start()
# Evaluation Settings
calendar   = ql.China()
daycounter = ql.ActualActual()

#endDate = ql.Date(4,8,2016)
endDate  = ql.Date(20,7,2017)
#evalDate = endDate
evalDate = ql.Date(13,7,2016)
evalDate = calendar.advance(evalDate, ql.Period(6, ql.Months))
begDate  = evalDate

def get_data_from_wind(next_i_month,curve):
    vols, expiration_date, strikes, spot = get_impliedvolmat_wind_oneMaturity('认购',evalDate,next_i_month)
    risk_free_rate  =   curve.zeroRate(expiration_date,daycounter,ql.Continuous).rate()
    return vols, expiration_date, strikes, spot, risk_free_rate

def get_underlying_ts(evalDate,endDate):
    evalDate_str = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    endDate_str  = str(endDate.year()) + "-" + str(endDate.month()) + "-" + str(endDate.dayOfMonth())
    underlyingdata = w.wsd("510050.SH", "close", evalDate_str, endDate_str, "Fill=Previous;PriceAdj=F")
    dates_ts  = underlyingdata.Times
    spot_ts   = underlyingdata.Data[0]
    spot_dic  = {}
    for idx_dt,dt in enumerate(dates_ts):
        date_tmp = pd.to_datetime(dt)
        date_ql = ql.Date(date_tmp.day, date_tmp.month, date_tmp.year)
        spot_dic.update({date_ql:spot_ts[idx_dt]})
    return spot_dic

spotprice_dic = get_underlying_ts(evalDate,endDate)
print('spotprice_dic : ',spotprice_dic)
#spot_last_close = spotprice_dic.get(begDate)

spreads_avg_ts = {}
curve = get_curve_treasuryBond(evalDate, daycounter)
cal_vols_data, put_vols_data = get_call_put_impliedVols(evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
        # Loop through contract months
spreads_avg = []
ql.Settings.instance().evaluationDate = evalDate
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
    print(call_vol_dict_sorted.keys())
    print(call_volatilities)
    plt.figure(idx_month)
    plt.plot(strikes,call_volatilities,'r*-')
    plt.plot(strikes, put_volatilities,'g*-')
spreads_avg_ts.update({evalDate:spreads_avg})
print('evalDate ',evalDate, ' finished')
plt.show()

#### ADD moneyness plot