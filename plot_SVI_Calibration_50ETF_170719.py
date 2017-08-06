import matplotlib.pyplot as plt
import svi_calibration_utility as svi_util
import svi_prepare_vol_data as svi_data
import QuantLib as ql
import numpy as np
from WindPy import w
import plot_util as pu

w.start()
# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(18,7,2017)
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
print(evalDate)
month_indexs = svi_data.get_contract_months(evalDate)
ql.Settings.instance().evaluationDate = evalDate
# Calibrate SVI total variance curve
curve = svi_data.get_curve_treasury_bond(evalDate, daycounter)
data_months,risk_free_rates = svi_util.get_data_from_BS_OTM_PCPRate(evalDate,daycounter,calendar,curve,False)
#print(risk_free_rates)
mark = "o"
line = pu.l3
for i in range(4):
    if i == 0:
        a_star, b_star, rho_star, m_star, sigma_star = 0.00392946245464, 0.932829724957, -0.674532827132, -0.0446916864921, 0.0326894289419
    elif i == 1:
        a_star, b_star, rho_star, m_star, sigma_star = 0.0202858609804,0.907688022355,0.867498561699,0.0238060958095,0.0180937230185
    elif i == 2:
        a_star, b_star, rho_star, m_star, sigma_star = 0.0105133312325, 0.274698338398, 0.292223667381, -0.000540665540219, 0.0776321826581
    else:
        a_star, b_star, rho_star, m_star, sigma_star = 0.0252339030552, 3.67875932103, 0.982658824086, 0.0210387531491, 0.0050963364926

    data = data_months.get(i)
    print('evaluation date: ', evalDate)
    logMoneynesses  = data[0]
    totalvariance   = data[1]
    expiration_date = data[2]

    print('expiration date: ',expiration_date)
    x_svi  = np.arange(min(logMoneynesses)-0.02, max(logMoneynesses)+0.002, 0.1 / 100)  # log_forward_moneyness
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    tv_svi = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
    print(iter,' : a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)
    v_svi = np.sqrt(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))

    # plot input data -- moneyness-totalvariance
    plt.figure()
    plt.scatter(logMoneynesses, totalvariance, marker = mark,color = pu.c2)
    plt.plot(x_svi, tv_svi,color = pu.c1,linestyle = line,linewidth = 2,label="SVI Implied Total Variance")
    scale1 = (max(totalvariance) - min(totalvariance)) / 10
    plt.ylim(min(totalvariance) - scale1 / 2, max(totalvariance) + scale1)
    t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
    plt.title('SVI total variance, T = ' + t)
    plt.figure()
    plt.plot(x_svi, v_svi,color = pu.c1,linestyle = line,linewidth = 2,label="SVI Implied Volatility")
    scale2 = (max(v_svi) - min(v_svi)) / 10
    plt.ylim(min(v_svi) - scale2 / 2, max(v_svi) + scale2)
    t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
    plt.title('SVI implied volatility, T = ' + t)
plt.show()


