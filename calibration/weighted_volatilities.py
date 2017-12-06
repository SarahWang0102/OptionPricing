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



evalDate = ql.Date(1, 6, 2016)
endDate = ql.Date(1, 4, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()

calibrered_params_ts = {}
svi_dataset_ts = []
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
            amount = mktData[mktFlds.index('amount')][mktindex]
            ttm = daycounter.yearFraction(evalDate, maturitydt)
            try:
                rf = curve.zeroRate(maturitydt, daycounter, ql.Continuous).rate()
            except:
                rf = 0.0
            Ft = spot * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            optiontype = ql.Option.Call
            implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                  close, evalDate, calendar, daycounter, precision = 0.05, maxVol = 0.5, step = 0.0001)
            totalvariance = (implied_vol**2)*ttm
            svi_dataset.update_data(mdate,strike,moneyness,implied_vol,ttm,totalvariance,close,open,amount)
    svi_dataset_ts.append(svi_dataset)
print(svi_dataset_ts)



