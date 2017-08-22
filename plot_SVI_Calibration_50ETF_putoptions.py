import matplotlib.pyplot as plt
import svi_calibration_utility as svi_util
import svi_prepare_vol_data as svi_data
import QuantLib as ql
import numpy as np
from WindPy import w
import plot_util as pu
import operator

def get_params(nbr_month):
    if nbr_month == 0:
        a_star, b_star, rho_star, m_star, sigma_star = 5.21428571606e-09, 0.975142793726, -0.715028457626, -0.051413796808, 0.0428595816562
        print(nbr_month,' : ',round(a_star,4), round(b_star,4), round(rho_star,4), round(m_star,4), round(sigma_star,4))
    elif nbr_month == 1:
        a_star, b_star, rho_star, m_star, sigma_star = 0.0119830022033, 0.209345779712, -0.239545892797, -0.0556912261369, 0.100862655414
        print(nbr_month, ' : ', round(a_star, 4), round(b_star, 4), round(rho_star, 4), round(m_star, 4),
              round(sigma_star, 4))
    elif nbr_month == 2:
        a_star, b_star, rho_star, m_star, sigma_star = 0.0223722222376, 0.244873156344, -0.81660991058, -0.165172508096, 0.103769251863
        print(nbr_month, ' : ', round(a_star, 4), round(b_star, 4), round(rho_star, 4), round(m_star, 4),
              round(sigma_star, 4))
    else:
        a_star, b_star, rho_star, m_star, sigma_star = 2.26708074534e-10, 0.171441311541, -0.577775453729, -0.234550672991, 0.2710537735
        print(nbr_month, ' : ', round(a_star, 4), round(b_star, 4), round(rho_star, 4), round(m_star, 4),
              round(sigma_star, 4))
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
#data_months,risk_free_rates = svi_util.get_data_from_BS_OTM_PCPRate(evalDate,daycounter,calendar,curve,False)
cal_vols,put_vols,expiration_dates,spot,r = svi_data.get_call_put_impliedVols_tbcurve(
        evalDate,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.05,show=True)
data_months = svi_util.orgnize_data_for_optimization_put(
        evalDate,daycounter,cal_vols,put_vols,expiration_dates,spot)
#print(risk_free_rates)
mark = "o"
line = pu.l3
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})

for i in range(4):
    a_star, b_star, rho_star, m_star, sigma_star = get_params(i)
    data = data_months.get(i)
    print('evaluation date: ', evalDate)
    logMoneynesses  = data[0]
    totalvariance   = data[1]
    expiration_date = data[2]
    impliedvol = data[3]

    print('expiration date: ',expiration_date)
    x_svi  = np.arange(min(logMoneynesses)-0.025, max(logMoneynesses)+0.005, 0.1 / 100)  # log_forward_moneyness
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
    '''
    f2, ax2 = plt.subplots()
    plt.scatter(logMoneynesses, impliedvol, marker=mark, color=pu.c2)
    plt.plot(x_svi, v_svi,color = pu.c1,linestyle = line,linewidth = 2,label="SVI Implied Volatility")
    scale2 = (max(impliedvol) - min(impliedvol))/13
    plt.ylim(min(impliedvol)-scale2,max(impliedvol)+scale2)
    title2 = 'SVI Implied Volatility, T = ' + t +' ,'+ str(evalDate)
    #plt.title(title2)
    '''
    # Hide the right and top spines
    #ax2.spines['right'].set_visible(False)
    #ax2.spines['top'].set_visible(False)
    ax1.spines['right'].set_visible(False)
    ax1.spines['top'].set_visible(False)
    # Only show ticks on the left and bottom spines
    #ax2.yaxis.set_ticks_position('left')
    #ax2.xaxis.set_ticks_position('bottom')
    ax1.yaxis.set_ticks_position('left')
    ax1.xaxis.set_ticks_position('bottom')

    f1.savefig(title1 + '.png', dpi=500, format='png')
    #f2.savefig('St'+title2 + '.png', dpi=300, format='png')

