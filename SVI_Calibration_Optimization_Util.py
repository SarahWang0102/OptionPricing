import QuantLib as ql
import numpy as np
import math
from SVI_NelderMeadOptimization import SVI_NelderMeadOptimization


def svi_calibration(evalDate,init_adc,calendar,daycounter,risk_free_rate,vols,expiration_date,strikes,spot):
    ql.Settings.instance().evaluationDate = evalDate

    # x: log(K/Ft) log-forward moneyness
    # v: implied molatilities
    x = []
    v = []
    vol = []
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    Ft = spot * math.exp(risk_free_rate * ttm)
    for j, K in enumerate(strikes):
        total_implied_variance = (vols[j]**2)*ttm # w = ttm*vol^2
        log_moneyness = math.log(K/Ft,math.e)
        x.append(log_moneyness)
        v.append(total_implied_variance)
        vol.append(vols[j])
    data = [x,v,vol,ttm,strikes,Ft]

    # Nelder-Mead Optimization
    nm = SVI_NelderMeadOptimization(data,init_adc)

    _a_star, _d_star, _c_star,m_star,sigma_star = nm.optimization()
    # SVI parameters: a, b, sigma, rho, m : _a = a*T; d = rho*b*sigma*T; c = b*sigma*T
    a_star = np.divide(_a_star,ttm)
    b_star = np.divide(_c_star/sigma_star,ttm)
    rho_star = np.divide(_d_star/(b_star*sigma_star),ttm)

    print('SVI parameters a,b,sigma,rho,m calibrated: ',a_star,b_star,sigma_star,rho_star,m_star)

    x_svi   = np.arange(-0.15,0.05,0.1/100)
    #v_svi  = np.maximum(0,a_star + b_star*(rho_star*(x_svi - m_star) + np.sqrt((x_svi - m_star)**2 + sigma_star**2 )))
    v_svi   = np.multiply(a_star + b_star*(rho_star*(x_svi - m_star) + np.sqrt((x_svi - m_star)**2 + sigma_star**2 )),ttm)
    x_svi2  = []
    v_svi2  = []
    for i, vi in enumerate(v_svi):
        if vi >= 0:
            x_svi2.append(x_svi[i])
            v_svi2.append(vi)
    #vol_svi = np.sqrt(np.array(v_svi2))
    vol_svi = v_svi2
    totalvariance = v
    log_forward_moneyness = x
    return log_forward_moneyness,totalvariance,np.array(x_svi2),vol_svi


def svi_calibration2(method,evalDate, init_adc, calendar, daycounter, risk_free_rate, vols, expiration_date, strikes, spot):
    ql.Settings.instance().evaluationDate = evalDate

    # x: log(K/Ft) log-forward moneyness
    # v: implied molatilities
    log_fmoneyness  = []
    totalvariance   = []
    volatility = []
    ttm = daycounter.yearFraction(evalDate, expiration_date)
    Ft  = spot * math.exp(risk_free_rate * ttm)
    for j, K in enumerate(strikes):
        tv = (vols[j] ** 2) * ttm  # w = ttm*vol^2
        moneyness = math.log(K / Ft, math.e)
        log_fmoneyness.append(moneyness)
        totalvariance.append(tv)
        volatility.append(vols[j])
    data = [log_fmoneyness, totalvariance, volatility, ttm, strikes, Ft]
    nm = SVI_NelderMeadOptimization(data, init_adc)
    if method == 'nm': # Nelder-Mead Optimization
        _a_star, _d_star, _c_star, m_star, sigma_star = nm.optimization()
    elif method == 'ols':
        _a_star, _d_star, _c_star, m_star, sigma_star = nm.optimization_SLSQP()
    else:
        return
    # SVI parameters: a, b, sigma, rho, m : _a = a*T; d = rho*b*sigma*T; c = b*sigma*T
    a_star = np.divide(_a_star, ttm)
    b_star = np.divide(_c_star , (sigma_star* ttm))
    rho_star = np.divide(_d_star , _c_star)

    print('SVI parameters a,b,sigma,rho,m calibrated: ', a_star, b_star, sigma_star, rho_star, m_star)

    return log_fmoneyness, totalvariance,volatility, a_star, b_star, sigma_star, rho_star, m_star


def svi_calibration3(method,evalDate, init_adc, init_msigma,calendar, daycounter,
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
    nm = SVI_NelderMeadOptimization(data, init_adc,init_msigma)
    if method == 'nm': # Nelder-Mead Optimization
        _a_star, _d_star, _c_star, m_star, sigma_star = nm.optimization()
    elif method == 'ols':
        _a_star, _d_star, _c_star, m_star, sigma_star = nm.optimization_SLSQP()
    else:
        return

    return log_fmoneyness, totalvariance,volatility, _a_star, _d_star, _c_star, m_star, sigma_star