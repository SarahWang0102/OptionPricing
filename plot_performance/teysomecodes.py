import Utilities.svi_read_data as wind_data
import matplotlib.pyplot as plt
from Utilities.utilities import *
import Utilities.svi_prepare_vol_data as svi_data
import Utilities.svi_calibration_utility as svi_util
import numpy as np
from WindPy import w
import datetime
import pickle
import os


with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_params_calls_noZeroVol.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_dates_calls_noZeroVol.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_svi_dataset_calls_noZeroVol.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

cal_vols_c, put_vols_c, maturity_dates_c, underlying_prices, rf_c = daily_svi_dataset.get(datetime.date(2017,3,31))
print(spot_c)
# 1,5,9主力合约
core_maturities = ['01','05','09']


daycounter = ql.ActualActual()


paramset_core = {}
for date in daily_svi_dataset.keys():
    temp = {}
    evalDate = ql.Date(date.day, date.month, date.year)
    dataset = daily_svi_dataset.get(date)
    paramset = daily_params.get(date)
    for contractId in paramset.keys():
        print(contractId[-2:])
        if contractId[-2:] in core_maturities:
            temp.update({contractId:paramset.get(contractId)})
    paramset_core.update({evalDate:temp})
print(paramset_core)
'''
    cal_vols, put_vols, maturity_dates, spot, rfs = dataset
    maturity_dates = to_ql_dates(maturity_dates)
    data_months = svi_util.orgnize_data_for_optimization_cmd(
        evalDate, daycounter, put_vols, maturity_dates)

    print(data_months.keys())
    # mdate = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(4, ql.Days))
'''