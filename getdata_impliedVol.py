from VolatilityData import *
from WindPy import *
import math
import matplotlib.pyplot as plt
import numpy as np
import datetime

w.start()
evalDate = ql.Date(12,6,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
#risk_free_rate = 0.0435
dividend_rate = 0.0
#next_i_month = 0
next_months = [0,1,3,6]

########################################################################################################################
## Depo curve
#curve = get_curve_depo(evalDate,daycounter)
## Treasury Bond curve
curve = get_curve_treasuryBond(evalDate,daycounter)
maxtime = daycounter.yearFraction(evalDate,ql.Date(6,12,2018))
#times = np.linspace(curve.referenceDate(),curve.maxDate(),100)
ref_date = curve.referenceDate()
max_date = curve.maxDate()
dates = np.array([datetime.date(ref_date.year(),ref_date.month(),ref_date.dayOfMonth()) + datetime.timedelta(days=i)
                  for i in range(max_date - ref_date)])
times = np.linspace(0.0, (max_date-ref_date)/365,100)
rate = curve.zeroRate(ref_date,daycounter,ql.Continuous)
rates = [curve.zeroRate(t,ql.Continuous).rate() for t in times]
########################################################################################################################

call_volatilities,put_converted_volatilites,strikes_call,strikes_put,\
           close_call,close_put,logMoneyness_call,logMoneyness_put,maturitydt,spot = \
    get_impliedvolmat_BS_OTM_oneMaturity(
        evalDate,daycounter,calendar,evalDate.month(),maxVol=1.0,step=0.0001,precision=0.001,show=True)
print("CALL:")
print("=" * 110)
print("%10s %10s %10s %25s %25s %20s" % ("Spot", "Strike", "close", "moneyness", "impliedVol", "Error (%)"))
print("-" * 110)
for i, v in enumerate(call_volatilities):
    print("%10s %10s %10s %25s %25s %20s" %
          (spot, strikes_call[i],close_call[i], logMoneyness_call[i], call_volatilities[i], 0.0))
print("-" * 110)
print("PUT:")
print("=" * 110)
print("%10s %10s %10s %25s %25s %20s" % ("Spot", "Strike", "close", "moneyness", "impliedVol", "Error (%)"))
print("-" * 110)
for i, v in enumerate(put_converted_volatilites):
    print("%10s %10s %10s %25s %25s %20s" %
          (spot, strikes_put[i],close_put[i], logMoneyness_put[i], put_converted_volatilites[i], 0.0))
print("-" * 110)
########################################################################################################################
vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data(evalDate)


#plt.plot(times,rates)
#plt.title('Interest Rate Term Structure')
#plt.show()