f, axarr = plt.subplots()

for j in range(4):
    a_star, b_star, rho_star, m_star, sigma_star = get_params(j)
    data = data_months.get(j)
    print('evaluation date: ', evalDate)
    logMoneynesses  = data[0]
    totalvariance   = data[1]
    expiration_date = data[2]
    impliedvol = data[3]
    print(expiration_date)

    if j == 3:
        x_svi = np.arange(-0.2, 0.025, 0.1 / 100)  # log_forward_moneyness
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        tv_svi = np.multiply(
            a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
        v_svi = np.sqrt(
            a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))
        t = str(round(daycounter.yearFraction(evalDate, expiration_date), 4))
        l1, = axarr.plot(x_svi, v_svi,color = pu.c1,linestyle = pu.l1,linewidth = 2)
        label1 = 'SVI方差，T = ' + t
    elif j == 2:
        x_svi = np.arange(-0.2, 0.05, 0.1 / 100)  # log_forward_moneyness
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        tv_svi = np.multiply(
            a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
        v_svi = np.sqrt(
            a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))
        t = str(round(daycounter.yearFraction(evalDate, expiration_date), 4))
        l2, = axarr.plot(x_svi, v_svi, color=pu.c2, linestyle=pu.l2, linewidth=2)
        label2 = 'SVI方差，T = ' + t
    elif j == 1:
        x_svi = np.arange(-0.2, 0.06, 0.1 / 100)  # log_forward_moneyness
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        tv_svi = np.multiply(
            a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
        v_svi = np.sqrt(
            a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))
        t = str(round(daycounter.yearFraction(evalDate, expiration_date), 4))
        l3, = axarr.plot(x_svi, v_svi, color=pu.c3, linestyle=pu.l3, linewidth=2)
        label3 = 'SVI方差，T = ' + t

    else:
        x_svi = np.arange(-0.2, 0.06, 0.1 / 100)  # log_forward_moneyness
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        tv_svi = np.multiply(
            a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
        v_svi = np.sqrt(
            a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))
        l4, = axarr.plot(x_svi, v_svi, color=pu.c4, linestyle=pu.l4, linewidth=2)
        t = str(round(daycounter.yearFraction(evalDate, expiration_date), 4))
        l4.set_dashes(pu.dash)
        label4 = 'SVI方差，T = ' + t

axarr.legend([l1,l2,l3,l4],[label1,label2,label3,label4],bbox_to_anchor=(0., 1.02, 1.1, .102), loc=3,
           ncol=2, borderaxespad=0.,columnspacing=1.5,frameon=False)
axarr.spines['right'].set_visible(False)
axarr.spines['top'].set_visible(False)
axarr.yaxis.set_ticks_position('left')
axarr.xaxis.set_ticks_position('bottom')
#f.savefig('SVI total variances no arbitrage, '+ str(evalDate) +'.png', dpi=300, format='png')


idx_month = 2
data = data_months.get(idx_month)
print('evaluation date: ', evalDate)
logMoneynesses = data[0]
totalvariance = data[1]
tv_dic = {}
for idx, m in enumerate(logMoneynesses):
    tv = totalvariance[idx]
    tv_dic.update({m:tv})
tv_sorted = sorted(tv_dic.items(), key=operator.itemgetter(0))
tv_sorted_dic = dict(tv_sorted)

totalvariance_sorted = []
logMoneynesses_sorted = []

for key_m in tv_sorted_dic.keys():
    logMoneynesses_sorted.append(key_m)
    totalvariance_sorted.append(tv_sorted_dic.get(key_m))
ff, ax = plt.subplots()
ax.plot(logMoneynesses_sorted, totalvariance_sorted, color = pu.c1,marker = "^",linestyle = pu.l1,linewidth = 2,label="认沽期权隐含方差")
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xlabel('Forward log-moneyness')
ax.legend()

ff.savefig('total variance put ,'+ str(evalDate) +'.png', dpi=300, format='png')
plt.show()


