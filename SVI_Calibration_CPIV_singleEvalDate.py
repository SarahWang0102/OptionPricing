import matplotlib.pyplot as plt
import operator
from SVI_Calibration_Util import *


#w.start()
# Evaluation Settings
calendar   = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(13,7,2017)
begDate  = evalDate

# Underlying close prices
spotprice_dic = get_underlying_ts()

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
    #print(call_vol_dict_sorted.keys())
    #print(call_volatilities)
    plt.figure(idx_month)
    plt.plot(strikes,call_volatilities,'r*-')
    plt.plot(strikes, put_volatilities,'g*-')
spreads_avg_ts.update({evalDate:spreads_avg})
print('evalDate ',evalDate, ' finished')
plt.show()

#### ADD moneyness plot