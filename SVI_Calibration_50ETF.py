import matplotlib.pyplot as plt
from SVI_Calibration_Util import *


w.start()
# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(13,7,2017)
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
month_indexs = get_contract_months(evalDate)
ql.Settings.instance().evaluationDate = evalDate
# Calibrate SVI total variance curve
curve = get_curve_treasuryBond(evalDate, daycounter)
data_months,risk_free_rates = get_data_from_BS_OTM_PCPRate(evalDate,daycounter,calendar,curve,False)
print(risk_free_rates)

i = 3
# a_star,b_star,rho_star, m_star, sigma_star :  0.013133617016 0.177082095191 0.403855212213 0.00459161356109 0.0644783617415

nbr_month = month_indexs[i]

data = data_months.get(i)
print('evaluation date: ', evalDate)
print('data_for_optimiztion : ', data)
logMoneynesses  = data[0]
totalvariance   = data[1]
expiration_date = data[2]
print('expiration date: ',expiration_date)
## NelderMeadOptimization
min_obj  = 1.0
for iter in range(50):
    nm   = SVI_NelderMeadOptimization(data)
    calibrated_params, obj = nm.optimization()
    if obj >= min_obj : continue
    _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
    x_svi  = np.arange(min(logMoneynesses)-0.05, max(logMoneynesses)+0.05, 0.1 / 100)  # log_forward_moneyness
    y_svi  = np.divide((x_svi - m_star), sigma_star)
    tv_svi = _a_star + _d_star * y_svi + _c_star * np.sqrt(y_svi**2 + 1)  # totalvariance objective fution values
    #print('_a_star, _d_star, _c_star, m_star, sigma_star',_a_star, _d_star, _c_star, m_star, sigma_star)
    ## Get a,b,rho
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    a_star = np.divide(_a_star, ttm)
    b_star = np.divide(_c_star, (sigma_star * ttm))
    rho_star = np.divide(_d_star, _c_star)
    tv_svi2 = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
    print(iter,' : a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)
    parameters = [a_star,b_star,rho_star, m_star, sigma_star]

    # plot input data -- moneyness-totalvariance
    plt.figure(iter)
    plt.plot(logMoneynesses, totalvariance, 'ro')
    # Plot SVI volatility smile -- moneyness-totalvariance
    #plt.plot(x_svi, tv_svi, 'b--')
    plt.plot(x_svi, tv_svi2, 'b--')
    t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
    plt.title('SVI total variance, T = ' + t)

plt.show()


w.stop()
