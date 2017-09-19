import Utilities.svi_prepare_vol_data as svi_data
from svi_model.svi_NelderMead_optimization import  SVI_NelderMeadOptimization
import QuantLib as ql
import numpy as np
import pandas as pd
import os
import math

def get_svi_optimal_params_m(data,ttm,sim_no = 100):
    #ms_rnd = [0.1,0.1]
    #adc_rnd = [1,1,1]
    logMoneynesses = data[0]
    totalvariance = data[1]
    calibrated_params = []
    min_sse = 10
    for iter in range(sim_no):
        ms_0 = [0.1,0.1]
        adc_0 = [0.1,0.1,0.1]
        nm = SVI_NelderMeadOptimization(data,adc_0,ms_0,1e-7)
        calibrated_params, obj = nm.optimization()
        _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
        sse = 0.0
        for i, m in enumerate(logMoneynesses):
            tv = totalvariance[i]
            y_1 = np.divide((m - m_star), sigma_star)
            tv_1 = _a_star + _d_star * y_1 + _c_star * np.sqrt(y_1 ** 2 + 1)
            sse += (tv - tv_1) ** 2
        if sse >= min_sse: continue
        min_sse = sse
    _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
    a_star = np.divide(_a_star, ttm)
    b_star = np.divide(_c_star, (sigma_star * ttm))
    rho_star = np.divide(_d_star, _c_star)
    final_parames = [a_star, b_star, rho_star, m_star, sigma_star]
    return final_parames

def get_svi_optimal_params(data,ttm,sim_no = 100):
    ms_rnd = np.random.random([sim_no, 2])*5
    adc_rnd = np.random.random([sim_no, 3])*5
    logMoneynesses = data[0]
    totalvariance = data[1]
    calibrated_params = []
    min_sse = 10
    for iter in range(sim_no):
        ms_0 = ms_rnd[iter,:]
        adc_0 = adc_rnd[iter, :]
        nm = SVI_NelderMeadOptimization(data,adc_0,ms_0,1e-7)
        calibrated_params, obj = nm.optimization()
        _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
        sse = 0.0
        for i, m in enumerate(logMoneynesses):
            tv = totalvariance[i]
            y_1 = np.divide((m - m_star), sigma_star)
            tv_1 = _a_star + _d_star * y_1 + _c_star * np.sqrt(y_1 ** 2 + 1)
            sse += (tv - tv_1) ** 2
        if sse >= min_sse: continue
        min_sse = sse
    _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
    a_star = np.divide(_a_star, ttm)
    b_star = np.divide(_c_star, (sigma_star * ttm))
    rho_star = np.divide(_d_star, _c_star)
    final_parames = [a_star, b_star, rho_star, m_star, sigma_star]
    return final_parames

def orgnize_data_for_optimization(
        evalDate,daycounter,cal_vols_data_moneyness,
        put_vols_data_monetness,expiration_dates,spot):
    data_for_optimiztion_months = {}
    for idx_month, call_data in enumerate(cal_vols_data_moneyness):
        expiration_date = expiration_dates[idx_month]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        put_data = put_vols_data_monetness[idx_month]
        vols = []
        logMoneynesses = []
        total_variance = []
        impliedvols = []
        strikes = []
        for moneyness in call_data.keys():
            strike = call_data.get(moneyness)[1]
            #if strike >=spot: # K>Ft,OTM Call
            if moneyness >= 0:
                vol = call_data.get(moneyness)[0]
            else:
                vol = put_data.get(moneyness)[0]
            tv = (vol ** 2) * ttm
            total_variance.append(tv)
            vols.append(vol)
            logMoneynesses.append(moneyness)
            impliedvols.append(vol)
            strikes.append(strike)
        data = [logMoneynesses, total_variance,expiration_date,impliedvols,strikes]
        data_for_optimiztion_months.update({idx_month:data})
    return data_for_optimiztion_months

