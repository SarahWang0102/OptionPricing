from WindPy import *
import QuantLib as ql
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from VolatilityData import *
from scipy.optimize import root
from scipy.optimize import least_squares
from scipy.optimize import minimize, rosen, rosen_der
import math
from SVI_NelderMeadOptimization import SVI_NelderMeadOptimization
import datetime

# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(12,6,2017)
ql.Settings.instance().evaluationDate = evalDate


next_i_month = 0 # 0, 1, 3, 6
# Implied Volaility Matrix Data
w.start()
#data,expiration_dates,strikes,iv_matrix,spot  = get_impliedvolmat_call_BS(evalDate, daycounter,calendar)
#vols,expiration_dates,strikes,matrix,spot = get_impliedvolmat_call_wind(evalDate)

vols1,maturitydate,strikes1,spot1 = get_impliedvolmat_call_wind_oneMaturity(evalDate,next_i_month)
# Construct yield term structure
curve           =   get_curve_depo(evalDate,daycounter)
risk_free_rate  =   curve.zeroRate(maturitydate,daycounter,ql.Continuous).rate()
yield_ts        =   ql.YieldTermStructureHandle(curve)
dividend_ts     =   ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
flat_vol_ts     =   ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, 0.0, daycounter))
print('rate is : ', risk_free_rate)
vols,expiration_date,strikes,spot = get_impliedvolmat_call_BS_oneMaturity(evalDate,daycounter,calendar,next_i_month)
w.stop()

# x: log(K/Ft) log-forward moneyness
# v: implied molatilities
x = []
v = []
vol = []
ttm = daycounter.yearFraction(evalDate, expiration_date)
Ft = spot * math.exp(risk_free_rate * ttm)
for j, K in enumerate(strikes):
    total_implied_variance = (vols[j]**2)*ttm # w = ttm*vol^2
    log_moneyness = math.log(K/Ft,math.e)
    x.append(log_moneyness)
    v.append(total_implied_variance)
    vol.append(vols[j])
data = [x,v,vol,ttm,strikes,Ft]

#print(data)

# Nelder-Mead Optimization
print("data",data)
nm = SVI_NelderMeadOptimization(data)
_a_star, _d_star, _c_star,m_star,sigma_star = nm.optimization()
# SVI parameters: a, b, sigma, rho, m : _a = a*T; d = rho*b*sigma*T; c = b*sigma*T
a_star = np.divide(_a_star,ttm)
b_star = np.divide(_c_star/sigma_star,ttm)
rho_star = np.divide(_d_star/(b_star*sigma_star),ttm)


print('SVI parameters a,b,sigma,rho,m calibrated: ',a_star,b_star,sigma_star,rho_star,m_star)

x_svi = np.arange(-0.15,0.05,0.1/100)
v_svi = np.maximum(0,a_star + b_star*(rho_star*(x_svi - m_star) + np.sqrt((x_svi - m_star)**2 + sigma_star**2 )))
#v_svi = a_star + b_star*(rho_star*(x_svi - m_star) + np.sqrt((x_svi - m_star)**2 + sigma_star**2 ))
#print(v_svi)
vol_svi = np.sqrt(v_svi)
#print(vol_svi)
########################################################################################################################
# plot input data -- moneyness-imliedvol
plt.plot(x, vol, 'ro')

########################################################################################################################
# Plot SVI volatility smile -- moneyness-impliedVol
plt.plot(x_svi, vol_svi, 'b--')

plt.show()
