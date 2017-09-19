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
'''
======================================
 SVI Hedge Performance (put options)
=======================================

Calculate SVI hedge errors for only put options. 
Currently persent in report.

'''

start = timeit.default_timer()
calendar = ql.China()
daycounter = ql.ActualActual()


with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_puts.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_dates_puts.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Hedge option using underlying 50ETF
daily_hedge_errors = {}
daily_pct_hedge_errors_td = {}
option_last_close_Ms = {}

for idx_date,date in enumerate(dates[0:len(dates)-2]):
    try:
        calibrate_date = to_ql_date(dates[idx_date])
        hedge_date = to_ql_date(dates[idx_date+1])
        liquidition_date = to_ql_date(dates[idx_date+2])

        # Liquidition Date Dataset
        dataset_on_liquidition_date = daily_svi_dataset.get(to_dt_date(liquidition_date))
        cal_vols, put_vols, maturity_dates, spot, rf_pcprs = dataset_on_liquidition_date

        # SELECT PUT OPTION DATA!!
        expiration_dates = to_ql_dates(maturity_dates)
        orgnized_data_liquidition_date = svi_util.orgnize_data_for_hedging(
            liquidition_date , daycounter, put_vols, expiration_dates, spot)
        optiontype = ql.Option.Put

        # Hedge Date Dataset
        dataset_on_hedge_date = daily_svi_dataset.get(to_dt_date(hedge_date))
        cal_vols_h, put_vols_h, maturity_dates_h, spot_on_hedge_date, rfs_on_hedge_date = dataset_on_hedge_date
        expiration_dates_h = to_ql_dates(maturity_dates_h)
        orgnized_data_hedge_date = svi_util.orgnize_data_for_hedging(
            hedge_date, daycounter, put_vols_h, expiration_dates_h, spot_on_hedge_date)

        calibrated_params = daily_params.get(to_dt_date(calibrate_date)) # on calibrate_date
        curve_on_hedge_date = svi_data.get_curve_treasury_bond(hedge_date,daycounter)
        # Local Vol Surface
        cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c  = daily_svi_dataset.get(to_dt_date(calibrate_date))
        black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params,to_ql_dates(maturity_dates_c),calibrate_date,daycounter,calendar,spot_c,rf_c)

        hedge_error_Ms,hedge_error_pct_Ms = hp_util.delta_hedge_svi(
            hedge_date,liquidition_date,daycounter,calendar,spot_c,spot_on_hedge_date,spot,black_var_surface,
            calibrated_params,orgnized_data_liquidition_date,orgnized_data_hedge_date,rfs_on_hedge_date,optiontype)
        key_date1 = datetime.date(liquidition_date.year(),liquidition_date.month(),liquidition_date.dayOfMonth())
        daily_hedge_errors.update({key_date1: hedge_error_Ms})
        daily_pct_hedge_errors_td.update({key_date1: hedge_error_pct_Ms})
    except Exception as e:
        print(e)
        continue

# Effective Delta
daily_hedge_errors = {}
daily_pct_hedge_errors_ed = {}
option_last_close_Ms = {}