def orgnize_data_for_optimization_single_optiontype(
        evalDate,daycounter,vols_data_moneyness,expiration_dates,spot,curve,optiontype):
    data_for_optimiztion_months = {}
    for idx_month, option_data in enumerate(vols_data_moneyness):
        expiration_date = expiration_dates[idx_month]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        rf = curve.zeroRate(expiration_date, daycounter, ql.Continuous).rate()
        vols = []
        logMoneynesses = []
        total_variance = []
        impliedvols = []
        strikes = []
        for moneyness in option_data.keys():
            vol = option_data.get(moneyness)[0]
            strike = option_data.get(moneyness)[1]
            close = option_data.get(moneyness)[2]
            if optiontype == ql.Option.Call:
                if close < spot - strike * math.exp(-rf * ttm): continue
            else:
                if close < strike * math.exp(-rf * ttm) - spot: continue
            tv = (vol ** 2) * ttm
            total_variance.append(tv)
            vols.append(vol)
            logMoneynesses.append(moneyness)
            impliedvols.append(vol)
            strikes.append(strike)
        data = [logMoneynesses, total_variance,expiration_date,impliedvols,strikes]
        data_for_optimiztion_months.update({idx_month:data})
    return data_for_optimiztion_months

def orgnize_data_for_optimization_cmd(
        evalDate,daycounter,vols_data_moneyness,expiration_dates):
    data_for_optimiztion_months = {}
    for idx_month, option_data in enumerate(vols_data_moneyness):
        if len(option_data) == 0 : continue
        expiration_date = expiration_dates[idx_month]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        vols = []
        logMoneynesses = []
        total_variance = []
        impliedvols = []
        strikes = []
        spotid = idx_month
        for moneyness in option_data.keys():
            vol = option_data.get(moneyness)[0]
            strike = option_data.get(moneyness)[1]
            close = option_data.get(moneyness)[2]
            spotid = option_data.get(moneyness)[3]
            tv = (vol ** 2) * ttm
            total_variance.append(tv)
            vols.append(vol)
            logMoneynesses.append(moneyness)
            impliedvols.append(vol)
            strikes.append(strike)
        data = [logMoneynesses, total_variance,expiration_date,impliedvols,strikes]
        data_for_optimiztion_months.update({spotid:data})
    return data_for_optimiztion_months


def orgnize_data_for_hedging(
        evalDate,daycounter,vols_data_monetness,expiration_dates,spot):
    data_months = {}
    for idx_month, option_data in enumerate(vols_data_monetness):
        expiration_date = expiration_dates[idx_month]
        logMoneynesses = []
        impliedvols = []
        strikes = []
        close_prices = {}
        for moneyness in option_data.keys():
            vol = option_data.get(moneyness)[0]
            strike = option_data.get(moneyness)[1]
            close = option_data.get(moneyness)[2]
            logMoneynesses.append(moneyness)
            impliedvols.append(vol)
            strikes.append(strike)
            close_prices.update({strike:close})
        data = [logMoneynesses,strikes,close_prices,expiration_date]
        data_months.update({idx_month:data})
    return data_months


def orgnize_data_for_optimization_put(
        evalDate,daycounter,cal_vols_data_moneyness,
        put_vols_data_moneyness,expiration_dates,spot):
    data_for_optimiztion_months = {}
    for idx_month, put_data in enumerate(put_vols_data_moneyness):
        expiration_date = expiration_dates[idx_month]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        vols = []
        logMoneynesses = []
        total_variance = []
        impliedvols = []
        for moneyness in put_data.keys():
            strike = put_data.get(moneyness)[0]
            vol = put_data.get(moneyness)[0]
            tv = (vol ** 2) * ttm
            total_variance.append(tv)
            impliedvols.append(vol)
            vols.append(vol)
            logMoneynesses.append(moneyness)
        data = [logMoneynesses, total_variance,expiration_date,impliedvols]
        data_for_optimiztion_months.update({idx_month:data})
    return data_for_optimiztion_months
