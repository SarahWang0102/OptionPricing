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
import os
import pickle

def implied_vol_function(params,x_svi):
    a_star, b_star, rho_star, m_star, sigma_star = params
    iv = np.sqrt( a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))
    return iv

def calculate_delta(hedge_date,params_Mi,spot,rf_h_d,strike,maturitydt,optiontype):
    step = 0.01
    rf = rf_h_d
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, rf, daycounter))
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, 0.0, daycounter))
    exercise = ql.EuropeanExercise(maturitydt)
    payoff = ql.PlainVanillaPayoff(optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)
    ttm = daycounter.yearFraction(hedge_date, maturitydt)

    s_plus = spot + step
    s_minus = spot - step
    Ft_plus = s_plus * math.exp(rf * ttm)
    x_plus = math.log(strike / Ft_plus, math.e)
    Ft_minus = s_minus * math.exp(rf * ttm)
    x_minus = math.log(strike / Ft_minus, math.e)
    iv_plus = implied_vol_function(params_Mi,x_plus)
    iv_minus = implied_vol_function(params_Mi,x_minus)
    flat_vol_plus = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(hedge_date, calendar, iv_plus, daycounter))
    flat_vol_minus = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(hedge_date, calendar, iv_minus, daycounter))

    process_plus = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(s_plus)), dividend_ts, yield_ts, flat_vol_plus)
    process_minus = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(s_minus)), dividend_ts, yield_ts,
                                                flat_vol_minus)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process_plus))
    npv_plus = option.NPV()
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process_minus))
    npv_minus = option.NPV()
    delta = (npv_plus-npv_minus)/(s_plus-s_minus)
    return delta

def calculate_cash_position(hedge_date,option_price,spot,delta):
    cash_position = option_price - delta*spot
    return cash_position

def calculate_hedging_error(hedge_date,liquidition_date,spot,option_price,delta,cash_position,rf_from_curve):
    t = daycounter.yearFraction(hedge_date, liquidition_date)
    hedging_error = delta*spot + cash_position*math.exp(rf_from_curve * t) - option_price
    return hedging_error

def get_spot_price(evalDate):
    # Uderlying market price
    underlyingdata = pd.read_json(os.getcwd() + '\marketdata\spotclose' + '.json')
    spot_ts = underlyingdata.values.tolist()
    dates_ts = underlyingdata.index.tolist()
    dt = datetime.datetime(evalDate.year(), evalDate.month(), evalDate.dayOfMonth(),
                           dates_ts[0].hour, dates_ts[0].minute, dates_ts[0].second, dates_ts[0].microsecond)
    spot = spot_ts[dates_ts.index(dt)][0]
    return spot

start = timeit.default_timer()
np.random.seed()
w.start()
#begDate = ql.Date(1, 12, 2016)
begDate = ql.Date(15, 7, 2017)
endDate = ql.Date(20, 7, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = begDate
daily_params = {}
daily_option_prices = {}
daily_spots = {}
daily_svi_dataset = {}
dates = []
while evalDate <= endDate:
    print('Start : ', evalDate)
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    ql.Settings.instance().evaluationDate = evalDate
    try:
        #vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = wind_data.get_wind_data(evalDate)
        cal_vols, put_vols, expiration_dates, spot, rf_months = svi_data.get_call_put_impliedVols_moneyness_PCPrate_pcvt(
            evalDate, daycounter, calendar, maxVol=1.0, step=0.0001, precision=0.001, show=False)
        data_months = svi_util.orgnize_data_for_optimization(
            evalDate, daycounter, cal_vols, put_vols, expiration_dates, spot)
        #print(data_months)
    except:
        continue
    svi_dataset =  cal_vols, put_vols, expiration_dates, spot, rf_months
    daily_svi_dataset.update({evalDate:svi_dataset})
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
        params = svi_util.get_svi_optimal_params(data, ttm, 20)
        params_months.append(params)
    daily_params.update({evalDate:params_months})
    dates.append(evalDate)
    print('Finished : ',evalDate)
    print(params_months[0])
    print(params_months[1])
    print(params_months[2])
    print(params_months[3])

#print(daily_params)
timebreak1 = timeit.default_timer()
print('calibration time : ',timebreak1-start)


# Hedge option using underlying 50ETF
dailly_hedge_error_Ms = {}
option_last_close_Ms = {}

print(dates)
for idx_date,date in enumerate(dates[0:len(dates)-3]):
    try:
        print(idx_date)
        calibrate_date = dates[idx_date]
        hedge_date = dates[idx_date+1]
        liquidition_date = dates[idx_date+2]
        dataset_on_liquidition_date = daily_svi_dataset.get(liquidition_date)
        cal_vols, put_vols, expiration_dates, spot, rf_months = dataset_on_liquidition_date
        # CALL OPTION DATA!!
        data_months = svi_util.orgnize_data_for_hedging( liquidition_date, daycounter, cal_vols, put_vols, expiration_dates, spot)
        optiontype = ql.Option.Call

        calibrated_params = daily_params.get(calibrate_date) # on calibrate_date
        rfs_on_hedge_date = svi_data.calculate_PCParity_ATM_riskFreeRate(hedge_date, daycounter, calendar)
        curve = svi_data.get_curve_treasury_bond(liquidition_date,daycounter)
        hedge_error_Ms = {}
        for nbr_month in range(4):
            params_Mi = calibrated_params[nbr_month]
            #rf = rf_months.get(nbr_month)

            rf_on_hedge_date = rfs_on_hedge_date.get(nbr_month)
            if nbr_month in option_last_close_Ms.keys():
                closes_on_hedge_date = option_last_close_Ms.get(nbr_month)
            else:
                closes_on_hedge_date = [0.0]*50
            data_Mi = data_months.get(nbr_month)
            moneyness, strikes, close_prices, expiration_date = data_Mi
            spot_on_hedge_date = get_spot_price(hedge_date)
            rf = curve.zeroRate(expiration_date, daycounter, ql.Continuous).rate()
            option_last_closes = []
            hedge_errors = []
            for idx_k,k in enumerate(strikes):
                close = close_prices[idx_k]
                close_on_hedge_date = closes_on_hedge_date[idx_k]
                delta = calculate_delta(hedge_date,params_Mi,spot_on_hedge_date,rf_on_hedge_date,k,expiration_date,optiontype) # on hedge date
                cash_on_hedge_date = calculate_cash_position(hedge_date, close_on_hedge_date, spot_on_hedge_date, delta) # on hedge date
                hedge_error = calculate_hedging_error(hedge_date,liquidition_date,spot,close,delta,cash_on_hedge_date,rf)
                option_last_closes.append(close)
                hedge_errors.append(hedge_error)
            option_last_close_Ms.update({nbr_month:option_last_closes})
            hedge_error_Ms.update({nbr_month:hedge_errors})
        print('liquidition date : ',liquidition_date)
        print('hedge errors : ',hedge_error_Ms)
        if idx_date != 0: dailly_hedge_error_Ms.update({date: hedge_error_Ms})
    except Exception as e:
        print(e)
        continue



stop = timeit.default_timer()
print('calibration time : ',stop-start)

print('dailly_hedge_error_Ms = ',dailly_hedge_error_Ms)
#with open('dailly_hedge_errors.pickle') as f:
#    pickle.dump([dailly_hedge_error_Ms],f)