for idx_date,date in enumerate(dates[0:len(dates)-2]):
    try:
        calibrate_date = to_ql_date(dates[idx_date])
        hedge_date = to_ql_date(dates[idx_date+1])
        liquidition_date = to_ql_date(dates[idx_date+2])

        # Liquidition Date Dataset
        dataset_on_liquidition_date = daily_svi_dataset.get(to_dt_date(liquidition_date))
        cal_vols, put_vols, maturity_dates, spot, rf_pcprs = dataset_on_liquidition_date

        # SELECT PUT OPTION DATA!!
        expiration_dates = to_ql_dates(maturity_dates)
        orgnized_data_liquidition_date = svi_util.orgnize_data_for_hedging(
            liquidition_date , daycounter, put_vols, expiration_dates, spot)
        optiontype = ql.Option.Put

        # Hedge Date Dataset
        dataset_on_hedge_date = daily_svi_dataset.get(to_dt_date(hedge_date))
        cal_vols_h, put_vols_h, maturity_dates_h, spot_on_hedge_date, rfs_on_hedge_date = dataset_on_hedge_date
        expiration_dates_h = to_ql_dates(maturity_dates_h)
        orgnized_data_hedge_date = svi_util.orgnize_data_for_hedging(
            hedge_date, daycounter, put_vols_h, expiration_dates_h, spot_on_hedge_date)

        calibrated_params = daily_params.get(to_dt_date(calibrate_date)) # on calibrate_date
        curve_on_hedge_date = svi_data.get_curve_treasury_bond(hedge_date,daycounter)
        # Local Vol Surface
        cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c  = daily_svi_dataset.get(to_dt_date(calibrate_date))
        black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params,to_ql_dates(maturity_dates_c),calibrate_date,daycounter,calendar,spot_c,rf_c)

        hedge_error_Ms,hedge_error_pct_Ms = hp_util.delta_hedge_svi_effdelta(
            hedge_date,liquidition_date,daycounter,calendar,spot_c,spot_on_hedge_date,spot,black_var_surface,
            calibrated_params,orgnized_data_liquidition_date,orgnized_data_hedge_date,rfs_on_hedge_date,optiontype)
        key_date1 = datetime.date(liquidition_date.year(),liquidition_date.month(),liquidition_date.dayOfMonth())
        daily_hedge_errors.update({key_date1: hedge_error_Ms})
        daily_pct_hedge_errors_ed.update({key_date1: hedge_error_pct_Ms})
    except Exception as e:
        print(e)
        continue


print("=" * 110)
print("SVI Model Average Hedging Percent Error, PUT (NO SMOOTHING) : ")
print("=" * 110)
print("%20s %15s %15s %25s %25s" % ("sample dates", "month", "moneyness", "total delta PnL(%)","eff delta PnL(%)"))
samples = ['2015.9-2016.1', '2016.2-2016.7', '2016.8-2017.1', '2017.2-2017.7']
p1_td = hedge_util.get_1st_percentile_dates(daily_pct_hedge_errors_td)
p2_td = hedge_util.get_2nd_percentile_dates(daily_pct_hedge_errors_td)
p3_td = hedge_util.get_3rd_percentile_dates(daily_pct_hedge_errors_td)
p4_td = hedge_util.get_4th_percentile_dates(daily_pct_hedge_errors_td)
container_td = [p1_td, p2_td, p3_td, p4_td]
p1_ed = hedge_util.get_1st_percentile_dates(daily_pct_hedge_errors_ed)
p2_ed = hedge_util.get_2nd_percentile_dates(daily_pct_hedge_errors_ed)
p3_ed = hedge_util.get_3rd_percentile_dates(daily_pct_hedge_errors_ed)
p4_ed = hedge_util.get_4th_percentile_dates(daily_pct_hedge_errors_ed)
container = [p1_ed, p2_ed, p3_ed, p4_ed]
results = {}
index = ["sample dates", "contract month", "moneyness", "total delta PnL(%)","eff delta PnL(%)"]
count = 0
for idx_c, r_ed in enumerate(container):
    r_td = container_td[idx_c]
    mny_td = hedge_util.hedging_performance_atm(r_td, r_td.keys())
    mny_ed = hedge_util.hedging_performance_atm(r_ed, r_ed.keys())
    print("-" * 110)
    for i in range(4):
        print("%20s %15s %15s %25s %25s" % (
            samples[idx_c], i, 'ATM', round(sum(mny_td.get(i)) / len(mny_td.get(i)), 4),
            round(sum(mny_ed.get(i)) / len(mny_ed.get(i)), 4)))
        results.update(
            {count: [samples[idx_c], i, ' ATM', round(sum(mny_td.get(i)) / len(mny_td.get(i)), 4),
                     round(sum(mny_ed.get(i)) / len(mny_ed.get(i)), 4)]})

        count += 1
    results.update({'total sample' + str(idx_c): ['Total Sample', len(r_td.keys()), 0, 0, 0]})
    #print('total date : ', len(r_ed.keys()))
print("=" * 110)

df = pd.DataFrame(data=results, index=index)
print(df)
df.to_csv('heging_svi_put_atm.csv')