def orgnize_data_for_optimization_call(
        evalDate,daycounter,call_vols_data_moneyness,
        put_vols_data_moneyness,expiration_dates,spot):
    data_for_optimiztion_months = {}
    for idx_month, put_data in enumerate(call_vols_data_moneyness):
        expiration_date = expiration_dates[idx_month]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        vols = []
        logMoneynesses = []
        total_variance = []
        impliedvols = []
        for moneyness in put_data.keys():
            strike = put_data.get(moneyness)[0]
            vol = put_data.get(moneyness)[0]
            tv = (vol ** 2) * ttm
            total_variance.append(tv)
            impliedvols.append(vol)
            vols.append(vol)
            logMoneynesses.append(moneyness)
        data = [logMoneynesses, total_variance,expiration_date,impliedvols]
        data_for_optimiztion_months.update({idx_month:data})
    return data_for_optimiztion_months



def orgnize_data_for_optimization_rfs(evalDate,daycounter,calendar,curve,show=True):

    cal_vols_data_moneyness, put_vols_data_monetness,expiration_dates,spot,rf_Ks_months \
        = svi_data.get_call_put_impliedVols_moneyness_PCPrate_pcvt(evalDate, daycounter, calendar,
                                                     maxVol=1.0,step=0.0001,precision=0.001,show=False)
    data_for_optimiztion_months = {}
    for idx_month, call_data in enumerate(cal_vols_data_moneyness):
        expiration_date = expiration_dates[idx_month]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        put_data = put_vols_data_monetness[idx_month]
        vols = []
        logMoneynesses = []
        total_variance = []
        implied_vols = []
        strikes = []
        for moneyness in call_data.keys():
            strike = call_data.get(moneyness)[1]
            #if strike >=spot: # K>Ft,OTM Call
            if moneyness >= 0:
                vol = call_data.get(moneyness)[0]
            else:
                vol = put_data.get(moneyness)[0]
            tv = (vol ** 2) * ttm
            total_variance.append(tv)
            implied_vols.append(vol)
            vols.append(vol)
            logMoneynesses.append(moneyness)
            strikes.append(strike)
        data = [logMoneynesses, total_variance,expiration_date,implied_vols,strikes]
        data_for_optimiztion_months.update({idx_month:data})
    return data_for_optimiztion_months,rf_Ks_months

# One Maturity
def get_data_from_BS_put_cnvt(evalDate,daycounter,calendar,nbr_month,curve,show=True):

    call_volatilities, put_converted_volatilites, strikes_call, strikes_put, \
    close_call, close_put, logMoneyness_call, logMoneyness_put, expiration_date, spot = \
        svi_data.get_impliedvolmat_BS_put_cnvt_oneMaturity(
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
        svi_data.get_impliedvolmat_BS_OTM_oneMaturity(
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
    vols_put, expiration_date, strikes_put, spot,close_put,logMoneyness_put = svi_data.get_impliedvolmat_BS_oneMaturity(
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

def svi_calibration_helper(method,evalDate, init_adc, init_msigma,calendar, daycounter,
                     risk_free_rate, vols, expiration_date, strikes, spot):
    ql.Settings.instance().evaluationDate = evalDate

    # x: log(K/Ft) log-forward moneyness
    # v: implied molatilities
    log_fmoneyness  = []
    totalvariance   = []
    volatility = []
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    Ft  = spot * math.exp(risk_free_rate * ttm)
    for j, K in enumerate(strikes):
        if vols[j] <= 0: continue
        tv = (vols[j] ** 2) * ttm  # w = ttm*vol^2
        moneyness = math.log(K / Ft, math.e)
        log_fmoneyness.append(moneyness)
        totalvariance.append(tv)
        volatility.append(vols[j])
    data = [log_fmoneyness, totalvariance, volatility, ttm, strikes, Ft]
    print('data for optimization:')
    print('data = [log_fmoneyness, totalvariance, volatility, ttm, strikes, Ft] ')
    print('data : ',data)
    print('log_fmoneyness : ',log_fmoneyness)
    print('totalvariance : ', totalvariance)
    nm = SVI_NelderMeadOptimization(data)
    if method == 'nm': # Nelder-Mead Optimization
        cal_params,obj = nm.optimization()
        _a_star, _d_star, _c_star, m_star, sigma_star = cal_params
    elif method == 'ols':
        _a_star, _d_star, _c_star, m_star, sigma_star = nm.optimization_SLSQP()
    else:
        return

    return log_fmoneyness, totalvariance,volatility, _a_star, _d_star, _c_star, m_star, sigma_star