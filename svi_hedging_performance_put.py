import svi_read_data as wind_data
from hedging_utility import get_spot_price, get_1st_percentile_dates, get_2nd_percentile_dates, \
    get_3rd_percentile_dates, get_4th_percentile_dates, hedging_performance, calculate_cash_position, \
    calculate_delta_sviVolSurface, get_local_volatility_surface_smoothed, get_local_volatility_surface, \
    calculate_delta_svi, calculate_hedging_error
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
daily_hedge_errors = {}
daily_pct_hedge_errors = {}
option_last_close_Ms = {}

for idx_date,date in enumerate(dates[0:len(dates)-2]):
    try:
        print(idx_date)
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
        cal_vols_h, put_vols_h, maturity_dates_h, spot_on_hedge_date, pcprs_on_hedge_date = dataset_on_hedge_date
        expiration_dates_h = to_ql_dates(maturity_dates_h)
        orgnized_data_hedge_date = svi_util.orgnize_data_for_hedging(
            hedge_date, daycounter, put_vols_h, expiration_dates_h, spot_on_hedge_date)

        calibrated_params = daily_params.get(to_dt_date(calibrate_date)) # on calibrate_date
        curve_on_hedge_date = svi_data.get_curve_treasury_bond(hedge_date,daycounter)
        # Local Vol Surface
        cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c  = daily_svi_dataset.get(to_dt_date(calibrate_date))
        black_var_surface = get_local_volatility_surface(calibrated_params,to_ql_dates(maturity_dates_c),calibrate_date,daycounter,calendar,spot_c,rf_c)
        hedge_error_Ms = {}
        hedge_error_pct_Ms = {}
        for nbr_month in range(4):
            params_Mi = calibrated_params[nbr_month]
            rf_on_hedge_date = pcprs_on_hedge_date.get(nbr_month)
            moneyness_l, strikes_l, close_prices_l, expiration_date_l = orgnized_data_liquidition_date.get(nbr_month)
            moneyness_h, strikes_h, close_prices_h, expiration_date_h = orgnized_data_hedge_date.get(nbr_month)
            evalDate = calendar.advance(liquidition_date, ql.Period(5, ql.Days))
            if expiration_date_l <= evalDate: continue
            rf = curve_on_hedge_date.zeroRate(liquidition_date, daycounter, ql.Continuous).rate()
            hedge_errors = []
            hedge_errors_pct = []
            moneyness = []
            print('liquidition date : ', liquidition_date, ',', nbr_month)
            for idx_k,k in enumerate(strikes_h):
                if k in close_prices_l.keys():
                    close_l = close_prices_l.get(k)
                else:
                    print('strike not found in L date')
                    continue
                close_h = close_prices_h.get(k)
                # No arbitrage condition
                ttm = daycounter.yearFraction(hedge_date,expiration_date_h)
                if close_h < k*math.exp(-rf_on_hedge_date*ttm) - spot_on_hedge_date:
                    continue
                if close_h < 0.0001:
                   continue
                delta = calculate_delta_sviVolSurface(black_var_surface, hedge_date, daycounter, calendar, params_Mi,
                                                      spot_c, rf, k, expiration_date_h, optiontype)
                cash_on_hedge_date = calculate_cash_position(hedge_date, close_h, spot_on_hedge_date, delta)
                hedge_error = calculate_hedging_error(hedge_date,liquidition_date,daycounter,spot,close_l,delta,cash_on_hedge_date,rf)
                hedge_error_pct = hedge_error/close_h
                if abs(hedge_error_pct) > 3 :
                    print(date,',',nbr_month,',',k,'too large error', hedge_error_pct)
                    continue
                hedge_error = round(hedge_error,4)
                hedge_error_pct = round(hedge_error_pct, 4)
                hedge_errors.append(hedge_error)
                hedge_errors_pct.append(hedge_error_pct)
                moneyness.append(round(spot_on_hedge_date/k,4))
            print('moneyness : ',moneyness)
            print('hedge errors pct : ', hedge_errors_pct)
            hedge_error_Ms.update({nbr_month:[moneyness,hedge_errors]})
            hedge_error_pct_Ms.update({nbr_month:[moneyness,hedge_errors_pct]})
        if idx_date != 0:
            #print('liquidition date : ',liquidition_date)
            #print('hedge errors : ',hedge_error_Ms)
            key_date1 = datetime.date(liquidition_date.year(),liquidition_date.month(),liquidition_date.dayOfMonth())
            daily_hedge_errors.update({key_date1: hedge_error_Ms})
            daily_pct_hedge_errors.update({key_date1: hedge_error_pct_Ms})
    except Exception as e:
        print(e)
        continue

