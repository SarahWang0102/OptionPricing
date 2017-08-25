import matplotlib.pyplot as plt
import svi_calibration_utility as svi_util
import svi_prepare_vol_data as svi_data
from svi_NelderMead_optimization import SVI_NelderMeadOptimization
import QuantLib as ql
from WindPy import w
import numpy as np
import math


'''
===========================
 SVI Params Optimization
===========================

Run n times Nelder-Mead optimization with random initials.
Use PUT CALL PARITY ADJUSTED RATES.
Plot each optimization result.

'''

def run_optimization(data,ttm,sim_no = 100):
    logMoneynesses = data[0]
    totalvariance = data[1]
    min_sse = 10
    calibrated_params = []
    ms_rnd = np.random.random([sim_no, 2])*5
    adc_rnd = np.random.random([sim_no, 3])*5
    for iter in range(sim_no):
        ms_0 = ms_rnd[iter,:]
        #adc_0 = adc_rnd[iter,:]*np.array([max(data[1]), 4*ms_0.item(1), 4*ms_0.item(1)])
        adc_0 = adc_rnd[iter, :]
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
        print(iter,' : a_star, b_star, rho_star, m_star, sigma_star = ',a_star,',', b_star,',', rho_star,',', m_star,',', sigma_star)
        x_svi = np.arange(min(logMoneynesses) - 0.005, max(logMoneynesses) + 0.02, 0.1 / 100)  # log_forward_moneyness
        tv_svi2 = np.multiply(
                a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
        plt.figure(iter)
        plt.plot(logMoneynesses, totalvariance, 'ro')
        plt.plot(x_svi, tv_svi2, 'b--')
        scale1 = (max(totalvariance) - min(totalvariance)) / 10
        plt.ylim(min(totalvariance) - scale1 / 2, max(totalvariance) + scale1)
        t = str(round(daycounter.yearFraction(evalDate, expiration_date), 4))
        plt.title('SVI total variance, T = ' + t)
    _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
    a_star = np.divide(_a_star, ttm)
    b_star = np.divide(_c_star, (sigma_star * ttm))
    rho_star = np.divide(_d_star, _c_star)
    final_parames = [a_star, b_star, rho_star, m_star, sigma_star]

    return final_parames

# Evaluation Settings
np.random.seed()
#w.start()
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(18, 7, 2017)
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
month_indexs = svi_data.get_contract_months(evalDate)
ql.Settings.instance().evaluationDate = evalDate
curve = svi_data.get_curve_treasury_bond(evalDate, daycounter)
cal_vols,put_vols,expiration_dates,spot,risk_free_rates = svi_data.get_call_put_impliedVols_moneyness_PCPrate_pcvt(
        evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
data_months = svi_util.orgnize_data_for_optimization(
        evalDate,daycounter,cal_vols,put_vols,expiration_dates,spot)
print(evalDate)
# Calibrate SVI total variance curve
i = 1
nbr_month = month_indexs[i]
data = data_months.get(i)
logMoneynesses = data[0]
totalvariance = data[1]
expiration_date = data[2]
ttm = daycounter.yearFraction(evalDate, expiration_date)
final_parames = run_optimization(data,ttm,50)
plt.show()
