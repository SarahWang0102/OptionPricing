import matplotlib.pyplot as plt
from VolatilityData_Copied import *
from SVI_CalibrationFun import *
import math
from SVI_NelderMeadOptimization import SVI_NelderMeadOptimization
import datetime
#month_indexs = [1,3,6] # 0,1,3,6
month_indexs = [0,1,3,6]
w.start()

# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(12,6,2017)
ql.Settings.instance().evaluationDate = evalDate

def get_data_from_wind(next_i_month):
    vols, expiration_date, strikes, spot = get_impliedvolmat_call_wind_oneMaturity(evalDate,next_i_month)
    curve           =   get_curve_depo(evalDate,daycounter)
    risk_free_rate  =   curve.zeroRate(expiration_date,daycounter,ql.Continuous).rate()
    return vols, expiration_date, strikes, spot, risk_free_rate

def get_data_from_BS(next_i_month):
    vols1,maturitydate,strikes1,spot1 = get_impliedvolmat_call_wind_oneMaturity(evalDate,next_i_month)
    # Construct yield term structure
    curve           =   get_curve_depo(evalDate,daycounter)
    risk_free_rate  =   curve.zeroRate(maturitydate,daycounter,ql.Continuous).rate()

    vols,expiration_date,strikes,spot = get_impliedvolmat_call_BS_oneMaturity(evalDate,daycounter,calendar,next_i_month)
    return vols,expiration_date,strikes,spot,risk_free_rate


for i, next_i_month in enumerate([0]):
    print('rate is : ', )
    vols, expiration_date, strikes, spot, risk_free_rate = get_data_from_BS(next_i_month)
    init_adc = [0.1,0.1,0.1]
    if next_i_month == 0:
        init_adc = [0.01,0.01,0.01]
    elif next_i_month == 1:
        init_adc = [0.02, 0.02, 0.02]
    elif next_i_month == 2:
        init_adc = [0.5, 0.5, 0.5]
    #x, vol, x_svi, vol_svi = svi_calibration(evalDate,init_adc,calendar,daycounter,risk_free_rate,vols,expiration_date,strikes,spot)
    log_fmoneyness, totalvariance, volatility, _a_star, _d_star, _c_star, m_star, sigma_star = svi_calibration3('nm',evalDate,init_adc,calendar,daycounter,risk_free_rate,vols,expiration_date,strikes,spot)
    x_svi  = np.arange(min(log_fmoneyness), max(log_fmoneyness), 0.1 / 100)  # log_forward_moneyness
    y_svi  = np.divide((x_svi - m_star), sigma_star)
    tv_svi = _a_star + _d_star * y_svi + _c_star * np.sqrt(y_svi ** 2 + 1)  # totalvariance objective fution values
    ########################################################################################################################
    # plot input data -- moneyness-totalvariance
    plt.figure(i)
    plt.plot(log_fmoneyness, totalvariance, 'ro')

    ########################################################################################################################
    # Plot SVI volatility smile -- moneyness-totalvariance
    plt.plot(x_svi, tv_svi, 'b--')
    t = str( daycounter.yearFraction(evalDate,expiration_date))
    plt.title('SVI total variance, T = ' + t)

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

