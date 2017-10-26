from Utilities.svi_read_data import get_commodity_m_data
from Utilities.svi_prepare_vol_data import calculate_vol_BS
from calibration.SviCalibrationInput import SviInputSet
import Utilities.svi_calibration_utility as svi_util
import math
import pandas as pd
import matplotlib.pyplot as plt
from Utilities.utilities import *
import numpy as np
import datetime
import os
import pickle



evalDate = ql.Date(20, 7, 2017)
#evalDate = ql.Date(28, 9, 2017)
endDate = ql.Date(9, 9, 2017)
core_contracts = ['801','805']
calendar = ql.China()
daycounter = ql.ActualActual()

svi_dataset = {}
calibrered_params_ts = {}
count = 0
while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    ql.Settings.instance().evaluationDate = evalDate
    print(evalDate)
    try:
        curve = get_curve_treasury_bond(evalDate, daycounter)
        results_call, results_put, underlying_prices = get_commodity_m_data(evalDate,calendar)
    except:
        continue
    yield_ts = ql.YieldTermStructureHandle(curve)
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))

    svi_data = SviInputSet(to_dt_date(evalDate))
    for maturitydt in results_call.keys():
        mktdata = results_call.get(maturitydt)
        contractid = mktdata[0][-1]
        if contractid[-3:] not in core_contracts:
            continue
        spot = underlying_prices.get(contractid)
        mdate = datetime.date(maturitydt.year(), maturitydt.month(), maturitydt.dayOfMonth())
        for data in mktdata:
            strike = data[0]
            close = data[1]
            volum = data[2] # 万元
            if volum == 0.0: continue
            open_price = ''
            Ft = spot
            moneyness = math.log(strike/Ft, math.e)
            optiontype = ql.Option.Call
            exercise = ql.EuropeanExercise(maturitydt)
            payoff = ql.PlainVanillaPayoff(optiontype, strike)
            option = ql.EuropeanOption(payoff, exercise)
            flat_vol_ts = ql.BlackVolTermStructureHandle(
                ql.BlackConstantVol(evalDate, calendar, 0.0, daycounter))
            process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,
                                                   flat_vol_ts)
            option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
            #error = 0.0
            try:
                implied_vol = option.impliedVolatility(close, process, 1.0e-4, 300, 0.0, 4.0)
            except RuntimeError:
                continue
            ttm = daycounter.yearFraction(evalDate, maturitydt)
            totalvariance = (implied_vol ** 2) * ttm
            svi_data.update_data(mdate, strike, moneyness, implied_vol, ttm, totalvariance, close, open_price,spot,volum)
        svi_dataset.update({to_dt_date(evalDate): svi_data})


    calibrered_params = {}
    for mdate in svi_data.dataSet.keys():
        optimization_data = []
        data_mdate = svi_data.dataSet.get(mdate)
        logMoneynesses = data_mdate.moneyness
        totalvariance = data_mdate.totalvariance
        vol = data_mdate.volatility
        #print('vols : ',vol)
        optimization_data.append(logMoneynesses)
        optimization_data.append(data_mdate.totalvariance)
        ttm = data_mdate.ttm
        params = svi_util.get_svi_optimal_params(optimization_data, ttm, 1)
        #print('params : ',params)
        calibrered_params.update({mdate:params})
        a_star, b_star, rho_star, m_star, sigma_star = params
        x_svi = np.arange(min(logMoneynesses)-0.005, max(logMoneynesses)+0.02, 0.1/100)  # log_forward_moneyness
        tv_svi = np.multiply(
            a_star + b_star*(rho_star*(x_svi-m_star)+np.sqrt((x_svi - m_star)**2 + sigma_star**2)), ttm)
        vol_svi = np.sqrt(
            a_star + b_star*(rho_star*(x_svi-m_star) + np.sqrt((x_svi - m_star)**2 + sigma_star**2)))
        #plt.figure()
        #plt.plot(logMoneynesses, vol, 'ro')
        #plt.plot(x_svi, vol_svi, 'b--')
        #plt.title('vol, '+str(evalDate)+', '+str(mdate))
        #plt.figure()
        #count += 1
        #plt.plot(logMoneynesses, totalvariance, 'ro')
        #plt.plot(x_svi, tv_svi, 'b--')
        #plt.title('tv, '+str(evalDate)+', '+str(mdate))
    #plt.show()
    #print(calibrered_params)
    calibrered_params_ts.update({to_dt_date(evalDate):calibrered_params})
print('calibrered_params_ts',calibrered_params_ts)
with open(os.path.abspath('..')+'/intermediate_data/svi_calibration_m_calls.pickle','wb') as f:
    pickle.dump([calibrered_params_ts],f)

print('svi',svi_dataset)
with open(os.path.abspath('..')+'/intermediate_data/svi_dataset_m_calls.pickle','wb') as f:
    pickle.dump([svi_dataset],f)









