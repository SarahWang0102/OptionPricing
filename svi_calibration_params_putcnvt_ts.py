import matplotlib.pyplot as plt
import svi_calibration_util as svi_util
import svi_prepare_vol_data as svi_data
from svi_NelderMead_optimization import  SVI_NelderMeadOptimization
import QuantLib as ql
import numpy as np
from WindPy import w


#w.start()
# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(12,6,2017)

month_indexs = svi_data.get_contract_months(evalDate)

# Calibrate SVI total variance curve
nbr_month = month_indexs[1] # Next Month Contarct
endDate = ql.Date(12,7,2017)
i = 0
print("=" * 150)
print("%20s %20s %20s %20s %20s %20s " % ("evalDate","a", "b", "rho", "m", "sigma"))
print("-" * 150)
figShow =  True
show = False
while evalDate < endDate:
    ql.Settings.instance().evaluationDate = evalDate
    try:
        curve = svi_data.get_curve_treasury_bond(evalDate, daycounter)
        #data = get_data_from_BS_put_cnvt(nbr_month,curve,True)
        data = svi_util.get_data_from_BS_put_cnvt(evalDate,daycounter,calendar,nbr_month, curve, show)
    except RuntimeError:
        print(evalDate,' get data failed')
        continue
    #data = get_data_from_BS_put('认沽',nbr_month, curve, True)
    if show : print('data_for_optimiztion : ', data)
    logMoneynesses  = data[0]
    totalvariance   = data[1]
    expiration_date = data[2]
    if show: print('expiration date: ',expiration_date)
    ## NelderMeadOptimization
    nm   = SVI_NelderMeadOptimization(data)
    calibrated_params, obj = nm.optimization()
    _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
    x_svi  = np.arange(min(logMoneynesses)-0.05, max(logMoneynesses)+0.05, 0.1 / 100)  # log_forward_moneyness
    y_svi  = np.divide((x_svi - m_star), sigma_star)
    tv_svi = _a_star + _d_star * y_svi + _c_star * np.sqrt(y_svi**2 + 1)  # totalvariance objective fution values
    if show: print('_a_star, _d_star, _c_star, m_star, sigma_star',_a_star, _d_star, _c_star, m_star, sigma_star)
    ########################################################################################################################
    ## Get a,b,rho
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    a_star = np.divide(_a_star, ttm)
    b_star = np.divide(_c_star, (sigma_star * ttm))
    rho_star = np.divide(_d_star, _c_star)
    tv_svi2 = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
    print("%20s %20s %20s %20s %20s %20s " % (evalDate,a_star,b_star,rho_star, m_star, sigma_star))
    ########################################################################################################################
    if figShow:
        ########################################################################################################################
        # plot input data -- moneyness-totalvariance
        plt.figure(i)
        plt.plot(logMoneynesses, totalvariance, 'ro')

        ########################################################################################################################
        # Plot SVI volatility smile -- moneyness-totalvariance
        plt.plot(x_svi, tv_svi, 'b--')
        t = str( daycounter.yearFraction(evalDate,expiration_date))
        plt.title('SVI total variance, T = ' + t)
    ########################################################################################################################
    i += 1
    evalDate = calendar.advance(evalDate, ql.Period(1,ql.Days))
print("-" * 150)
if figShow: plt.show()

w.stop()


########################################################################################################################
