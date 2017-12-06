from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
from pricing_options.Evaluation import Evaluation
from pricing_options.StaticHedgePortfolio import StaticHedgePortfolio
from pricing_options.Options import OptionBarrierEuropean
import Utilities.svi_prepare_vol_data as svi_data
from Utilities.utilities import *
from exotic_options import exotic_option_utilities as exotic_util
import QuantLib as ql
import pandas as pd
import os
import pickle
import numpy as np
import math
from WindPy import w

with open(os.path.abspath('..') + '/intermediate_data/svi_calibration_50etf_calls_noZeroVol_itd.pickle', 'rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/svi_dataset_50etf_calls_noZeroVol_itd.pickle', 'rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/total_hedging_bs_estimated_vols.pickle', 'rb') as f:
    estimated_vols = pickle.load(f)[0]

w.start()
option_data = w.wsd("10000931.SH,10000893.SH", "close", "2017-07-14", "2017-11-20", "Fill=Previous")
call_265 = w.wsd("10000765.SH", "close", "2017-05-25", "2017-06-28", "Fill=Previous") # 50ETF购2017年6月2.495A
put_230 = w.wsd("10000732.SH", "close", "2017-05-25", "2017-06-28", "Fill=Previous") # 5A0ETF沽2017年6月2.153
put_data = put_230.Data[0]
call_data = call_265.Data[0]
print(put_data)
print(call_data)
# .tolist().index("2017-07-14")
# Evaluation Settings
evalDate = ql.Date(25, 5, 2017)
maturitydt = ql.Date(28, 6, 2017)
endDate = ql.Date(28, 6, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()

contractType = '50etf'
engineType = 'AnalyticEuropeanEngine'
facevalue = 1000
# i = 3
rf = 0.03

optionType = ql.Option.Call
barrierType = ql.Barrier.DownOut

evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
evaluation = Evaluation(evalDate, daycounter, calendar)

svidata = svi_dataset.get(to_dt_date(evalDate))
# paramset = calibrered_params_ts.get(to_dt_date(evalDate))
# volSurface = SviVolSurface(evalDate, paramset, daycounter, calendar)
daily_close = svidata.spot
# maturity_dates = sorted(svidata.dataSet.keys())
# svi = SviPricingModel(volSurface, daily_close, daycounter, calendar,
#                       to_ql_dates(maturity_dates), ql.Option.Call, contractType)
# black_var_surface = svi.black_var_surface()
ttm = daycounter.yearFraction(evalDate, maturitydt)

# print(black_var_surface.blackVol(ttm,2.495))
underlying = ql.SimpleQuote(daily_close)
# process = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
vol = estimated_vols.get(to_dt_date(evalDate))
process = evaluation.get_bsmprocess_cnstvol(daycounter,calendar,underlying,vol)
print(daily_close)
# barrierstrike = daily_close # 2.475
strike = 2.495
barrier = 2.30

exercise = ql.EuropeanExercise(maturitydt)
payoff = ql.PlainVanillaPayoff(optionType, strike)
barrieroption = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
# barrieroption.setPricingEngine(ql.AnalyticBarrierEngine(process))
# barrier_option = OptionBarrierEuropean(strike, maturitydt, optionType, barrier, barrierType)
# staticHedge = StaticHedgePortfolio(barrier_option)
# staticHedge.set_static_portfolio(evaluation,spot,black_var_surface)


strike_barrier = ((barrier) ** 2) / strike
strike_barrierforward = ((barrier * np.exp(rf * ttm)) ** 2) / strike
strike_strikeforward = ((daily_close) ** 2) / strike

print(maturitydt)
print('init spot',daily_close)
print('underlying : ', daily_close)
print('barrier : ', barrier)
print('strike : ', strike)
# print('barrier forward : ', barrier * np.exp(rf * ttm))
european_engine = ql.AnalyticEuropeanEngine(process)
barrier_engine = ql.AnalyticBarrierEngine(process)
barrieroption.setPricingEngine(barrier_engine)
barrier_price = barrieroption.NPV()
init_barrier = barrier_price
# Construct Replicaiton Portfolio
portfolio = ql.CompositeInstrument()

# Long a call struck at strike
call = ql.EuropeanOption(payoff, exercise)
call.setPricingEngine(european_engine)
call_value = call.NPV()
print('call value : ', call_value)
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
put_price = put_data[put_230.Times.index(to_dt_date(evalDate))]
call_price = call_data[call_265.Times.index(to_dt_date(evalDate))]
# put_ratio = (barrier_price-call_price)/put_price
# put_ratio = math.sqrt(strike/k_put)

print('put ratio : ', put_ratio)
portfolio.subtract(put, put_ratio)


underlying.setValue(daily_close)
portfolio_value = portfolio.NPV()

print('portfolio init value : ',portfolio_value)
print('barrier option init value : ',barrier_price)
#
# print(put_230.Data[0][put_230.Times.index(datetime.date(2017, 7, 14))])
# print(put_230.Times.index(datetime.date(2017, 7, 14)))
#

price_cont = []
dates = []
hist_spots = []
portfolio_prices = []
portfolio_values  =[]
pnls_value = []
pnls_price = []
callprices = []
putprices = []
spots = []
while evalDate < endDate:
    try:
        evaluation = Evaluation(evalDate, daycounter, calendar)
        if daily_close <= barrier: break
        put_price = put_data[put_230.Times.index(to_dt_date(evalDate))]
        call_price = call_data[call_265.Times.index(to_dt_date(evalDate))]
        portfolio_price = call_price-put_ratio*put_price
        svidata = svi_dataset.get(to_dt_date(evalDate))
        paramset = calibrered_params_ts.get(to_dt_date(evalDate))
        volSurface = SviVolSurface(evalDate, paramset, daycounter, calendar)
        daily_close = svidata.spot

        maturity_dates = sorted(svidata.dataSet.keys())
        svi = SviPricingModel(volSurface, daily_close, daycounter, calendar,
                              to_ql_dates(maturity_dates), ql.Option.Call, contractType)
        black_var_surface = svi.black_var_surface()
        # const_vol = estimated_vols.get(to_dt_date(evalDate))
        # print(black_var_surface.blackVol(ttm,daily_close))
        underlying = ql.SimpleQuote(daily_close)
        # process = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)

        # vol = estimated_vols.get(to_dt_date(evalDate))
        ttm = daycounter.yearFraction(evalDate, maturitydt)

        vol = black_var_surface.blackVol(ttm,daily_close)
        if not vol > 0.0: vol = estimated_vols.get(to_dt_date(evalDate))
        process = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, vol)

        barrier_engine = ql.AnalyticBarrierEngine(process)
        barrieroption.setPricingEngine(barrier_engine)
        barrier_price = barrieroption.NPV()
        # barrier_price = exotic_util.calculate_barrier_price(evaluation, barrier_option, hist_spots, process, engineType)
        european_engine = ql.AnalyticEuropeanEngine(process)
        call.setPricingEngine(european_engine)
        put.setPricingEngine(european_engine)
        # portfolio.setPricingEngine(european_engine)
        portfolio_value = portfolio.NPV()
        call_value = call.NPV()
        put_value = put.NPV()
        pnl_price = (portfolio_price-barrier_price)/init_barrier
        pnl_value = (portfolio_value-barrier_price)/init_barrier
        pnls_price.append(pnl_price)
        pnls_value.append(pnl_value)
        spots.append(daily_close)
        portfolio_prices.append(portfolio_price*facevalue)
        portfolio_values.append(portfolio_value*facevalue)
        callprices.append(call_price)
        putprices.append(put_price)
        print(evalDate,pnl_price, pnl_value)
        # print('spot',daily_close,strike)
        # print(portfolio_price,portfolio_value)
        # print(call_price,call_value)
        # print(put_price,put_value)
        hist_spots.append(daily_close)
        dates.append(evalDate)
        price_cont.append(barrier_price*facevalue)
    except Exception as e:
        print(evalDate,e)
        print('option price unavailable')
    evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
results = {'3exotic prices':price_cont}
results.update({'1dates':dates})
results.update({'2underlyings':spots})
results.update({'4portfolio price':portfolio_prices})
results.update({'4portfolio value':portfolio_values})
results.update({'pnls price':pnls_price})
results.update({'pnls value':pnls_value})
results.update({'call':callprices})
results.update({' put':putprices})
df = pd.DataFrame(data=results)
# print(df)
df.to_csv(os.path.abspath('..') + '/results/exotic_option_prices_2.csv')
