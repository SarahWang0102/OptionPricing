from Utilities.svi_read_data import get_commodity_sr_data
from Utilities.svi_prepare_vol_data import calculate_vol_BS
from calibration.SviCalibrationInput import SviInputSet
import Utilities.svi_calibration_utility as svi_util
import math
import pandas as pd
import matplotlib.pyplot as plt
from Utilities.utilities import *
import numpy as np
import datetime
from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

evalDate = ql.Date(2, 8, 2017)
#endDate = ql.Date(20, 8, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()

core_contracts = ['801','805']


calibrered_params_ts = {}
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
ql.Settings.instance().evaluationDate = evalDate
print(evalDate)

curve = get_curve_treasury_bond(evalDate, daycounter)
results_call, results_put, underlying_prices = get_commodity_sr_data(evalDate, calendar)

yield_ts = ql.YieldTermStructureHandle(curve)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))

svi_data = SviInputSet(to_dt_date(evalDate))
min_k = 10000
max_k = 0
##################################
optionType = '认沽'
optiontype = ql.Option.Put
dataset = results_put
##################################
for maturitydt in dataset.keys():
    mktdata = dataset.get(maturitydt)
    contractid = mktdata[0][-1]
    if contractid[-3:] not in core_contracts:
        continue
    spot = underlying_prices.get(contractid)
    mdate = datetime.date(maturitydt.year(), maturitydt.month(), maturitydt.dayOfMonth())
    for data in mktdata:
        strike = data[0]
        close = data[1]
        volum = data[2]  # 万元
        if volum == 0.0: continue
        open_price = ''
        Ft = spot
        moneyness = math.log(strike / Ft, math.e)
        exercise = ql.EuropeanExercise(maturitydt)
        payoff = ql.PlainVanillaPayoff(optiontype, strike)
        option = ql.EuropeanOption(payoff, exercise)
        flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(evalDate, calendar, 0.0, daycounter))
        process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,
                                               flat_vol_ts)
        option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
        # error = 0.0
        try:
            implied_vol = option.impliedVolatility(close, process, 1.0e-4, 300, 0.0, 4.0)
        except RuntimeError:
            continue
        ttm = daycounter.yearFraction(evalDate, maturitydt)
        totalvariance = (implied_vol ** 2) * ttm
        min_k = min(min_k,strike)
        max_k = max(max_k,strike)
        svi_data.update_data(mdate, strike, moneyness, implied_vol, ttm, totalvariance, close, open_price, spot, volum)

calibrered_params = {}
underlyings = {}
for mdate in svi_data.dataSet.keys():
    optimization_data = []
    data_mdate = svi_data.dataSet.get(mdate)
    underlyings.update({mdate:data_mdate.spot})
    logMoneynesses = data_mdate.moneyness
    totalvariance = data_mdate.totalvariance
    vol = data_mdate.volatility
    #print('vols : ', vol)
    optimization_data.append(logMoneynesses)
    optimization_data.append(data_mdate.totalvariance)
    ttm = data_mdate.ttm
    params = svi_util.get_svi_optimal_params(optimization_data, ttm, 10)
    #print('params : ', params)
    calibrered_params.update({mdate: params})
    a_star, b_star, rho_star, m_star, sigma_star = params
    x_svi = np.arange(min(logMoneynesses) - 0.005, max(logMoneynesses) + 0.02, 0.1 / 100)  # log_forward_moneyness
    tv_svi2 = np.multiply(
        a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
    vol_svi = np.sqrt(
        a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))

    #plt.figure()
    #plt.plot(logMoneynesses, vol, 'ro')
    #plt.plot(x_svi, vol_svi, 'b--')
    #plt.title('vol, ' + str(evalDate) + ', ' + str(mdate))
    plt.figure()
    plt.plot(logMoneynesses, totalvariance, 'ro')
    plt.plot(x_svi, tv_svi2, 'b--')
    plt.title('tv, ' + str(evalDate) + ', ' + str(mdate))
    plt.show()

#print(calibrered_params)
maturity_dates = sorted(calibrered_params.keys())
#print(maturity_dates)
calibrered_params_ts.update({evalDate: calibrered_params})
volSurface = SviVolSurface(evalDate, calibrered_params, daycounter, calendar)
svi = SviPricingModel(volSurface, underlyings, daycounter, calendar,
                            to_ql_dates(maturity_dates), ql.Option.Put, 'sr')
black_var_surface = svi.black_var_surface()
#local_vol_surface = ql.LocalVolSurface(ql.BlackVolTermStructureHandle(black_var_surface),
#                                       yield_ts,dividend_ts,spot)
dt = black_var_surface.maxDate()
t = daycounter.yearFraction(evalDate,dt)
# Plot
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
plot_years = np.arange(0.05, t-0.05, 0.01)
plot_strikes = np.arange(float(min_k), float(max_k), 1.0)

fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)

Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))
print(Z)
print(Z[np.argmin(Z[:,1]),0])
surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.1,vmin = 0.15,vmax = 0.3)
ax.set_xlabel('K')
ax.set_ylabel('T')
fig.colorbar(surf, shrink=0.5, aspect=5)

print(evalDate)
fig.savefig('svi_implied_vol_surface_sr, ' + optionType + ' ' + str(evalDate) +'.png', dpi=300, format='png')
plt.show()
