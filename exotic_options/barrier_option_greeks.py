import QuantLib as ql
import numpy as np
from exotic_options import exotic_option_utilities as exotic_util

evalDate = ql.Date(19,1,2017)
maturityDate = ql.Date(19,7,2017)
calendar = ql.China()
daycounter = ql.ActualActual()

spot = 100
strike = 100
barrier = 105
rf = 0.03

optionType = ql.Option.Call
hist_spots = []

# up out call
barrierType = ql.Barrier.UpIn


vol = 0.2
#
for vol in np.arange(0.1,0.3,0.01):
    underlying = ql.SimpleQuote(spot)
    exercise = ql.EuropeanExercise(maturityDate)
    payoff = ql.PlainVanillaPayoff(optionType, strike)
    flat_d = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
    flat_yts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,rf,daycounter))
    flat_vol = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, vol, daycounter))
    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying), flat_d, flat_yts, flat_vol)
    barrier_price = exotic_util.barrier_npv_ql(
        evalDate, hist_spots, barrierType, barrier, payoff, exercise, process)
    ql.Settings.instance().evaluationDate = evalDate
    european_engine = ql.AnalyticEuropeanEngine(process)
    euro_option = ql.EuropeanOption(payoff,exercise)
    euro_option.setPricingEngine(european_engine)
    euro_price = euro_option.NPV()
    print(barrier_price,euro_price)
