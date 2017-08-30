import exotic_options.exotic_option_utilities as exotic_otil
from Utilities.utilities import *
import Utilities.hedging_utility as hedge_util
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import Utilities.plot_util as pu


with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_puts.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_dates_puts.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Evaluation Settings
begDate = ql.Date(14,7,2017)
calendar = ql.China()
daycounter = ql.ActualActual()

simulation_no = 1000
noise = np.random.normal(0,1,(simulation_no,len(dates)))
delta_t = 1.0/365
i = 3

optiontype = ql.Option.Call
barrierType = ql.Barrier.DownOut

calibrated_params = daily_params.get(to_dt_date(begDate))  # on calibrate_date
cal_vols, put_vols, maturity_dates, spot, risk_free_rates = daily_svi_dataset.get(to_dt_date(begDate))
black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params, to_ql_dates(maturity_dates),
                                                            begDate, daycounter, calendar, spot, risk_free_rates)
maturityDate = to_ql_date(maturity_dates[i])
rf = risk_free_rates.get(i)
params =  calibrated_params[i]

barrier = 0.9*spot
strike = 1.1*spot

print('barrier : ', barrier)
print('strike : ', strike)

ql.Settings.instance().evaluationDate = begDate
yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(begDate, rf, daycounter))
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(begDate, 0.0, daycounter))
exercise = ql.EuropeanExercise(maturityDate)
payoff = ql.PlainVanillaPayoff(optiontype, strike)

option = ql.BarrierOption(barrierType, barrier, 0.0,payoff, exercise)
process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts,
                                       yield_ts, ql.BlackVolTermStructureHandle(black_var_surface))
option.setPricingEngine(ql.AnalyticBarrierEngine(process))
npv = option.NPV()
print(npv)

'''
underlyings = np.arange(0.85*spot,1.02*spot,0.005)
option_prices = []
for s0 in underlyings:
    print(s0)
    price,x,xx = exotic_otil.down_out_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,
                                             s0,strike,barrier,rf,delta_t,params,noise)
    option_prices.append(price)
plt.plot(underlyings.tolist(),option_prices,color = pu.c1,linestyle = pu.l1,linewidth = 2)
plt.ylim([0,max(option_prices)])
plt.show()
'''