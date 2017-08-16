import svi_read_data as wind_data
from hedging_utility import get_spot_price,calculate_cash_position,calculate_hedging_error
from utilities import convert_datelist_from_datetime_to_ql as to_ql_dates
from utilities import convert_datelist_from_ql_to_datetime as to_dt_dates
from utilities import convert_date_from_ql_to_datetime as to_dt_date
from utilities import convert_date_from_datetime_to_ql as to_ql_date
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

start = timeit.default_timer()
np.random.seed()
w.start()

#begDate = ql.Date(1, 12, 2016)
begDate = ql.Date(1, 6, 2017)
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
    key_date = datetime.date(evalDate.year(), evalDate.month(), evalDate.dayOfMonth())
    maturity_dates = to_dt_dates(expiration_dates)
    svi_dataset =  cal_vols, put_vols, maturity_dates, spot, rf_months
    daily_svi_dataset.update({key_date:svi_dataset})
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
        params = svi_util.get_svi_optimal_params(data, ttm, 30)
        params_months.append(params)

    daily_params.update({key_date:params_months})
    dates.append(key_date)
    print('Finished : ',evalDate)
    print(params_months[0])
    print(params_months[1])
    print(params_months[2])
    print(params_months[3])

#print(daily_params)
timebreak1 = timeit.default_timer()
print('calibration time : ',timebreak1-start)
print('daily_params = ',daily_params)
print('daily_svi_dataset = ',daily_svi_dataset)
print('dates = ', dates)

with open(os.getcwd()+'/intermediate_data/hedging_daily_params_pcprates.pickle','wb') as f:
    pickle.dump([daily_params],f)
with open(os.getcwd()+'/intermediate_data/hedging_dates_pcprates.pickle','wb') as f:
    pickle.dump([dates],f)
with open(os.getcwd()+'/intermediate_data/hedging_daily_svi_dataset_pcprates.pickle','wb') as f:
    pickle.dump([daily_svi_dataset],f)
