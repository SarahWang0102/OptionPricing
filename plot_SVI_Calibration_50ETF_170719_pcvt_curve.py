import matplotlib.pyplot as plt
import svi_calibration_utility as svi_util
import svi_prepare_vol_data as svi_data
import QuantLib as ql
import numpy as np
from WindPy import w
import plot_util as pu

def get_params(nbr_month):
    if nbr_month == 0:
        a_star, b_star, rho_star, m_star, sigma_star = 0.0112064856489, 1.05386614737, -0.765168670221, -0.0501975625884, 0.0269781341942
    elif nbr_month == 1:
        a_star, b_star, rho_star, m_star, sigma_star = 1.04285714286e-09, 0.716639782872, 0.733796955397, 0.0503438625508, 0.0661889047085
    elif nbr_month == 2:
        a_star, b_star, rho_star, m_star, sigma_star = 0.00512237429886, 0.444383653941, -0.832445439484, -0.216783427583, 0.13043505387
    else:
        a_star, b_star, rho_star, m_star, sigma_star = 2.26708076008e-10, 0.432100648749, -0.877406860606, -0.370367656316, 0.183792253408
    return a_star, b_star, rho_star, m_star, sigma_star

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
cal_vols,put_vols,expiration_dates,spot,curve = svi_data.get_impliedvolmat_BS_put_cnvt(
        evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
data_months = svi_util.orgnize_data_for_optimization_put(
        evalDate,daycounter,cal_vols,put_vols,expiration_dates,spot)
mark = "o"
line = pu.l3


for i in range(4):
    a_star, b_star, rho_star, m_star, sigma_star = get_params(i)
    data = data_months.get(i)
    print('evaluation date: ', evalDate)
    logMoneynesses  = data[0]
    totalvariance   = data[1]
    expiration_date = data[2]
    impliedvol = data[3]

    print('expiration date: ',expiration_date)
    x_svi  = np.arange(min(logMoneynesses)-0.02, max(logMoneynesses)+0.01, 0.1 / 100)  # log_forward_moneyness
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    tv_svi = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
    print(iter,' : a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)
    v_svi = np.sqrt(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))

    # plot input data -- moneyness-totalvariance
    #f1 = plt.figure()
    f1, ax1 = plt.subplots()
    plt.scatter(logMoneynesses, totalvariance, marker = mark,color = pu.c2)
    plt.plot(x_svi, tv_svi,color = pu.c1,linestyle = line,linewidth = 2,label="SVI Implied Total Variance")
    scale1 = (max(totalvariance) - min(totalvariance))/13
    plt.ylim(min(totalvariance)-scale1,max(totalvariance)+scale1)
    t = str( round( daycounter.yearFraction(evalDate,expiration_date),4))
    title1 = 'SVI Total Variance, T = ' + t + ' ,' + str(evalDate)
    #plt.title(title1)

    f2, ax2 = plt.subplots()
    plt.scatter(logMoneynesses, impliedvol, marker=mark, color=pu.c2)
    plt.plot(x_svi, v_svi,color = pu.c1,linestyle = line,linewidth = 2,label="SVI Implied Volatility")
    scale2 = (max(impliedvol) - min(impliedvol))/13
    plt.ylim(min(impliedvol)-scale2,max(impliedvol)+scale2)
    title2 = 'SVI Implied Volatility, T = ' + t +' ,'+ str(evalDate)
    #plt.title(title2)
    # Hide the right and top spines
    ax2.spines['right'].set_visible(False)
    ax2.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    # Only show ticks on the left and bottom spines
    ax2.yaxis.set_ticks_position('left')
    ax2.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    ax1.xaxis.set_ticks_position('bottom')

    f1.savefig(title1 + '.png', dpi=300, format='png')
    f2.savefig(title2 + '.png', dpi=300, format='png')

f, axarr = plt.subplots()
for j in range(4):
    a_star, b_star, rho_star, m_star, sigma_star = get_params(j)
    data = data_months.get(j)
    print('evaluation date: ', evalDate)
    logMoneynesses  = data[0]
    totalvariance   = data[1]
    expiration_date = data[2]
    impliedvol = data[3]

    print('expiration date: ',expiration_date)
    x_svi  = np.arange(-0.3, 0.1, 0.1 / 100)  # log_forward_moneyness
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    tv_svi = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
    print(iter,' : a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)
    v_svi = np.sqrt(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))
    t = str(round(daycounter.yearFraction(evalDate, expiration_date), 4))
    if j == 3:
        l1, = axarr.plot(x_svi, tv_svi,color = pu.c1,linestyle = pu.l1,linewidth = 2)
        label1 = 'T = ' + t
    elif j == 2:
        l2, = axarr.plot(x_svi, tv_svi, color=pu.c2, linestyle=pu.l2, linewidth=2)
        label2 = 'T = ' + t
    elif j == 1:
        l3, = axarr.plot(x_svi, tv_svi, color=pu.c3, linestyle=pu.l3, linewidth=2)
        label3 = 'T = ' + t
    else:
        l4, = axarr.plot(x_svi, tv_svi, color=pu.c4, linestyle=pu.l4, linewidth=2)
        l4.set_dashes(pu.dash)
        label4 = 'T = ' + t
axarr.legend([l1,l2,l3,l4],[label1,label2,label3,label4])
f.savefig('total_variances '+ str(evalDate) +'.png', dpi=300, format='png')
plt.show()


