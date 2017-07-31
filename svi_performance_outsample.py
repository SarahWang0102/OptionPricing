import svi_read_data as wind_data
import svi_prepare_vol_data as svi_data
import QuantLib as ql
import pandas as pd
import math
import numpy as np

# Calibrate based on market data one day before
evalDate = ql.Date(14,7,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
params_month0 =  -0.442190449383, 1.88495933915, 0.0113239298356, 0.0102760514872, 0.246395133895
params_month1 =  0.0027154378929, 0.1201944098, -0.141331089153, 0.01945999699, 0.194002279093
params_month2 =  0.00167809322339, 0.536900997282, 0.733311043179, 0.071223058622, 0.0618405058673
params_month3 =  0.0107047521466, 0.297485230118, 0.647754886901, 0.0262354285707, 0.0554674716145
rf_container = svi_data.calculate_PCParity_riskFreeRate(evalDate, daycounter, calendar) # rf is also considered calibrated results.
dividend_ts  = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))

month_indexs = wind_data.get_contract_months(evalDate)
sse = 0
print("-" * 80)
print("SVI Out of Sample Performance:")
print("=" * 80)
print(" %15s %25s %25s " % ("market price","model price", "square error(* e-4)"))

# get market price for next busuness day
evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = wind_data.get_wind_data(evalDate)
ql.Settings.instance().evaluationDate = evalDate
for idx, optionid in enumerate(optionids):
    optionDataIdx = optionData[optionFlds.index('wind_code')].index(optionid)
    mdate = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
    maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
    mktindex = mktData[mktFlds.index('option_code')].index(optionid)
    strike = optionData[optionFlds.index('exercise_price')][optionDataIdx]
    close = mktData[mktFlds.index('close')][mktindex]
    ttm = daycounter.yearFraction(evalDate, maturitydt)
    nbr_month = maturitydt.month()
    if nbr_month == month_indexs[0]:
        a, b, rho, m, sigma = params_month0
        rf = min(0.0002, rf_container.get(0).get(strike))
    if nbr_month == month_indexs[1]:
        a, b, rho, m, sigma = params_month1
        rf = min(0.0002, rf_container.get(1).get(strike))
    elif nbr_month == month_indexs[2]:
        a, b, rho, m, sigma = params_month2
        rf = min(0.0002, rf_container.get(2).get(strike))
    else:
        a, b, rho, m, sigma = params_month3
        rf = min(0.0002, rf_container.get(3).get(strike))
    if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
        optiontype = ql.Option.Call
    else:
        optiontype = ql.Option.Put
    Ft = spot * math.exp(rf * ttm)
    moneyness = math.log(strike / Ft, math.e)
    vol_svi = np.sqrt(a + b * (rho * (moneyness - m) + np.sqrt((moneyness - m) ** 2 + sigma ** 2)))
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, vol_svi, daycounter))
    exercise = ql.EuropeanExercise(maturitydt)
    payoff = ql.PlainVanillaPayoff(optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)
    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,flat_vol_ts)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
    model_price = option.NPV()
    squared_error = (model_price - close) ** 2
    sse += squared_error
    print(" %15s %25s %25s " % (round(close, 6), round(model_price, 6), round(squared_error * 10000, 6)))

print("-" * 80)
print(" %15s %25s %25s " % ("","SSE:", round(sse,6)))
print("-" * 80)