from svi_model import local_vol_surface_util as localVol
from Utilities.utilities import *
import Utilities.svi_prepare_vol_data as svi_data
import QuantLib as ql
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import math
import numpy as np
import datetime
import timeit
import os
import pickle

start = timeit.default_timer()

date = ql.Date(17,7,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
date = calendar.advance(date,ql.Period(1,ql.Days))


with open(os.path.abspath('..')+'/intermediate_data/sr_hedging_daily_params_calls_noZeroVol.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/sr_hedging_dates_calls_noZeroVol.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/sr_hedging_daily_svi_dataset_puts_noZeroVol.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]


# 1,5,9主力合约
core_maturities = ['709','801','805']
strikes = np.arange(5500.0, 7400.0, 1.0)
#paramset_core = {}
calibrated_params = {}
dataset = daily_svi_dataset.get(to_dt_date(date))
paramset = daily_params.get(to_dt_date(date))
for contractId in paramset.keys():
    if contractId[-3:] in core_maturities:
        calibrated_params.update({contractId:paramset.get(contractId)})

# Local Vol Surface
cal_vols, put_vols, maturitydates, underlying_prices, rfs = daily_svi_dataset.get(to_dt_date(date))
black_var_surface = localVol.get_black_variance_surface_cmd(calibrated_params, date, daycounter, calendar, underlying_prices,'sr',strikes)
curve = get_curve_treasury_bond(date,daycounter)
yield_ts = get_yield_ts(date,curve,to_ql_date(max(maturitydates)),daycounter)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(date, 0.0, daycounter))

# Plot
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
plot_years = np.arange(0.1, black_var_surface.maxTime(), 0.05)
plot_strikes = np.arange(5500.0, 7400.0, 1)

fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)

Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))
#print(Z)
#print(Z[np.argmin(Z[:,1]),0])
surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.1,vmin = 0.1,vmax = 0.3)
ax.set_xlabel('K')
ax.set_ylabel('T')
fig.colorbar(surf, shrink=0.5, aspect=5)

#### Include all cotracts
calibrated_params = paramset
# Local Vol Surface
cal_vols, put_vols, maturitydates, underlying_prices, rfs = daily_svi_dataset.get(to_dt_date(date))
black_var_surface = localVol.get_black_variance_surface_cmd(calibrated_params, date, daycounter, calendar, underlying_prices,'sr',strikes)
curve = get_curve_treasury_bond(date,daycounter)

# Plot
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
plot_years = np.arange(0.1, black_var_surface.maxTime(), 0.05)

fig1= plt.figure()
ax1 = fig1.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))
print(Z[np.argmin(Z[:,1]),0])
surf = ax1.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.1,vmin = 0.1,vmax = 0.3)
ax1.set_xlabel('K')
ax1.set_ylabel('T')
fig1.colorbar(surf, shrink=0.5, aspect=5)





fig.savefig('svi_implied_vol_surface_sr1, call，'+ str(date) +'.png', dpi=300, format='png')
fig1.savefig('svi_implied_vol_surface_sr2, call，'+ str(date) +'.png', dpi=300, format='png')
plt.show()