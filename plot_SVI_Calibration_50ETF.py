import matplotlib.pyplot as plt
from SVI_Calibration_Util import *
import plot_util as pu

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
#print(risk_free_rates)

i = 1
a_star,b_star,rho_star, m_star, sigma_star =  0.0027154378929, 0.1201944098, -0.141331089153, 0.01945999699, 0.194002279093
data = data_months.get(i)
print('evaluation date: ', evalDate)
logMoneynesses  = data[0]
totalvariance   = data[1]
expiration_date = data[2]
print('expiration date: ',expiration_date)

x_svi  = np.arange(min(logMoneynesses)-0.02, max(logMoneynesses)+0.05, 0.1 / 100)  # log_forward_moneyness

ttm = daycounter.yearFraction(evalDate, expiration_date)

tv_svi = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
print(iter,' : a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)

# plot input data -- moneyness-totalvariance
plt.figure(i)
plt.scatter(logMoneynesses, totalvariance, marker = "o",color = pu.c1)
plt.plot(x_svi, tv_svi,color = pu.c2,linestyle = pu.l1,linewidth = 2,label="SVI Implied Volatility")
plt.ylim(min(totalvariance)-0.0001,max(totalvariance)+0.0005)
t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
plt.title('SVI total variance, T = ' + t)

i = 2
a_star,b_star,rho_star, m_star, sigma_star =  0.00167809322339, 0.536900997282, 0.733311043179, 0.071223058622, 0.0618405058673

data = data_months.get(i)
#print('evaluation date: ', evalDate)
logMoneynesses  = data[0]
totalvariance   = data[1]
expiration_date = data[2]
print('expiration date: ',expiration_date)

x_svi  = np.arange(min(logMoneynesses)-0.05, max(logMoneynesses)+0.05, 0.1 / 100)  # log_forward_moneyness

ttm = daycounter.yearFraction(evalDate, expiration_date)

tv_svi = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
print(iter,' : a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)

# plot input data -- moneyness-totalvariance
plt.figure(i)
plt.scatter(logMoneynesses, totalvariance, marker = "o",color = pu.c1)
plt.plot(x_svi, tv_svi,color = pu.c2,linestyle = pu.l1,linewidth = 2,label="SVI Implied Volatility")
plt.ylim(min(totalvariance)-0.001,max(totalvariance)+0.002)
t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
plt.title('SVI total variance, T = ' + t)

i = 3
#a_star,b_star,rho_star, m_star, sigma_star =  0.013133617016, 0.177082095191, 0.403855212213, 0.00459161356109, 0.0644783617415
a_star,b_star,rho_star, m_star, sigma_star =  0.0107047521466, 0.297485230118, 0.647754886901, 0.0262354285707, 0.0554674716145
data = data_months.get(i)
print('evaluation date: ', evalDate)
logMoneynesses  = data[0]
totalvariance   = data[1]
expiration_date = data[2]
print('expiration date: ',expiration_date)

x_svi  = np.arange(min(logMoneynesses)-0.05, max(logMoneynesses)+0.01, 0.1 / 100)  # log_forward_moneyness

ttm = daycounter.yearFraction(evalDate, expiration_date)

tv_svi = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
print(iter,' : a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)

# plot input data -- moneyness-totalvariance
plt.figure(i)
plt.scatter(logMoneynesses, totalvariance, marker = "o",color = pu.c1)
plt.plot(x_svi, tv_svi,color = pu.c2,linestyle = pu.l1,linewidth = 2,label="SVI Implied Volatility")
plt.ylim(min(totalvariance)-0.001,max(totalvariance)+0.005)
t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
plt.title('SVI total variance, T = ' + t)

plt.show()


