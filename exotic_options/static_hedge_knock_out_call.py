from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
from pricing_options.Evaluation import Evaluation
from pricing_options.StaticHedgePortfolio import StaticHedgePortfolio
from pricing_options.Options import OptionBarrierEuropean
import Utilities.svi_prepare_vol_data as svi_data
from Utilities.utilities import *
from exotic_options import exotic_option_utilities as exotic
import QuantLib as ql
import pandas as pd
import os
import pickle
import numpy as np
import math

with open(os.path.abspath('..') + '/intermediate_data/svi_calibration_50etf_calls_noZeroVol_itd.pickle', 'rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/svi_dataset_50etf_calls_noZeroVol_itd.pickle', 'rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/total_hedging_bs_estimated_vols.pickle', 'rb') as f:
    estimated_vols = pickle.load(f)[0]

# Evaluation Settings
evalDate = ql.Date(17, 6, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()
contractType = '50etf'
engineType = 'AnalyticEuropeanEngine'
facevalue = 1
# i = 2
rf = 0.03
evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
evaluation = Evaluation(evalDate, daycounter, calendar)

maturitydt = calendar.advance(evalDate, ql.Period(3, ql.Months))  # contract maturity

svidata = svi_dataset.get(to_dt_date(evalDate))
paramset = calibrered_params_ts.get(to_dt_date(evalDate))
volSurface = SviVolSurface(evalDate, paramset, daycounter, calendar)
daily_close = svidata.spot
maturity_dates = sorted(svidata.dataSet.keys())
svi = SviPricingModel(volSurface, daily_close, daycounter, calendar,
                      to_ql_dates(maturity_dates), ql.Option.Call, contractType)
black_var_surface = svi.black_var_surface()
print(maturitydt)
underlying = ql.SimpleQuote(daily_close)
process = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
print(daily_close)
# Barrier Option
strike = daily_close
barrier = strike - 0.2

optiontype = ql.Option.Call
barrierType = ql.Barrier.DownOut
exercise = ql.EuropeanExercise(maturitydt)
payoff = ql.PlainVanillaPayoff(optiontype, strike)
barrieroption = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)

barrier_option = OptionBarrierEuropean(strike, maturitydt, optiontype, barrier, barrierType)
staticHedge = StaticHedgePortfolio(barrier_option)
# staticHedge.set_static_portfolio(evaluation,spot,black_var_surface)


ttm = daycounter.yearFraction(evalDate, maturitydt)
strike_barrier = ((barrier) ** 2) / strike
strike_barrierforward = ((barrier * np.exp(rf * ttm)) ** 2) / strike
strike_strikeforward = ((daily_close) ** 2) / strike

print('underlying : ', daily_close)
print('barrier : ', barrier)
print('strike : ', strike)
print('barrier forward : ', barrier * np.exp(rf * ttm))

barrier_engine = ql.AnalyticBarrierEngine(process)
european_engine = ql.AnalyticEuropeanEngine(process)
barrieroption.setPricingEngine(barrier_engine)
barrier_price = barrieroption.NPV()

# Construct Replicaiton Portfolio
portfolio = ql.CompositeInstrument()

# Long a call struck at strike
call = ql.EuropeanOption(payoff, exercise)
call.setPricingEngine(european_engine)
call_price = call.NPV()
print('call value : ', call_price)
portfolio.add(call)

# short put_ratio shares of puts struck at k_put
k_put = strike_barrierforward
print('k` : ', k_put)
put_payoff = ql.PlainVanillaPayoff(ql.Option.Put, k_put)
put = ql.EuropeanOption(put_payoff, exercise)
put.setPricingEngine(european_engine)


underlying.setValue(barrier)
callprice_at_barrier = call.NPV()
putprice_at_barrier = put.NPV()
put_ratio = callprice_at_barrier / putprice_at_barrier
# put_ratio = math.sqrt(strike/k_put)

print('put ratio : ', put_ratio)
portfolio.subtract(put, put_ratio)


underlying.setValue(daily_close)
portfolio_value = portfolio.NPV()
print('reference npv :', barrier_price)
print('replicate npv :', portfolio_value)
print('hedge error : ', barrier_price - portfolio_value)
print("=" * 100)
print("%15s %25s %25s %25s %25s %25s" % ("spot", "barrier_npv", "euro_call", "euro_put", "replicate npv", "pnl"))
print("-" * 100)
df = pd.DataFrame()
spot_range = np.arange(barrier - 0.1, strike + 0.1, 0.01)
barrier_npvs = []
call_npvs = []
put_npvs = []
portfolio_values = []
pnls = []
for s in spot_range:
    underlying.setValue(s)
    # barrier_npv = facevalue * exotic.barrier_npv_ql(evalDate, [], barrierType, barrier, payoff, exercise, process)
    call_npv = facevalue * call.NPV()
    put_npv = facevalue * put.NPV()
    if s <= barrier:
        portfolio_value = 0.0
        barrier_npv = 0.0
    else:
        price = exotic.calculate_barrier_price(evaluation, barrier_option, [], process, engineType)
        barrier_npv = facevalue * price

        portfolio_value = facevalue * portfolio.NPV()
    pnl =  portfolio_value - barrier_npv
    barrier_npvs.append(barrier_npv)
    call_npvs.append(call_npv)
    put_npvs.append((put_npv))
    portfolio_values.append(portfolio_value)
    pnls.append(pnl/barrier_price)
    print("%15s %25s %25s %25s %25s %25s" % (s, round(barrier_npv, 2), round(call_npv, 2), round(put_npv, 2),
                                             round(portfolio_value, 2), round(pnl/barrier_price, 2)))
df['Spot'] = spot_range
df['barrier_npv'] = barrier_npvs
df['call_npv'] = call_npvs
df['put_npv'] = put_npvs
df['replicate_portfolio'] = portfolio_values
df['pnl'] = pnls
# df.to_csv('static_hegde_knockout_call.csv')
df.to_csv(os.path.abspath('..') + '/results/static_hegde_knockout_call.csv')

