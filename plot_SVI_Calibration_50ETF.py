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
evalDate = ql.Date(13,7,2017)
evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
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
        a_star,b_star,rho_star, m_star, sigma_star =  -0.442190449383, 1.88495933915, 0.0113239298356, 0.0102760514872, 0.246395133895
        d = 0.0002
    elif i == 1:
        #a_star,b_star,rho_star, m_star, sigma_star =  0.0208375208515, 0.0461228448035, -0.0299637399006, 0.0778418089194, 0.103363008259
        a_star, b_star, rho_star, m_star, sigma_star = 0.0252928022052, 0.0564924387201, 0.319285421937, 0.0348294627737, 0.0168594330178
        d = 0.0001
    elif i == 2:
        #a_star, b_star, rho_star, m_star, sigma_star = 0.00167809322339, 0.536900997282, 0.733311043179, 0.071223058622, 0.0618405058673
        a_star, b_star, rho_star, m_star, sigma_star = -0.221627005691, 0.797019693474, 0.55538381427, 0.256240601654, 0.371972840536
        d = 0.001
    else:
        # a_star,b_star,rho_star, m_star, sigma_star =  0.013133617016, 0.177082095191, 0.403855212213, 0.00459161356109, 0.0644783617415
        # a_star,b_star,rho_star, m_star, sigma_star =  0.0107047521466, 0.297485230118, 0.647754886901, 0.0262354285707, 0.0554674716145
        a_star, b_star, rho_star, m_star, sigma_star = 2.1987951839e-10, 0.368896397562, 0.742325933862, 0.102341857317, 0.100541406157
        d = 0.001

    data = data_months.get(i)
    print('evaluation date: ', evalDate)
    logMoneynesses  = data[0]
    totalvariance   = data[1]
    expiration_date = data[2]

    print('expiration date: ',expiration_date)
    x_svi  = np.arange(min(logMoneynesses)-0.02, max(logMoneynesses)+0.02, 0.1 / 100)  # log_forward_moneyness
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    tv_svi = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
    print(iter,' : a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)
    v_svi = np.sqrt(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))

    # plot input data -- moneyness-totalvariance
    plt.figure()
    plt.scatter(logMoneynesses, totalvariance, marker = mark,color = pu.c2)
    plt.plot(x_svi, tv_svi,color = pu.c1,linestyle = line,linewidth = 2,label="SVI Implied Total Variance")
    plt.ylim(min(tv_svi)-d,max(tv_svi)+d)
    t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
    plt.title('SVI total variance, T = ' + t)
    plt.figure()
    plt.plot(x_svi, v_svi,color = pu.c1,linestyle = line,linewidth = 2,label="SVI Implied Volatility")
    t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
    plt.title('SVI implied volatility, T = ' + t)
plt.show()