stop = timeit.default_timer()
print('calibration time : ',stop-start)
with open(os.getcwd() + '/intermediate_data/hedging_daily_hedge_errors_svi_put_no_smoothing.pickle', 'wb') as f:
    pickle.dump([daily_hedge_errors, daily_pct_hedge_errors], f)

p1 = get_1st_percentile_dates(daily_pct_hedge_errors)
p2 = get_2nd_percentile_dates(daily_pct_hedge_errors)
p3 = get_3rd_percentile_dates(daily_pct_hedge_errors)
p4 = get_4th_percentile_dates(daily_pct_hedge_errors)
container = [p1, p2, p3, p4]
samples = ['2015.9-2016.1', '2016.2-2016.7', '2016.8-2017.1', '2017.2-2017.7']
print("=" * 100)
print("SVI Model Average Hedging Percent Error,PUT (SVI VOL SURFACE 5-Day SMOOTHING) : ")
print("=" * 100)
print("%20s %20s %20s %30s" % ("sample dates", "contract month", "moneyness", "avg hedging error(%)"))
for idx_c, r in enumerate(container):
    mny_0, mny_1, mny_2, mny_3 = hedging_performance(r, r.keys())
    print("-" * 100)
    for i in range(4):
        if len(mny_0.get(i)) > 0: print("%20s %20s %20s %25s" % (
        samples[idx_c], i, ' < 0.97', round(sum(np.abs(mny_0.get(i))) * 100 / len(mny_0.get(i)), 4)))
        if len(mny_1.get(i)) > 0: print("%20s %20s %20s %25s" % (
        samples[idx_c], i, ' 0.97 - 1.00', round(sum(np.abs(mny_1.get(i))) * 100 / len(mny_1.get(i)), 4)))
        if len(mny_2.get(i)) > 0: print("%20s %20s %20s %25s" % (
        samples[idx_c], i, ' 1.00 - 1.03', round(sum(np.abs(mny_2.get(i))) * 100 / len(mny_2.get(i)), 4)))
        if len(mny_3.get(i)) > 0: print("%20s %20s %20s %25s" % (
        samples[idx_c], i, ' > 1.03', round(sum(np.abs(mny_3.get(i))) * 100 / len(mny_3.get(i)), 4)))
        print("-" * 100)
    print('total date : ', len(r.keys()))

results = {}
index = ["sample dates", "contract month", "moneyness", "avg hedging error(%)"]
count = 0
for idx_c, r in enumerate(container):
    mny_0, mny_1, mny_2, mny_3 = hedging_performance(r, r.keys())
    print("-" * 100)
    for i in range(4):
        results.update(
            {count: [samples[idx_c], i, ' \'< 0.97', round(sum(np.abs(mny_0.get(i))) * 100 / len(mny_0.get(i)), 4)]})

        results.update({count + 1: [samples[idx_c], i, ' \'0.97 - 1.00',
                                    round(sum(np.abs(mny_1.get(i))) * 100 / len(mny_1.get(i)), 4)]})
        results.update({count + 2: [samples[idx_c], i, ' \'1.00 - 1.03',
                                    round(sum(np.abs(mny_2.get(i))) * 100 / len(mny_2.get(i)), 4)]})
        results.update({count + 3: [samples[idx_c], i, ' \'> 1.03',
                                    round(sum(np.abs(mny_3.get(i))) * 100 / len(mny_3.get(i)), 4)]})
        count += 4
    results.update({'total sample' + str(idx_c): ['Total Sample', len(r.keys()), 0, 0]})

df = pd.DataFrame(data=results, index=index)
print(df)
df.to_csv('svi hedge put no smoothing.csv')