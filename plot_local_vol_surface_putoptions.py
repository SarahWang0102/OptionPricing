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
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
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


def Date(d, m, y):
    return ql.Date(d, m, y)


with open(os.getcwd() + '/intermediate_data/total_hedging_daily_params_puts.pickle', 'rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.getcwd() + '/intermediate_data/total_hedging_dates_puts.pickle', 'rb') as f:
    dates = pickle.load(f)[0]
with open(os.getcwd() + '/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle', 'rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Hedge option using underlying 50ETF
daily_hedge_errors = {}
daily_pct_hedge_errors = {}
option_last_close_Ms = {}

#date = datetime.date(2017,6,12)
date = datetime.date(2017,7,19)
idx_date = dates.index(date)
calibrate_date4 = to_ql_date(dates[idx_date-4])
calibrate_date3 = to_ql_date(dates[idx_date -3])
calibrate_date2 = to_ql_date(dates[idx_date -2])
calibrate_date1 = to_ql_date(dates[idx_date -1])
calibrate_date = to_ql_date(dates[idx_date])


calibrated_params = daily_params.get(to_dt_date(calibrate_date))  # on calibrate_date
calibrated_params1 = daily_params.get(to_dt_date(calibrate_date1))  # on calibrate_date
calibrated_params2 = daily_params.get(to_dt_date(calibrate_date2))  # on calibrate_date
calibrated_params3 = daily_params.get(to_dt_date(calibrate_date3))  # on calibrate_date
calibrated_params4 = daily_params.get(to_dt_date(calibrate_date4))  # on calibrate_date
curve_on_calibrate_date = svi_data.get_curve_treasury_bond(calibrate_date, daycounter)
# Local Vol Surface
cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c = daily_svi_dataset.get(to_dt_date(calibrate_date))
# black_var_surface = get_local_volatility_surface(calibrated_params,to_ql_dates(maturity_dates_c),calibrate_date,daycounter,calendar,spot_c,rf_c)
calibrated_params_list = [calibrated_params, calibrated_params1, calibrated_params2, calibrated_params3,
                          calibrated_params4]
calibrate_dates = [calibrate_date, calibrate_date1, calibrate_date2, calibrate_date3, calibrate_date4]
black_var_surface_smoothed = get_local_volatility_surface_smoothed(calibrated_params_list, to_ql_dates(maturity_dates_c),
                                                          calibrate_dates, daycounter, calendar, spot_c, rf_c)
black_var_surface = get_local_volatility_surface(calibrated_params, to_ql_dates(maturity_dates_c),
                                                          calibrate_date, daycounter, calendar, spot_c, rf_c)

yield_ts = ql.YieldTermStructureHandle(curve_on_calibrate_date)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(calibrate_date, 0.0, daycounter))
local_vol_surface = ql.LocalVolSurface(ql.BlackVolTermStructureHandle(black_var_surface),yield_ts,dividend_ts,spot_c)

# Plot
plot_years = np.arange(0.05, 0.44, 0.05)
plot_strikes = np.arange(2.1, 2.6, 0.03)
fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([local_vol_surface.localVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))
print(Z[np.argmin(Z[:,1]),0])
surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.1)
fig.colorbar(surf, shrink=0.5, aspect=5)

plt.show()