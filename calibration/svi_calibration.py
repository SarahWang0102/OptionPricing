from Utilities.svi_read_data import get_wind_data
from Utilities.svi_prepare_vol_data import calculate_vol_BS
from calibration.SviCalibrationInput import SviInputSet
import Utilities.svi_calibration_utility as svi_util
import math
import pandas as pd
import matplotlib.pyplot as plt
from Utilities.utilities import *
import numpy as np
import datetime


evalDate = ql.Date(3, 8, 2017)
endDate = ql.Date(20, 8, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()

calibrered_params_ts = {}
while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    ql.Settings.instance().evaluationDate = evalDate
    try:
        curve = get_curve_treasury_bond(evalDate, daycounter)
        vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = get_wind_data(evalDate)
    except:
        continue
    yield_ts = ql.YieldTermStructureHandle(curve)
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))

    svi_dataset = SviInputSet(evalDate)
    for optionid in optionids:
        optionDataIdx = optionData[optionFlds.index('wind_code')].index(optionid)
        if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
            temp = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            mdate = datetime.date(temp.year,temp.month,temp.day)
            maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex = mktData[mktFlds.index('option_code')].index(optionid)
            strike = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close = mktData[mktFlds.index('close')][mktindex]
            open = mktData[mktFlds.index('open')][mktindex]
            ttm = daycounter.yearFraction(evalDate, maturitydt)
            rf = curve.zeroRate(maturitydt, daycounter, ql.Continuous).rate()
            Ft = spot * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            optiontype = ql.Option.Call
            implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                  close, evalDate, calendar, daycounter, precision = 0.05, maxVol = 0.5, step = 0.0001)
            totalvariance = (implied_vol**2)*ttm
            svi_dataset.update_data(mdate,strike,moneyness,implied_vol,ttm,totalvariance,close,open)

    calibrered_params = {}
    for mdate in svi_dataset.dataSet.keys():
        optimization_data = []
        data_mdate = svi_dataset.dataSet.get(mdate)
        logMoneynesses = data_mdate.moneyness
        totalvariance = data_mdate.totalvariance
        vol = data_mdate.volatility
        print('vols : ',vol)
        optimization_data.append(logMoneynesses)
        optimization_data.append(data_mdate.totalvariance)
        ttm = data_mdate.ttm
        params = svi_util.get_svi_optimal_params(optimization_data, ttm, 10)
        print('params : ',params)
        calibrered_params.update({mdate:params})
        a_star, b_star, rho_star, m_star, sigma_star = params
        x_svi = np.arange(min(logMoneynesses)-0.005, max(logMoneynesses)+0.02, 0.1/100)  # log_forward_moneyness
        tv_svi2 = np.multiply(
            a_star + b_star*(rho_star*(x_svi-m_star) + np.sqrt((x_svi - m_star)**2 + sigma_star**2)), ttm)
        vol_svi = np.sqrt(
            a_star + b_star*(rho_star*(x_svi-m_star) + np.sqrt((x_svi - m_star)**2 + sigma_star**2)))
        plt.figure()
        plt.plot(logMoneynesses, vol, 'ro')
        plt.plot(x_svi, vol_svi, 'b--')
        plt.title('vol, '+str(evalDate)+', '+str(mdate))
        plt.figure()
        plt.plot(logMoneynesses, totalvariance, 'ro')
        plt.plot(x_svi, tv_svi2, 'b--')
        plt.title('tv, '+str(evalDate)+', '+str(mdate))
        plt.show()
    print(calibrered_params)
    calibrered_params_ts.update({evalDate:calibrered_params})









