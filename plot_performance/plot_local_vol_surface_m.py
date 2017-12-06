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


with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_params_puts_noZeroVol.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_dates_puts_noZeroVol.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_svi_dataset_puts_noZeroVol.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]


# 1,5,9主力合约
core_maturities = ['01','05','09']
#paramset_core = {}
calibrated_params = {}
dataset = daily_svi_dataset.get(to_dt_date(date))
paramset = daily_params.get(to_dt_date(date))
for contractId in paramset.keys():
    if contractId[-2:] in core_maturities:
        calibrated_params.update({contractId:paramset.get(contractId)})

print('calibrated_params')
print(calibrated_params)

strikes = np.arange(2400.0, 3200.0, 1.0)
#strikes = np.arange(1.0, 5.0, 0.1 / 100)
# Local Vol Surface
cal_vols, put_vols, maturitydates, underlying_prices, rfs = daily_svi_dataset.get(to_dt_date(date))
black_var_surface = localVol.get_black_variance_surface_cmd(calibrated_params, date, daycounter, calendar, underlying_prices,'m',strikes)
curve = get_curve_treasury_bond(date,daycounter)
yield_ts = get_yield_ts(date,curve,to_ql_date(max(maturitydates)),daycounter)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(date, 0.0, daycounter))
local_vol_surface = ql.LocalVolSurface(ql.BlackVolTermStructureHandle(black_var_surface),yield_ts,dividend_ts,underlying_prices.get('1801'))

print(black_var_surface.maxStrike())
# Plot
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
plot_years = np.arange(0.1, black_var_surface.maxTime(), 0.05)
plot_strikes = np.arange(2400.0, 3200.0, 10.0)

fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
'''
Z = np.array([local_vol_surface.localVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))
'''
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
print(put_vols)
black_var_surface = localVol.get_black_variance_surface_cmd(calibrated_params, date, daycounter,
                                                            calendar, underlying_prices,'m',strikes)
curve = get_curve_treasury_bond(date,daycounter)
yield_ts = get_yield_ts(date,curve,to_ql_date(max(maturitydates)),daycounter)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(date, 0.0, daycounter))
local_vol_surface = ql.LocalVolSurface(ql.BlackVolTermStructureHandle(black_var_surface),yield_ts,dividend_ts,underlying_prices.get('1801'))

# Plot
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
plot_years = np.arange(0.1, black_var_surface.maxTime(), 0.05)
#plot_strikes = np.arange(2500.0, 3000.0, 1.0)

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





fig.savefig('svi_implied_vol_surface_m1, put，'+ str(date) +'.png', dpi=300, format='png')
fig1.savefig('svi_implied_vol_surface_m2, put，'+ str(date) +'.png', dpi=300, format='png')
plt.show()