
import exotic_options.exotic_option_utilities as exotic_otil
from Utilities.utilities import *
import Utilities.hedging_utility as hedge_util
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import Utilities.plot_util as pu



# Evaluation Settings
today = ql.Date(29,5,2006)
ql.Settings.instance().evaluationDate = today

optiontype = ql.Option.Put
barrierType = ql.Barrier.DownOut
barrier = 70.0
spot = 100.0
strike = 100.0
underlying = ql.SimpleQuote(spot)
vol_handle = ql.QuoteHandle(ql.SimpleQuote(0.2))
rf_handle = ql.QuoteHandle(ql.SimpleQuote(0.04))

maturity = today + 1*ql.Years
daycounter = ql.Actual365Fixed()




flat_rate = ql.YieldTermStructureHandle(ql.FlatForward(0,ql.NullCalendar(), rf_handle, daycounter))
flat_vol = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0,ql.NullCalendar(), vol_handle, daycounter))
exercise = ql.EuropeanExercise(maturity)
payoff = ql.PlainVanillaPayoff(optiontype, strike)

option = ql.BarrierOption(barrierType, barrier, 0.0,payoff, exercise)
bs_process = ql.BlackScholesProcess(ql.QuoteHandle(underlying), flat_rate,flat_vol)
barrier_engine = ql.AnalyticBarrierEngine(bs_process)
european_engine = ql.AnalyticEuropeanEngine(bs_process)
option.setPricingEngine(barrier_engine)
reference_npv = option.NPV()
print('reference npv :',reference_npv)

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

inner_maturity = maturity
idx = 12
while idx >= 1:
    inner_maturity = today + idx*ql.Months
    inner_exercise = ql.EuropeanExercise(inner_maturity)
    inner_payoff = ql.PlainVanillaPayoff(ql.Option.Put,barrier)
    putn = ql.EuropeanOption(inner_payoff,inner_exercise)
    putn.setPricingEngine(european_engine)
    kill_date = today + (idx-1)*ql.Months
    ql.Settings.instance().evaluationDate = kill_date
    underlying.setValue(barrier)
    portfolio_value = portfolio.NPV()
    put_value = putn.NPV()
    notional = portfolio_value/put_value
    portfolio.subtract(putn,notional)
    idx -= 1
print(portfolio)

ql.Settings.instance().evaluationDate = today
underlying.setValue(spot)
portfolio_value = portfolio.NPV()
print(portfolio_value)
print('portfolio npv :',portfolio_value)


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