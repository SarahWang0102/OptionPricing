import matplotlib.pyplot as plt
import svi_calibration_utility as svi_util
import svi_prepare_vol_data as svi_data
from svi_NelderMead_optimization import SVI_NelderMeadOptimization
import QuantLib as ql
from WindPy import w
import numpy as np
import math


# Evaluation Settings
np.random.seed()
w.start()
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(13, 7, 2017)
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
month_indexs = svi_data.get_contract_months(evalDate)
ql.Settings.instance().evaluationDate = evalDate
curve = svi_data.get_curve_treasury_bond(evalDate, daycounter)
cal_vols,put_vols,expiration_dates,spot,curve = svi_data.get_impliedvolmat_BS_put_cnvt(
        evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
data_months = svi_util.orgnize_data_for_optimization(
        evalDate,daycounter,cal_vols,put_vols,expiration_dates,spot)
print(curve)

# Calibrate SVI total variance curve
i = 0
nbr_month = month_indexs[i]
data = data_months.get(i)
logMoneynesses = data[0]
totalvariance = data[1]
expiration_date = data[2]
ttm = daycounter.yearFraction(evalDate, expiration_date)
final_parames = svi_util.get_svi_optimal_params(data,ttm,100)
print(final_parames)
a_star, b_star, rho_star, m_star, sigma_star = final_parames
x_svi = np.arange(min(logMoneynesses) - 0.05, max(logMoneynesses) + 0.05, 0.1 / 100)  # log_forward_moneyness
y_svi = np.divide((x_svi - m_star), sigma_star)

tv_svi2 = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)

plt.figure()
plt.plot(logMoneynesses, totalvariance, 'ro')
plt.plot(x_svi, tv_svi2, 'b--')
plt.ylim(min(totalvariance) - 0.0001, max(totalvariance) + 0.0001)
t = str(round(daycounter.yearFraction(evalDate, expiration_date), 4))
plt.title('SVI total variance, T = ' + t)

plt.show()
w.stop()
