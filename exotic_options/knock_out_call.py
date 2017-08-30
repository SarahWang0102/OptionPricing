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
today = ql.Date(14,7,2017)
calendar = ql.China()
daycounter = ql.ActualActual()

simulation_no = 1000
noise = np.random.normal(0,1,(simulation_no,len(dates)))
delta_t = 1.0/365
i = 3

optiontype = ql.Option.Call
barrierType = ql.Barrier.DownOut

calibrated_params = daily_params.get(to_dt_date(today))  # on calibrate_date
cal_vols, put_vols, maturity_dates, spot, risk_free_rates = daily_svi_dataset.get(to_dt_date(today))
black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params, to_ql_dates(maturity_dates),
                                                            today, daycounter, calendar, spot, risk_free_rates)
maturityDate = to_ql_date(maturity_dates[i])
rf = risk_free_rates.get(i)
params =  calibrated_params[i]
barrier = 0.9*spot
strike = spot

print('barrier : ', barrier)
print('strike : ', strike)

ql.Settings.instance().evaluationDate = today
yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(today, rf, daycounter))
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(today, 0.0, daycounter))
exercise = ql.EuropeanExercise(maturityDate)
payoff = ql.PlainVanillaPayoff(optiontype, strike)

option = ql.BarrierOption(barrierType, barrier, 0.0,payoff, exercise)
process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts,
                                       yield_ts, ql.BlackVolTermStructureHandle(black_var_surface))
barrier_engine = ql.AnalyticBarrierEngine(process)
european_engine = ql.AnalyticEuropeanEngine(process)
option.setPricingEngine(barrier_engine)
reference_npv = option.NPV()
print(reference_npv)

portfolio = ql.CompositeInstrument()
# Long a put struck at strike
put1 = ql.EuropeanOption(payoff,exercise)
put1.setPricingEngine(european_engine)
portfolio.add(put1)
# minus a digital put struck at barrier of notional strike-barrier
digital_payoff = ql.CashOrNothingPayoff(ql.Option.Put, barrier, 1.0)
digital_put = ql.EuropeanOption(digital_payoff,exercise)
digital_put.setPricingEngine(european_engine)
portfolio.subtract(digital_put,strike-barrier)
# minus a put option struck at barrier
lowerPayoff = ql.PlainVanillaPayoff(ql.Option.Put, barrier)
put2 = ql.EuropeanOption(lowerPayoff,exercise)
put2.setPricingEngine(european_engine)
portfolio.subtract(put2)

# Now we use puts struck at B to kill the value of the
# portfolio on a number of points (B,t).  For the first
# portfolio, we'll use 12 dates at one-month's distance.

inner_maturity = maturityDate
while inner_maturity > today:
    print(inner_maturity)
    inner_exercise = ql.EuropeanExercise(inner_maturity)
    inner_payoff = ql.PlainVanillaPayoff(ql.Option.Put,barrier)
    putn = ql.EuropeanOption(inner_payoff,inner_exercise)

    inner_maturity = calendar.advance(inner_maturity, ql.Period(-1, ql.Months))
    ql.Settings.instance().evaluationDate = inner_maturity
    underlying = barrier
    process1 = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(underlying)), dividend_ts,
                                           yield_ts, ql.BlackVolTermStructureHandle(black_var_surface))
    putn.setPricingEngine(ql.AnalyticEuropeanEngine(process1))
    #portfolio.setPricingEngine(ql.AnalyticEuropeanEngine(process1))
    portfolio_value = portfolio.NPV()
    put_value = putn.NPV()
    notional = portfolio_value/put_value
    portfolio.subtract(putn,notional)

print(portfolio)

ql.Settings.instance().evaluationDate = today
#portfolio.setPricingEngine(european_engine)

portfolio_value = portfolio.NPV()
print(portfolio_value)


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