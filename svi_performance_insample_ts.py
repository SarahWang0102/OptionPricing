import svi_read_data as wind_data
import svi_prepare_vol_data as svi_data
import svi_calibration_utility as svi_util
import QuantLib as ql
import pandas as pd
import math
import numpy as np
from WindPy import w
import datetime
import timeit

start = timeit.default_timer()
np.random.seed()
w.start()
begDate = ql.Date(1, 12, 2016)
#begDate = ql.Date(10, 7, 2017)
endDate = ql.Date(20, 7, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()
sse_container = {}
evalDate = begDate

while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    print(evalDate)
    ql.Settings.instance().evaluationDate = evalDate
    try:
        vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = wind_data.get_wind_data(evalDate)
        curve = svi_data.get_curve_treasury_bond(evalDate, daycounter)
        data_months, rf_container = svi_util.get_data_from_BS_OTM_PCPRate(evalDate, daycounter, calendar, curve, False)
    except:
        continue
    #print(rf_container)
    # rf_container = svi_data.calculate_PCParity_riskFreeRate(evalDate, daycounter, calendar)
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
    month_indexs = wind_data.get_contract_months(evalDate)
    params_months = []
    for i in range(4):
        nbr_month = month_indexs[i]
        data = data_months.get(i)
        logMoneynesses = data[0]
        totalvariance = data[1]
        expiration_date = data[2]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        #svi_util.get_svi_optimal_params(data, ttm, 20)
        params = svi_util.get_svi_optimal_params(data, ttm, 50)
        params_months.append(params)
    #print(evalDate,' : ',params_months)

    print('final_params : ', params_months)
    print("-" * 80)
    print("SVI In Sample Performance:")
    print("=" * 80)
    print(" %15s %25s %25s " % ("market price", "model price", "square error(* e-4)"))

    sse = 0
    for idx, optionid in enumerate(optionids):
        try:
            optionDataIdx = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex = mktData[mktFlds.index('option_code')].index(optionid)
            strike = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close = mktData[mktFlds.index('close')][mktindex]

            ttm = daycounter.yearFraction(evalDate, maturitydt)
            nbr_month = maturitydt.month()
            if nbr_month == month_indexs[0]:
                a, b, rho, m, sigma = params_months[0]
                rf =  rf_container.get(0)
            if nbr_month == month_indexs[1]:
                a, b, rho, m, sigma = params_months[1]
                rf = rf_container.get(1)
            elif nbr_month == month_indexs[2]:
                a, b, rho, m, sigma = params_months[2]
                rf =  rf_container.get(2)
            else:
                a, b, rho, m, sigma = params_months[3]
                rf =  rf_container.get(3)
            Ft = spot * math.exp(rf * ttm)
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                optiontype = ql.Option.Call
                if close <= spot - strike or close <= Ft - strike: continue
            else:
                optiontype = ql.Option.Put
                if close <= strike - spot or close <= strike - Ft: continue
            moneyness = math.log(strike / Ft, math.e)
            vol_svi = np.sqrt(a + b * (rho * (moneyness - m) + np.sqrt((moneyness - m) ** 2 + sigma ** 2)))
            yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
            dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
            flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, vol_svi, daycounter))
            exercise = ql.EuropeanExercise(maturitydt)
            payoff = ql.PlainVanillaPayoff(optiontype, strike)
            option = ql.EuropeanOption(payoff, exercise)
            process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts, flat_vol_ts)
            option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
            model_price = option.NPV()
            if model_price == 0.0:continue
            squared_error = (model_price - close) ** 2
            sse += squared_error
            print(" %15s %25s %25s " % (round(close, 6), round(model_price, 6), round(squared_error * 10000, 6)))
        except:
            sse = 'NAN'
    sse_container.update({evalDate:sse})
    print('SSE : ' ,sse)
print("=" * 80)
print(" %15s %25s " % ("EvalDate", "SSE"))
for date in sse_container.keys():
    e = sse_container.get(date)
    d = datetime.date(date.year(),date.month(),date.dayOfMonth())
    if e == 'NAN': continue
    print(" %15s %25s " % (d, round(e, 6)))
print("-" * 80)

print('sse_container = ',sse_container)
stop = timeit.default_timer()
print('time : ',stop-start)