import matplotlib.pyplot as plt
from VolatilityData import *
from SVI_CalibrationFun import *
import math
from SVI_NelderMeadOptimization import SVI_NelderMeadOptimization


def get_data_from_wind(next_i_month,curve):
    vols, expiration_date, strikes, spot = get_impliedvolmat_wind_oneMaturity('认购',evalDate,next_i_month)
    risk_free_rate  =   curve.zeroRate(expiration_date,daycounter,ql.Continuous).rate()
    return vols, expiration_date, strikes, spot, risk_free_rate

def get_data_from_BS_OTM(nbr_month,curve,show=True):

    call_volatilities, put_converted_volatilites, strikes_call, strikes_put, \
    close_call, close_put, logMoneyness_call, logMoneyness_put, expiration_date, spot = \
        get_impliedvolmat_BS_OTM_oneMaturity(
            evalDate,curve, daycounter, calendar, nbr_month,1.0, 0.0001, 0.001, True)
    vols           = []
    strikes        = []
    logMoneynesses = []
    closes         = []
    total_variance = []
    print("CALL:")
    print("=" * 110)
    print("%10s %10s %10s %25s %25s" % ("Spot", "Strike", "close", "moneyness", "impliedVol"))
    print("-" * 110)
    for i, v in enumerate(call_volatilities):
        print("%10s %10s %10s %25s %25s %20s" %
              (spot, strikes_call[i], close_call[i], logMoneyness_call[i], call_volatilities[i], 0.0))
    print("-" * 110)
    print("PUT (cnvt) :")
    print("=" * 110)
    print("%10s %10s %10s %25s %25s" % ("Spot", "Strike", "close", "moneyness", "impliedVol"))
    print("-" * 110)
    for i, v in enumerate(put_converted_volatilites):
        print("%10s %10s %10s %25s %25s " %
              (spot, strikes_put[i], close_put[i], logMoneyness_put[i], put_converted_volatilites[i]))
    print("-" * 110)
    print("SELECTED OTM:")
    print("=" * 110)
    print("%10s %10s %10s %25s %25s " % ("Spot", "Strike", "close", "moneyness", "impliedVol"))
    print("-" * 110)
    risk_free_rate = curve.zeroRate(expiration_date, daycounter, ql.Continuous).rate()
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    for idx_call , k in enumerate(strikes_call):
        idx_put = strikes_put.index(k)
        m       = logMoneyness_call[idx_call]
        #eqvlt_Ft = (close_call[idx_call] - close_put[idx_put])*math.exp()
        if k >= spot: # OTM call
            vol = call_volatilities[idx_call]
            cls = close_call[idx_call]
        else: # OTM put
            vol = put_converted_volatilites[idx_put]
            cls = close_put[idx_put]
        tv = (vol ** 2) * ttm
        total_variance.append(tv)
        closes.append(cls)
        vols.append(vol)
        strikes.append(k)
        logMoneynesses.append(m)
        print("%10s %10s %10s %25s %25s" % (spot, k, cls, m, vol))
    data_for_optimiztion = [logMoneynesses, total_variance,expiration_date]

    print("-" * 110)
    return data_for_optimiztion
    #return vols,expiration_date,strikes,spot,risk_free_rate,closes,logMoneynesses

def get_data_from_BS_put_cnvt(nbr_month,curve,show=True):

    call_volatilities, put_converted_volatilites, strikes_call, strikes_put, \
    close_call, close_put, logMoneyness_call, logMoneyness_put, expiration_date, spot = \
        get_impliedvolmat_BS_put_cnvt_oneMaturity(
            evalDate, curve,daycounter, calendar, nbr_month,1.0, 0.0001, 0.001, False)
    vols           = []
    strikes        = []
    logMoneynesses = []
    closes         = []
    total_variance = []
    if show:
        print("PUT (cnvt) : ")
        print("=" * 110)
        print("%10s %10s %10s %25s %25s %20s" % ("Spot", "Strike", "close", "moneyness", "impliedVol", "Error (%)"))
        print("-" * 110)
    risk_free_rate = curve.zeroRate(expiration_date, daycounter, ql.Continuous).rate()
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    for idx_put , k in enumerate(strikes_put):
        m       = logMoneyness_put[idx_put]
        vol = put_converted_volatilites[idx_put]
        cls = close_put[idx_put]
        tv = (vol ** 2) * ttm
        total_variance.append(tv)
        closes.append(cls)
        vols.append(vol)
        strikes.append(k)
        logMoneynesses.append(m)
        if show : print("%10s %10s %10s %25s %25s %20s" % (spot, k, cls, m, vol, 0.0))
    data_for_optimiztion = [logMoneynesses, total_variance,expiration_date]
    if show : print("-" * 110)
    return data_for_optimiztion
    #return vols,expiration_date,strikes,spot,risk_free_rate,closes,logMoneynesses

def get_data_from_BS_put(type,next_i_month,curve,show=True):

    print('Put')
    vols_put, expiration_date, strikes_put, spot,close_put,logMoneyness_put = get_impliedvolmat_BS_oneMaturity(
        type,evalDate, daycounter, calendar, nbr_month,1.0,0.0001,0.001,show)
    ## Select OTM options from Calls and Puts
    vols           = []
    strikes        = []
    logMoneynesses = []
    closes         = []
    total_variance = []
    print("Convert put moneyness to log(Ft/k):")
    print("=" * 110)
    print("%10s %10s %10s %25s %25s %20s" % ("Spot", "Strike", "close", "moneyness", "impliedVol", "Error (%)"))
    print("-" * 110)
    risk_free_rate = curve.zeroRate(expiration_date, daycounter, ql.Continuous).rate()
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    rf = curve.zeroRate(expiration_date, daycounter, ql.Continuous).rate()
    Ft = spot * math.exp(rf * ttm)
    for idx_put , k in enumerate(strikes_put):
        m   =  math.log(Ft / k, math.e) ######################
        vol = vols_put[idx_put]
        tv  = (vol ** 2) * ttm
        cls = close_put[idx_put]
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

########################################################################################################################
w.start()
# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(12,5,2017)
#evalDate = ql.Date(10,7,2017)
month_indexs = [evalDate.month(),evalDate.month()+1,9,12]
#month_indexs = [evalDate.month()]
# Calibrate SVI total variance curve
nbr_month = evalDate.month()+1
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
        curve = get_curve_treasuryBond(evalDate, daycounter)
        #data = get_data_from_BS_put_cnvt(nbr_month,curve,True)
        data = get_data_from_BS_put_cnvt(nbr_month, curve, show)
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
    nm   = SVI_NelderMeadOptimization(data, init_adc = [0.5,0.5,0.5], init_msigma = [1,1])
    _a_star, _d_star, _c_star, m_star, sigma_star = nm.optimization()
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
