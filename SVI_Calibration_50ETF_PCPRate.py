from WindPy import *
import matplotlib.pyplot as plt
from VolatilityData_readpkl import *
from SVI_Calibration_Util import *
import math
from SVI_NelderMeadOptimization_2 import SVI_NelderMeadOptimization

def get_data_from_BS_OTM_PCPRate(evalDate,daycounter,calendar,curve,show=True):

    cal_vols_data_moneyness, put_vols_data_monetness,expiration_dates,spot = get_call_put_impliedVols_moneyness_PCPrate(evalDate, curve,
                                                                                                  daycounter, calendar,
                                                                                                  maxVol=1.0,
                                                                                                  step=0.0001,
                                                                                                  precision=0.001,
                                                                                                  show=False)
    data_for_optimiztion_months = {}
    for idx_month, call_data in enumerate(cal_vols_data_moneyness):
        expiration_date = expiration_dates[idx_month]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        put_data = put_vols_data_monetness[idx_month]
        vols = []
        logMoneynesses = []
        total_variance = []
        for moneyness in call_data.keys():
            strike = call_data.get(moneyness)[0]
            #if strike >=spot: # K>Ft,OTM Call
            if moneyness >= 0:
                vol = call_data.get(moneyness)[0]
            else:
                vol = put_data.get(moneyness)[0]
            tv = (vol ** 2) * ttm
            total_variance.append(tv)
            vols.append(vol)
            logMoneynesses.append(moneyness)
        data = [logMoneynesses, total_variance,expiration_date]
        data_for_optimiztion_months.update({idx_month:data})
    return data_for_optimiztion_months

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
data_months = get_data_from_BS_OTM_PCPRate(evalDate,daycounter,calendar,curve,False)

i = 3
nbr_month = month_indexs[i]

#for i, nbr_month in enumerate(month_indexs):
data = data_months.get(i)

print('data_for_optimiztion : ', data)
logMoneynesses  = data[0]
totalvariance   = data[1]
expiration_date = data[2]
print('expiration date: ',expiration_date)
## NelderMeadOptimization
#nm   = SVI_NelderMeadOptimization(data, init_adc = [0.5,0.5,0.5], init_msigma = [1,1])
nm   = SVI_NelderMeadOptimization(data)
_a_star, _d_star, _c_star, m_star, sigma_star = nm.optimization()
x_svi  = np.arange(min(logMoneynesses)-0.05, max(logMoneynesses)+0.05, 0.1 / 100)  # log_forward_moneyness
y_svi  = np.divide((x_svi - m_star), sigma_star)
tv_svi = _a_star + _d_star * y_svi + _c_star * np.sqrt(y_svi**2 + 1)  # totalvariance objective fution values
print('_a_star, _d_star, _c_star, m_star, sigma_star',_a_star, _d_star, _c_star, m_star, sigma_star)
########################################################################################################################
## Get a,b,rho
ttm = daycounter.yearFraction(evalDate, expiration_date)
a_star = np.divide(_a_star, ttm)
b_star = np.divide(_c_star, (sigma_star * ttm))
rho_star = np.divide(_d_star, _c_star)
tv_svi2 = np.multiply(a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
print('a_star,b_star,rho_star, m_star, sigma_star : ',a_star,b_star,rho_star, m_star, sigma_star)
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
    ## Double check parameters calculation -- two lines should be exactly the same
    #plt.figure(11+i)
    #plt.plot(x_svi, tv_svi, 'b--')
    #plt.plot(x_svi, tv_svi2, 'r--')

    #plt.figure(10)
    #if i==0:
    #    plt.plot(log_fmoneyness, totalvariance, 'bo')
    #    l1,=plt.plot(x_svi, tv_svi, 'b--',label = 'T = ' + t)
    #    a1 = 'T = ' + t
    #elif i==1:
    #    plt.plot(log_fmoneyness, totalvariance, 'g*')
    #    l2,=plt.plot(x_svi, tv_svi, 'g-',label = 'T = ' + t)
    #    a2 = 'T = ' + t
    #elif i == 2:
    #    plt.plot(log_fmoneyness, totalvariance, 'y+')
    #    l3,=plt.plot(x_svi, tv_svi, 'y-.', label='T = ' + t)
    #    a3 = 'T = ' + t
    #elif i == 3:
    #    plt.plot(log_fmoneyness, totalvariance, 'ko')
    #    l4,=plt.plot(x_svi, tv_svi, 'k--', label='T = ' + t)
    #    a4 ='T = ' + t

#plt.title('SVI total variance for all maturities')

#plt.legend([l1,l2,l3,l4],[a1,a2,a3,a4])

plt.show()

w.stop()


########################################################################################################################
'''
def get_data_from_BS_OTM_old(nbr_month,curve,show=True):
    print('Call')
    vols_call,expiration_date,strikes_call,spot,close_call,logMoneyness_call = get_impliedvolmat_BS_oneMaturity(
        '认购',evalDate,daycounter,calendar,nbr_month,1.0,0.0001,0.001,show)
    print('Put')
    vols_put, expiration_date, strikes_put, spot,close_put,logMoneyness_put = get_impliedvolmat_BS_oneMaturity(
        '认沽',evalDate, daycounter, calendar, nbr_month,1.0,0.0001,0.001,show)
    ## Select OTM options from Calls and Puts
    vols           = []
    strikes        = []
    logMoneynesses = []
    closes         = []
    total_variance = []
    print("Select OTM:")
    print("=" * 110)
    print("%10s %10s %10s %25s %25s %20s" % ("Spot", "Strike", "close", "moneyness", "impliedVol", "Error (%)"))
    print("-" * 110)
    risk_free_rate = curve.zeroRate(expiration_date, daycounter, ql.Continuous).rate()
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    for idx_call , k in enumerate(strikes_call):
        idx_put = strikes_put.index(k)
        m       = logMoneyness_call[idx_call]
        #eqvlt_Ft = (close_call[idx_call] - close_put[idx_put])*math.exp()
        if m >= 0: # OTM call
            vol = vols_call[idx_call]
            cls = close_call[idx_call]
        else: # OTM put
            vol = vols_put[idx_put]
            cls = close_put[idx_put]
        tv = (vol ** 2) * ttm
        total_variance.append(tv)
        closes.append(cls)
        vols.append(vol)
        strikes.append(k)
        logMoneynesses.append(m)
        print("%10s %10s %10s %25s %25s %20s" % (spot, k, cls, m, vol, 0.0))
    data_for_optimiztion = [logMoneynesses, total_variance,expiration_date]

    print("-" * 110)
    return data_for_optimiztion
    #return vols,expiration_date,strikes,spot,risk_free_rate,closes,logMoneynesses
'''