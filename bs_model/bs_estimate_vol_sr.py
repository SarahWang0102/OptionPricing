# -*- coding: utf-8 -*-
from Utilities.svi_read_data import get_curve_treasury_bond
from Utilities import utilities as util
import QuantLib as ql
import pandas as pd
import pickle
import os

with open(os.path.abspath('..') + '/intermediate_data/svi_dataset_sr_calls.pickle', 'rb') as f:
    svi_dataset = pickle.load(f)[0]

print(svi_dataset)

optiontype = ql.Option.Call
daycounter = ql.ActualActual()
calendar = ql.China()

dates = svi_dataset.keys()
print(dates)
estimated_vols = {}
# for evalDate in dates:
#     # if evalDate in estimated_vols.keys(): continue
#     svi_data = svi_dataset.get(evalDate).dataSet
#     curve = get_curve_treasury_bond(util.to_ql_date(evalDate), daycounter)
#     yield_ts = ql.YieldTermStructureHandle(curve)
#     dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(util.to_ql_date(evalDate), 0.0, daycounter))
#     vol = 0.2
#     minvol = 0.01
#     step = 0.00005
#     min_sse = 1000000000
#     estimate_vol = 0.0
#     while vol > minvol:
#         flat_vol_ts = ql.BlackVolTermStructureHandle(
#             ql.BlackConstantVol(util.to_ql_date(evalDate), calendar, vol, daycounter))
#
#         sse = 0.0
#         for mdate in svi_data.keys():
#             data_mdate = svi_data.get(mdate)
#             strikes = data_mdate.strike
#             spot = data_mdate.spot
#             for i in range(len(strikes)):
#                 maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
#                 strike = strikes[i]
#                 close = data_mdate.close[i]
#
#                 exercise = ql.EuropeanExercise(maturitydt)
#                 payoff = ql.PlainVanillaPayoff(optiontype, strike)
#                 option = ql.EuropeanOption(payoff, exercise)
#                 process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,
#                                                        flat_vol_ts)
#                 option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
#                 try:
#                     model_price = option.NPV()
#                 except:
#                     model_price = 0.0
#                 # if model_price == 0.0: continue
#                 squared_error = (model_price - close) ** 2
#                 # print(" %15s %25s %25s " % (round(close,6),round(model_price,6), round(squared_error*10000,6)))
#                 sse += squared_error
#         if sse < min_sse:
#             min_sse = sse
#             estimate_vol = vol
#         vol -= step
#     estimated_vols.update({evalDate: estimate_vol})
#     print(evalDate, ' : ', estimate_vol)

for evalDate in dates:
    # if evalDate in estimated_vols.keys(): continue
    ql.Settings.instance().evaluationDate = util.to_ql_date(evalDate)
    svi_data = svi_dataset.get(evalDate).dataSet
    curve = get_curve_treasury_bond(util.to_ql_date(evalDate), daycounter)
    yield_ts = ql.YieldTermStructureHandle(curve)
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(util.to_ql_date(evalDate), 0.0, daycounter))
    vol = 0.0
    flat_vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(util.to_ql_date(evalDate), calendar, vol, daycounter))
    vols = []
    for mdate in svi_data.keys():
        data_mdate = svi_data.get(mdate)
        strikes = data_mdate.strike
        spot = data_mdate.spot
        for i in range(len(strikes)):
            maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
            strike = strikes[i]
            close = data_mdate.close[i]

            exercise = ql.EuropeanExercise(maturitydt)
            payoff = ql.PlainVanillaPayoff(optiontype, strike)
            option = ql.EuropeanOption(payoff, exercise)
            process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,
                                                   flat_vol_ts)
            option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
            implied_vol = option.impliedVolatility(close, process, 1.0e-4, 300, 0.0, 4.0)
            vols.append(implied_vol)
    estimate_vol = sum(vols)/len(vols)
    estimated_vols.update({evalDate: estimate_vol})
    print(evalDate, ' : ', estimate_vol)

with open(os.path.abspath('..') + '/intermediate_data/bs_estimite_vols_sr_calls.pickle', 'wb') as f:
    pickle.dump([estimated_vols], f)
