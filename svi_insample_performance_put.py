import hedging_utility as hedge_util
from utilities import convert_datelist_from_datetime_to_ql as to_ql_dates
from utilities import convert_date_from_ql_to_datetime as to_dt_date
from utilities import convert_date_from_datetime_to_ql as to_ql_date
import svi_prepare_vol_data as svi_data
import svi_calibration_utility as svi_util
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
 SVI Insample Performance (put options)
=======================================

Calculate SVI insample percentage pricing errors for only put options. 
Currently persent in report.

'''
start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()

def Date(d,m,y):
    return ql.Date(d,m,y)


with open(os.getcwd()+'/intermediate_data/total_hedging_daily_params_puts.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/total_hedging_dates_puts.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Hedge option using underlying 50ETF
daily_pricing_errors = {}
option_last_close_Ms = {}

for idx_date,date in enumerate(dates[0:len(dates)-2]):
    try:
        print(idx_date)
        calibrate_date = to_ql_date(dates[idx_date])

        optiontype = ql.Option.Put

        calibrated_params = daily_params.get(to_dt_date(calibrate_date)) # on calibrate_date
        curve = svi_data.get_curve_treasury_bond(calibrate_date,daycounter)

        # Local Vol Surface
        cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c  = daily_svi_dataset.get(to_dt_date(calibrate_date))
        expiration_dates_h = to_ql_dates(maturity_dates_c)
        orgnized_data = svi_util.orgnize_data_for_hedging(
            calibrate_date, daycounter, put_vols_c, expiration_dates_h, spot_c)
        black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params,to_ql_dates(maturity_dates_c),calibrate_date,daycounter,calendar,spot_c,rf_c)
        pricing_error_Ms = {}
        for nbr_month in range(4):
            params_Mi = calibrated_params[nbr_month]
            moneyness, strikes, close_prices, expiration_date = orgnized_data.get(nbr_month)
            rf = curve.zeroRate(expiration_date, daycounter, ql.Continuous).rate()
            pricing_errors = []
            moneyness = []
            #print('liquidition date : ', calibrate_date, ',', nbr_month)
            for idx_k,k in enumerate(strikes):
                if k in close_prices.keys():
                    close_l = close_prices.get(k)
                else:
                    print('strike not found in L date')
                    continue
                close = close_prices.get(k)
                # No arbitrage condition
                ttm = daycounter.yearFraction(calibrate_date, expiration_date)
                if close < k*math.exp(-rf*ttm) - spot_c:
                    continue
                if close < 0.0001:
                   continue
                ttm = daycounter.yearFraction(calibrate_date,expiration_date)
                npv = hedge_util.calculate_NPV_sviVolSurface(black_var_surface, calibrate_date, daycounter, calendar, params_Mi,
                                                      spot_c, rf, k, expiration_date, optiontype)
                pct_error = (npv - close) /close
                if pct_error > 3:
                   print('error is large ')
                   continue
                pricing_error = round(pct_error, 4)
                pricing_errors.append(pricing_error)
                moneyness.append(round(spot_c/k,4))
            #print('moneyness : ',moneyness)
            #print('hedge errors pct : ', pricing_errors)
            pricing_error_Ms.update({nbr_month:[moneyness,pricing_errors]})
        if idx_date != 0:
            #print('liquidition date : ',liquidition_date)
            #print('hedge errors : ',hedge_error_Ms)
            key_date1 = datetime.date(calibrate_date.year(),calibrate_date.month(),calibrate_date.dayOfMonth())
            daily_pricing_errors.update({key_date1: pricing_error_Ms})
    except Exception as e:
        print(e)
        continue

stop = timeit.default_timer()
print('calibration time : ',stop-start)
with open(os.getcwd() + '/intermediate_data/pricing_errors_svi_put_no_smoothing.pickle', 'wb') as f:
    pickle.dump([daily_pricing_errors], f)

#p1 = get_1st_percentile_dates(daily_pricing_errors)
#p2 = get_2nd_percentile_dates(daily_pricing_errors)
#p3 = get_3rd_percentile_dates(daily_pricing_errors)
#p4 = get_4th_percentile_dates(daily_pricing_errors)
container = [daily_pricing_errors]
#samples = ['2015.9-2016.1', '2016.2-2016.7', '2016.8-2017.1', '2017.2-2017.7']
print("=" * 100)
print("SVI Model Average Pricing Percent Error,PUT (SVI VOL SURFACE 5-Day SMOOTHING) : ")
print("=" * 100)
print("%20s %20s %30s" % ("contract month", "moneyness", "avg pricing error(%)"))
for idx_c, r in enumerate(container):
    mny_0, mny_1, mny_2, mny_3 = hedge_util.hedging_performance(r, r.keys())
    print("-" * 100)
    for i in range(4):
        if len(mny_0.get(i)) > 0: print("%20s %20s %25s" % (
        i, ' < 0.97', round(sum(np.abs(mny_0.get(i))) * 100 / len(mny_0.get(i)), 4)))
        if len(mny_1.get(i)) > 0: print("%20s %20s %25s" % (
         i, ' 0.97 - 1.00', round(sum(np.abs(mny_1.get(i))) * 100 / len(mny_1.get(i)), 4)))
        if len(mny_2.get(i)) > 0: print("%20s %20s %25s" % (
        i, ' 1.00 - 1.03', round(sum(np.abs(mny_2.get(i))) * 100 / len(mny_2.get(i)), 4)))
        if len(mny_3.get(i)) > 0: print("%20s %20s %25s" % (
        i, ' > 1.03', round(sum(np.abs(mny_3.get(i))) * 100 / len(mny_3.get(i)), 4)))
        print("-" * 100)
    print('total date : ', len(r.keys()))

results = {}
index = ["contract month", "moneyness", "avg pricing error(%)"]
count = 0
for r in container:
    mny_0, mny_1, mny_2, mny_3 = hedge_util.hedging_performance(r, r.keys())
    print("-" * 100)
    for i in range(4):
        results.update({count: [ i, ' \'< 0.97', round(sum(np.abs(mny_0.get(i))) * 100 / len(mny_0.get(i)), 4)]})
        results.update({count + 1: [ i, ' \'0.97 - 1.00', round(sum(np.abs(mny_1.get(i))) * 100 / len(mny_1.get(i)), 4)]})
        results.update({count + 2: [ i, ' \'1.00 - 1.03', round(sum(np.abs(mny_2.get(i))) * 100 / len(mny_2.get(i)), 4)]})
        results.update({count + 3: [ i, ' \'> 1.03', round(sum(np.abs(mny_3.get(i))) * 100 / len(mny_3.get(i)), 4)]})
        count += 4
    results.update({'total sample': ['Total Sample', len(r.keys()), 0]})

df = pd.DataFrame(data=results,index=index)
print(df)
df.to_csv('svi pricing errors put no smoothing.csv')