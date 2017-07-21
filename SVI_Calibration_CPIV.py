from VolatilityData import *
from SVI_CalibrationFun import *
import math
import matplotlib.pyplot as plt
import datetime

w.start()
# Evaluation Settings
calendar   = ql.China()
daycounter = ql.ActualActual()

#endDate = ql.Date(4,8,2016)
endDate  = ql.Date(20,7,2017)
#evalDate = endDate
evalDate = ql.Date(13,7,2015)
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
            for k in call_vol_dict.keys():
                call_volatilities.append(call_vol_dict.get(k))
                put_volatilities.append(put_vol_dict.get(k))
                spread = put_vol_dict.get(k) - call_vol_dict.get(k)
                vol_spreads.append(spread)
            spreads_avg.append(sum(vol_spreads)/len(vol_spreads))
        spreads_avg_ts.update({evalDate:spreads_avg})
        print('evalDate ',evalDate, ' finished')
    except:
        print(evalDate,' get data failed')
        continue
    #print(str(evalDate),'spreads : ',spreads_avg)
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
    spread_next_month.append(spreads_avg_ts.get(key)[1])
    underlying_chg.append((spotprice_dic.get(key) - spot_last_close)/spot_last_close)
    spot_last_close = spotprice_dic.get(key)
print('dates: ',dates)
print('spread_next_month: ',spread_next_month)
print('underlying_chg:',underlying_chg)



for key in spreads_avg_ts.keys():
    spread_far_month.append(spreads_avg_ts.get(key)[3])

print('spread_far_month: ',spread_far_month)

for key in spreads_avg_ts.keys():
    spread_this_month.append(spreads_avg_ts.get(key)[0])
print('spread_this_month: ',spread_this_month)

for key in spreads_avg_ts.keys():
    spread_next_season.append(spreads_avg_ts.get(key)[2])
print('spread_next_season: ',spread_next_season)


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
        print(strikes_call)
        print(strikes_put)
        print('Maturity Date : ',maturitydt)
        print("=" * 110)
        print(" %15s %25s %25s %25s" % ("Strike", "impliedVol(call)", "impliedVol(put)","spread"))
        print("-" * 110)
        for i, v in enumerate(call_volatilities):
            print(" %15s %25s %25s %25s" % (strikes_call[i], round(v,3), round(put_volatilites[i],3), round(vol_spreads[i],3)))
        print("-" * 110)
        plt.figure(idx)
        plt.plot(strikes_call,vol_spreads,'r*')
        plt.title('Call Put Volatility Spread for ' + str(maturitydt))
    plt.figure(idx+1)
    plt.plot([1,2,3,4],spreads_avg)
    plt.show()
    '''