# -*- coding: utf-8 -*-
import svi_read_data as wind_data
import QuantLib as ql
import pandas as pd


def calulate_market_model_price_sse(
        spot, mktData, mktFlds, optionData, optionFlds, optionids,yield_ts,dividend_ts,flat_vol_ts):
    try:
        sse = 0.0
        for idx, optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt      = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex        = mktData[mktFlds.index('option_code')].index(optionid)
            strike          = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close           = mktData[mktFlds.index('close')][mktindex]
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                optiontype = ql.Option.Call
            else:
                optiontype = ql.Option.Put
            exercise = ql.EuropeanExercise(maturitydt)
            payoff   = ql.PlainVanillaPayoff(optiontype, strike)
            option   = ql.EuropeanOption(payoff, exercise)
            process  = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,
                                                   flat_vol_ts)
            option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
            model_price = option.NPV()
            if model_price == 0.0 : continue
            squared_error = (model_price - close)**2
            #print(" %15s %25s %25s " % (round(close,6),round(model_price,6), round(squared_error*10000,6)))
            sse += squared_error
    except:
        print('Error -- calulate_market_model_price_sse failed')
        return
    return sse

def estimiate_bs_constant_vol(evalDate, calendar, daycounter):
    try:
        vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = wind_data.get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        curve       = wind_data.get_curve_treasury_bond(evalDate, daycounter)
        yield_ts    = ql.YieldTermStructureHandle(curve)
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
        vol = 1.0
        step = 0.0005
        min_sse = 10000
        estimate_vol = 0.0
        while vol > step:
            flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, vol, daycounter))
            sse = calulate_market_model_price_sse(
                spot, mktData, mktFlds, optionData, optionFlds, optionids, yield_ts, dividend_ts, flat_vol_ts)
            if sse < min_sse:
                min_sse = sse
                estimate_vol = vol
            vol -= step
    except:
        print('Error -- estimiate_bs_constant_vol failed')
        return
    return estimate_vol,min_sse

evalDate = ql.Date(14,7,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
# estimate_vol,min_sse = estimiate_bs_constant_vol(evalDate, calendar, daycounter)
#print(estimate_vol,' ',min_sse) # 0.15410000000009316   0.011299317884210248

estimate_vol = 0.15410000000009316
vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = wind_data.get_wind_data(evalDate)
ql.Settings.instance().evaluationDate = evalDate
curve       = wind_data.get_curve_treasury_bond(evalDate, daycounter)
yield_ts    = ql.YieldTermStructureHandle(curve)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, estimate_vol, daycounter))
print("-" * 80)
print("BS In Sample Performance:")
print("=" * 80)
print(" %15s %25s %25s " % ("market price","model price", "square error(* e-4)"))
sse         = calulate_market_model_price_sse(
                spot, mktData, mktFlds, optionData, optionFlds, optionids, yield_ts, dividend_ts, flat_vol_ts)
print("-" * 80)
print(" %15s %25s %25s " % ("","SSE:", round(sse,6)))
print("-" * 80)