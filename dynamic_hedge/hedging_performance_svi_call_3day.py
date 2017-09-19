import Utilities.hedging_utility as hedge_util
from Utilities.utilities import *
import Utilities.svi_prepare_vol_data as svi_data
import Utilities.svi_calibration_utility as svi_util
import Utilities.hedging_performance_utility as hp_util
import QuantLib as ql
import pandas as pd
import math
import numpy as np
import datetime
import timeit
import os
import pickle

start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()

def Date(d,m,y):
    return ql.Date(d,m,y)

with open(os.path.abspath('..') +'/intermediate_data/total_hedging_daily_params_puts.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_dates_puts.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Hedge option using underlying 50ETF
daily_hedge_errors = {}
daily_pct_hedge_errors = {}
option_last_close_Ms = {}

for idx_date,date in enumerate(dates[0:len(dates)-10]):
    try:
        calibrate_date2 = to_ql_date(dates[idx_date])
        calibrate_date1 = to_ql_date(dates[idx_date+1])
        calibrate_date = to_ql_date(dates[idx_date+2])
        hedge_date = to_ql_date(dates[idx_date+3])
        liquidition_date = to_ql_date(dates[idx_date+4])

        # Liquidition Date Dataset
        dataset_on_liquidition_date = daily_svi_dataset.get(to_dt_date(liquidition_date))
        cal_vols, put_vols, maturity_dates, spot, rf_pcprs = dataset_on_liquidition_date

        # SELECT CALL OPTION DATA!!
        expiration_dates = to_ql_dates(maturity_dates)
        orgnized_data_liquidition_date = svi_util.orgnize_data_for_hedging(
            liquidition_date , daycounter, cal_vols, expiration_dates, spot)
        optiontype = ql.Option.Call

        # Hedge Date Data Set
        dataset_on_hedge_date = daily_svi_dataset.get(to_dt_date(hedge_date))
        cal_vols_h, put_vols_h, maturity_dates_h, spot_on_hedge_date, rfs_on_hedge_date = dataset_on_hedge_date
        expiration_dates_h = to_ql_dates(maturity_dates_h)
        orgnized_data_hedge_date = svi_util.orgnize_data_for_hedging(
            hedge_date, daycounter, cal_vols_h, expiration_dates_h, spot_on_hedge_date)

        calibrated_params = daily_params.get(to_dt_date(calibrate_date)) # on calibrate_date
        calibrated_params1 = daily_params.get(to_dt_date(calibrate_date1))  # on calibrate_date
        calibrated_params2 = daily_params.get(to_dt_date(calibrate_date2))  # on calibrate_date
        curve_on_hedge_date = svi_data.get_curve_treasury_bond(hedge_date,daycounter)

        # Local Vol Surface
        cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c  = daily_svi_dataset.get(to_dt_date(calibrate_date))

        calibrated_params_list=[calibrated_params,calibrated_params1,calibrated_params2]
        calibrate_dates = [calibrate_date,calibrate_date1,calibrate_date2]
        black_var_surface = hedge_util.get_local_volatility_surface_smoothed(calibrated_params_list,to_ql_dates(maturity_dates_c),
                                                                  calibrate_dates,daycounter,calendar,spot_c,rf_c)
        hedge_error_Ms,hedge_error_pct_Ms = hp_util.delta_hedge_svi(
            hedge_date,liquidition_date,daycounter,calendar,spot_c,spot_on_hedge_date,spot,black_var_surface,
            calibrated_params,orgnized_data_liquidition_date,orgnized_data_hedge_date,rfs_on_hedge_date,optiontype)
        key_date1 = datetime.date(liquidition_date.year(),liquidition_date.month(),liquidition_date.dayOfMonth())
        daily_hedge_errors.update({key_date1: hedge_error_Ms})
        daily_pct_hedge_errors.update({key_date1: hedge_error_pct_Ms})
    except Exception as e:
        print(e)
        continue

stop = timeit.default_timer()
print('calibration time : ',stop-start)

#print('daily_hedge_errors = ',daily_hedge_errors)
#print('daily_pct_hedge_errors = ',daily_pct_hedge_errors)
with open(os.path.abspath('..') +'/intermediate_data/hedging_daily_hedge_errors_svi_call.pickle','wb') as f:
    pickle.dump([daily_hedge_errors,daily_pct_hedge_errors],f)

print(daily_pct_hedge_errors.keys())
mny_0,mny_1,mny_2,mny_3 = hedge_util.hedging_performance(daily_pct_hedge_errors,daily_pct_hedge_errors.keys())
print("="*100)
print("SVI Model Average Hedging Percent Error,CALL (SVI VOL SURFACE 3-Day SMOOTHING) : ")
print("="*100)
print("%20s %20s %30s" % ("contract month","moneyness", "avg hedging error(%)"))
print("-"*100)
for i in range(4):
    if len(mny_0.get(i)) > 0: print("%20s %20s %25s" % (i,' < 0.97',round(sum(mny_0.get(i))*100/len(mny_0.get(i)),4)))
    if len(mny_1.get(i))>0: print("%20s %20s %25s" % (i,' 0.97 - 1.00', round(sum(mny_1.get(i))*100 / len(mny_1.get(i)),4)))
    if len(mny_2.get(i)) > 0: print("%20s %20s %25s" % (i,' 1.00 - 1.03', round(sum(mny_2.get(i))*100 / len(mny_2.get(i)),4)))
    if len(mny_3.get(i)) > 0: print("%20s %20s %25s" % (i,' > 1.03', round(sum(mny_3.get(i))*100 / len(mny_3.get(i)),4)))
    print("-" * 100)
print('total date : ', len(daily_pct_hedge_errors.keys()))
