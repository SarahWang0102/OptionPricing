from pricing_engines.SVI_optimization_NelderMead import SVI_NelderMeadOptimization
import matplotlib.pyplot as plt
import numpy as np
import datetime
import math

def svi_calibration_util(data,ttm,sim_no = 10):
    logMoneynesses = data[0]
    totalvariance = data[1]
    calibrated_params = []
    min_sse = 10
    for iter in range(sim_no):
        ms_0 = [0.1,0.1] # 参数初始值，可调
        adc_0 = [0.1,0.1,0.1] # 参数初始值，可调
        nm = SVI_NelderMeadOptimization(data,adc_0,ms_0,1e-7)
        calibrated_params, obj = nm.optimization()
        _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
        sse = 0.0
        for i, m in enumerate(logMoneynesses):
            tv = totalvariance[i]
            y_1 = np.divide((m - m_star), sigma_star)
            tv_1 = _a_star + _d_star * y_1 + _c_star * np.sqrt(y_1 ** 2 + 1)
            sse += (tv - tv_1) ** 2
        if sse >= min_sse: continue
        min_sse = sse
    _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
    a_star = np.divide(_a_star, ttm)
    b_star = np.divide(_c_star, (sigma_star * ttm))
    rho_star = np.divide(_d_star, _c_star)
    final_parames = [a_star, b_star, rho_star, m_star, sigma_star]
    return final_parames

# INPUTS:
today = datetime.date(2017,7,18)
maturity = datetime.date(2017,7,26)
spot = 2.659
rf = 0.028697999999993663
strikes = [2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6, 2.65, 2.7, 2.75]
# impliedVols是隐含波动率，基于收盘价从BS公式反推得到，与行权价相对应
impliedVols = [0.3777079181658674, 0.3426795072036777, 0.3012127199407369, 0.2621437573715114, 0.21103677883979366, 0.174068047851204, 0.1730795707320038, 0.1684228797713123, 0.18083357267167852, 0.21577383125687366]


totalvariances = []
logMoneynesses = []
ttm = (maturity-today).days/365
for idx,k in enumerate(strikes):
    Ft = spot * math.exp(rf * ttm)
    m = math.log(k / Ft, math.e) # forward log moneyness
    tv = (impliedVols[idx] ** 2) * ttm # total variance = (volatility^2)*ttm
    totalvariances.append(tv)
    logMoneynesses.append(m)

data = [logMoneynesses,totalvariances]
params = svi_calibration_util(data,ttm,10)
a_star, b_star, rho_star, m_star, sigma_star = params
x_svi = np.arange(min(logMoneynesses) - 0.005, max(logMoneynesses) + 0.02, 0.1 / 100)  # log_forward_moneyness
tv_svi2 = np.multiply(
    a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
plt.figure()
plt.plot(logMoneynesses, totalvariances, 'ro')
plt.plot(x_svi, tv_svi2, 'b--')
plt.show()

