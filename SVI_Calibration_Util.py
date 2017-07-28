from VolatilityData_readpkl import *
from SVI_Calibration_Optimization_Util import *


def get_underlying_ts():
    underlyingdata = pd.read_pickle(os.getcwd()+'\marketdata\spotclose' +'.pkl')
    dates_ts  = underlyingdata.index.tolist()
    spot_ts   = underlyingdata.values.tolist()
    spot_dic  = {}
    for idx_dt,dt in enumerate(dates_ts):
        date_tmp = pd.to_datetime(dt)
        date_ql = ql.Date(date_tmp.day, date_tmp.month, date_tmp.year)
        spot_dic.update({date_ql:spot_ts[idx_dt][0]})
    return spot_dic

def get_data_from_BS_OTM_PCPRate(evalDate,daycounter,calendar,curve,show=True):

    cal_vols_data_moneyness, put_vols_data_monetness,expiration_dates,spot,rf_Ks_months \
        = get_call_put_impliedVols_moneyness_PCPrate(evalDate, curve,daycounter, calendar,
                                                     maxVol=1.0,step=0.0001,precision=0.001,show=False)
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
    return data_for_optimiztion_months,rf_Ks_months

def get_data_from_BS_put_cnvt(evalDate,daycounter,calendar,nbr_month,curve,show=True):

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
        if show: print("%10s %10s %10s %25s %25s %20s" % (spot, k, cls, m, vol, 0.0))
    data_for_optimiztion = [logMoneynesses, total_variance,expiration_date]

    if show: print("-" * 110)
    return data_for_optimiztion
    #return vols,expiration_date,strikes,spot,risk_free_rate,closes,logMoneynesses

def get_data_from_BS_OTM(evalDate,daycounter,calendar,nbr_month,curve,show=True):

    call_volatilities, put_converted_volatilites, strikes_call, strikes_put, \
    close_call, close_put, logMoneyness_call, logMoneyness_put, expiration_date, spot = \
        get_impliedvolmat_BS_OTM_oneMaturity(
            evalDate,curve, daycounter, calendar, nbr_month,1.0, 0.0001, 0.001, True)
    vols           = []
    strikes        = []
    logMoneynesses = []
    closes         = []
    total_variance = []
    if show:
        print("CALL:")
        print("=" * 110)
        print("%10s %10s %10s %25s %25s" % ("Spot", "Strike", "close", "moneyness", "impliedVol"))
        print("-" * 110)
    for i, v in enumerate(call_volatilities):
        if show:
            print("%10s %10s %10s %25s %25s %20s" %
                  (spot, strikes_call[i], close_call[i], logMoneyness_call[i], call_volatilities[i], 0.0))
    if show:
        print("-" * 110)
        print("PUT (cnvt) :")
        print("=" * 110)
        print("%10s %10s %10s %25s %25s" % ("Spot", "Strike", "close", "moneyness", "impliedVol"))
        print("-" * 110)
    for i, v in enumerate(put_converted_volatilites):
        if show:
            print("%10s %10s %10s %25s %25s " %
                  (spot, strikes_put[i], close_put[i], logMoneyness_put[i], put_converted_volatilites[i]))
    if show:
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
        if show: print("%10s %10s %10s %25s %25s" % (spot, k, cls, m, vol))
    data_for_optimiztion = [logMoneynesses, total_variance,expiration_date]

    if show: print("-" * 110)
    return data_for_optimiztion
    #return vols,expiration_date,strikes,spot,risk_free_rate,closes,logMoneynesses

def get_data_from_BS_put(evalDate,daycounter,calendar,nbr_month,type,next_i_month,curve,show=True):

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

def get_data_from_wind(evalDate,daycounter,next_i_month,curve):
    vols, expiration_date, strikes, spot = get_impliedvolmat_wind_oneMaturity('认购',evalDate,next_i_month)
    risk_free_rate  =   curve.zeroRate(expiration_date,daycounter,ql.Continuous).rate()
    return vols, expiration_date, strikes, spot, risk_free_rate