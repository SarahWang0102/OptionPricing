import exotic_options.exotic_option_utilities as exotic_otil
import Utilities.svi_prepare_vol_data as svi_data
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
today = ql.Date(14,7,2017)
ql.Settings.instance().evaluationDate = today
calendar = ql.China()
daycounter = ql.ActualActual()

#simulation_no = 1000
#noise = np.random.normal(0,1,(simulation_no,len(dates)))
#delta_t = 1.0/365
i = 3

# Down and out Call
optiontype = ql.Option.Call
barrierType = ql.Barrier.DownIn
curve = svi_data.get_curve_treasury_bond(today,daycounter)
calibrated_params = daily_params.get(to_dt_date(today))  # on calibrate_date
cal_vols, put_vols, maturity_dates, spot, risk_free_rates = daily_svi_dataset.get(to_dt_date(today))
black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params, to_ql_dates(maturity_dates),
                                                            today, daycounter, calendar, spot, risk_free_rates)

maturityDate = to_ql_date(maturity_dates[i])
rf = risk_free_rates.get(i)
params =  calibrated_params[i]

#maturityDate = calendar.advance(today,ql.Period(6,ql.Months))
print(maturityDate)
print(rf)
#rf = 0.0
#spot = 100
barrier = spot - 0.05
strike = spot
ttm = daycounter.yearFraction(today,maturityDate)
strike = ((barrier*np.exp(rf*ttm))**2)/strike
k_container = []
for vol in cal_vols[i].values():
    k_container.append(vol[1])

print('barrier : ', barrier)
print('strike : ', strike)


yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(today, rf, daycounter))
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(today, 0.0, daycounter))
flat_vol = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0,ql.NullCalendar(), ql.QuoteHandle(ql.SimpleQuote(0.157)), daycounter))
exercise = ql.EuropeanExercise(maturityDate)
payoff = ql.PlainVanillaPayoff(optiontype, strike)
underlying = ql.SimpleQuote(spot)

option = ql.BarrierOption(barrierType, barrier, 0.0,payoff, exercise)
process = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying), dividend_ts,
                                       yield_ts, ql.BlackVolTermStructureHandle(black_var_surface))
process1 = ql.BlackScholesProcess(ql.QuoteHandle(underlying),yield_ts, flat_vol)
barrier_engine = ql.AnalyticBarrierEngine(process)
european_engine = ql.AnalyticEuropeanEngine(process)
option.setPricingEngine(barrier_engine)
reference_npv = option.NPV()
print('reference_npv :',reference_npv)
portfolio1 = ql.CompositeInstrument()
portfolio2 = ql.CompositeInstrument()

# Long a call struck at strike
call = ql.EuropeanOption(payoff,exercise)
call.setPricingEngine(european_engine)
call_price = call.NPV()
print('call value : ',call_price)
portfolio1.add(call)


# short put_ratio shares of puts struck at k_put
k_put = strike
put_payoff = ql.PlainVanillaPayoff(ql.Option.Put, k_put)
put = ql.EuropeanOption(put_payoff,exercise)
put.setPricingEngine(european_engine)
put_price = put.NPV()
put_ratio = np.sqrt(strike/k_put)
print('put_ratio : ',put_ratio,call_price/put_price,np.abs(put_price*np.sqrt(strike/k_put)-call_price))
print('put value : ',put.NPV())
# Find the shares of put that make replication portfolio = 0.0 at barrier
put_ratio2 = 1.0
diff = 10
for r in np.arange(0,2,0.001):
    p = ql.CompositeInstrument()
    p.add(call)
    underlying.setValue(barrier)
    p.subtract(put, r)
    npv = p.NPV()
    if abs(npv - 0) < diff :
        diff = abs(npv - 0)
        put_ratio2 = r
print('put_ratio2 : ',put_ratio2)

portfolio2.add(put,put_ratio)

underlying.setValue(spot)
print("="*100)
print("%15s %25s %25s %25s" % ("spot","reference npv","replicate npv", "hedge error"))
print("-"*100)
for s in np.arange(barrier,strike+0.2,0.01):
    underlying.setValue(s)

    if s > barrier:
        portfolio_value = portfolio2.NPV()
    else:
        portfolio_value = portfolio1.NPV()

    reference_npv = option.NPV()

    print("%15s %25s %25s %25s" % (s, round(reference_npv,4), round(portfolio_value,4), round(reference_npv-portfolio_value,4)))
