
import datetime
import QuantLib as ql
import math
import numpy as np
import pandas as pd
import os

def get_spot_price(evalDate):
    # Uderlying market price
    underlyingdata = pd.read_json(os.getcwd() + '\marketdata\spotclose' + '.json')
    spot_ts = underlyingdata.values.tolist()
    dates_ts = underlyingdata.index.tolist()
    dt = datetime.datetime(evalDate.year(), evalDate.month(), evalDate.dayOfMonth(),
                           dates_ts[0].hour, dates_ts[0].minute, dates_ts[0].second, dates_ts[0].microsecond)
    spot = spot_ts[dates_ts.index(dt)][0]
    return spot





def implied_vol_function(params,x_svi):
    a_star, b_star, rho_star, m_star, sigma_star = params
    iv = np.sqrt( a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))
    return iv

def calculate_delta_svi(hedge_date,daycounter,calendar,params_Mi,spot,rf_h_d,strike,maturitydt,optiontype):
    ql.Settings.instance().evaluationDate = hedge_date
    step = 0.005
    rf = rf_h_d
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, rf, daycounter))
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, 0.0, daycounter))
    exercise = ql.EuropeanExercise(maturitydt)
    payoff = ql.PlainVanillaPayoff(optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)
    ttm = daycounter.yearFraction(hedge_date, maturitydt)

    s_plus = spot + step
    s_minus = spot - step
    Ft_plus = s_plus * math.exp(rf * ttm)
    x_plus = math.log(strike / Ft_plus, math.e)
    Ft_minus = s_minus * math.exp(rf * ttm)
    x_minus = math.log(strike / Ft_minus, math.e)
    iv_plus = implied_vol_function(params_Mi,x_plus)
    iv_minus = implied_vol_function(params_Mi,x_minus)
    flat_vol_plus = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(hedge_date, calendar, iv_plus, daycounter))
    flat_vol_minus = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(hedge_date, calendar, iv_minus, daycounter))

    process_plus = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(s_plus)), dividend_ts, yield_ts, flat_vol_plus)
    process_minus = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(s_minus)), dividend_ts, yield_ts,
                                                flat_vol_minus)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process_plus))
    npv_plus = option.NPV()
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process_minus))
    npv_minus = option.NPV()
    delta = (npv_plus-npv_minus)/(s_plus-s_minus)
    return delta

def get_local_volatility_surface(calibrated_params,maturity_dates_c,calibrate_date,daycounter,calendar,spot,rfs):
    strikes = np.arange(1.0, 5.0, 0.1 / 100)
    data_BVS = []
    for idx_mdt,mdt in enumerate(maturity_dates_c):
        params = calibrated_params[idx_mdt]
        a_star, b_star, rho_star, m_star, sigma_star = params
        ttm = daycounter.yearFraction(calibrate_date,mdt)
        rf = rfs.get(idx_mdt)
        Ft = spot * math.exp(rf * ttm)
        x_svi =  np.log(strikes/Ft)
        #vol = np.sqrt(np.maximum(0,a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))))
        vol = np.sqrt(np.sqrt(np.maximum(0, a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))))
        data_BVS.append(vol)
    implied_vols = ql.Matrix(len(strikes), len(maturity_dates_c))
    for i in range(implied_vols.rows()):
        for j in range(implied_vols.columns()):
            implied_vols[i][j] = data_BVS[j][i]
    black_var_surface = ql.BlackVarianceSurface(calibrate_date, calendar,maturity_dates_c, strikes,implied_vols, daycounter)
    return black_var_surface

def get_local_volatility_surface_smoothed(calibrated_params_list,maturity_dates_c,calibrate_dates,daycounter,calendar,spot,rfs):
    strikes = np.arange(1.0, 5.0, 0.1 / 100)
    data_BVS = []

    for idx_mdt,mdt in enumerate(maturity_dates_c):
        vol_list = []
        avg_vols = []
        for idx_calibrate,calibrated_params in enumerate(calibrated_params_list):
            params = calibrated_params[idx_mdt]
            a_star, b_star, rho_star, m_star, sigma_star = params
            calibrate_date = calibrate_dates[idx_calibrate]
            ttm = daycounter.yearFraction(calibrate_date,mdt)
            rf = rfs.get(idx_mdt)
            Ft = spot * math.exp(rf * ttm)
            x_svi =  np.log(strikes/Ft)
            #vol = np.sqrt(np.maximum(0,a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))))
            vol = np.sqrt(np.sqrt(np.maximum(0, a_star + b_star * (
            rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))))
            vol_list.append(vol)
        for idx_v,v in enumerate(vol_list[0]):
            avg_vol = 0.0
            for vols in vol_list:
                avg_vol += vols[idx_v]
            avg_vol = avg_vol/len(vol_list)
            avg_vols.append(avg_vol)
        data_BVS.append(avg_vols)
    implied_vols = ql.Matrix(len(strikes), len(maturity_dates_c))
    for i in range(implied_vols.rows()):
        for j in range(implied_vols.columns()):
            implied_vols[i][j] = data_BVS[j][i]
    black_var_surface = ql.BlackVarianceSurface(calibrate_dates[0], calendar,maturity_dates_c, strikes,implied_vols, daycounter)
    return black_var_surface

def calculate_delta_sviVolSurface(black_var_surface,hedge_date,daycounter,calendar,params_Mi,spot,rf,strike,maturitydt,optiontype):
    ql.Settings.instance().evaluationDate = hedge_date
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, rf, daycounter))
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, 0.0, daycounter))
    exercise = ql.EuropeanExercise(maturitydt)
    payoff = ql.PlainVanillaPayoff(optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)

    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts,
                                           yield_ts,ql.BlackVolTermStructureHandle(black_var_surface))

    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
    delta = option.delta()
    return delta


def calculate_delta_formula_svi(hedge_date,daycounter,calendar,params_Mi,spot,rf,strike,maturitydt,optiontype):
    ql.Settings.instance().evaluationDate = hedge_date
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, rf, daycounter))
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, 0.0, daycounter))
    exercise = ql.EuropeanExercise(maturitydt)
    payoff = ql.PlainVanillaPayoff(optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)
    ttm = daycounter.yearFraction(hedge_date, maturitydt)

    Ft = spot * math.exp(rf * ttm)
    x = math.log(strike / Ft, math.e)
    iv = implied_vol_function(params_Mi,x)
    # Construct SVI IV surface ! !
    flat_vol = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(hedge_date, calendar, iv, daycounter))

    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,flat_vol)

    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
    delta = option.delta()
    return delta

def calculate_delta_bs(hedge_date,daycounter,calendar,estimate_vol,spot,rf_h_d,strike,maturitydt,optiontype):
    ql.Settings.instance().evaluationDate = hedge_date
    step = 0.01
    rf = rf_h_d
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, rf, daycounter))
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(hedge_date, 0.0, daycounter))
    exercise = ql.EuropeanExercise(maturitydt)
    payoff = ql.PlainVanillaPayoff(optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)
    ttm = daycounter.yearFraction(hedge_date, maturitydt)

    s_plus = spot + step
    s_minus = spot - step
    Ft_plus = s_plus * math.exp(rf * ttm)
    x_plus = math.log(strike / Ft_plus, math.e)
    Ft_minus = s_minus * math.exp(rf * ttm)
    x_minus = math.log(strike / Ft_minus, math.e)
    flat_vol_plus = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(hedge_date, calendar, estimate_vol, daycounter))
    flat_vol_minus = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(hedge_date, calendar, estimate_vol, daycounter))

    process_plus = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(s_plus)), dividend_ts, yield_ts, flat_vol_plus)
    process_minus = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(s_minus)), dividend_ts, yield_ts,
                                                flat_vol_minus)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process_plus))
    npv_plus = option.NPV()
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process_minus))
    npv_minus = option.NPV()
    delta = (npv_plus-npv_minus)/(s_plus-s_minus)
    return delta

def calculate_cash_position(hedge_date,option_price,spot,delta):
    cash_position = option_price - delta*spot
    return cash_position

def calculate_hedging_error(hedge_date,liquidition_date,daycounter,spot,option_price,delta,cash_position,rf_from_curve):
    t = daycounter.yearFraction(hedge_date, liquidition_date)
    hedging_error = abs(delta*spot + cash_position*math.exp(rf_from_curve * t) - option_price)
    if math.isnan(hedging_error):
        print('warning! hedging error is nan')
    return hedging_error

def hedging_performance(svi_pct,dates):
    mny_0 = {} # S/k <0.97
    mny_1 = {} # 0.97 - 1.00
    mny_2 = {} # 1.00 - 1.03
    mny_3 = {} # S/k > 1.03

    for date in dates:
        if date in svi_pct.keys():
            pct_Ms = svi_pct.get(date)
        else:
            print('date not in list')
            continue
        # month number = 1
        for nbr_m in pct_Ms.keys():
            if nbr_m not in mny_0.keys():mny_0.update({nbr_m:[]})
            if nbr_m not in mny_1.keys():mny_1.update({nbr_m: []})
            if nbr_m not in mny_2.keys():mny_2.update({nbr_m:[]})
            if nbr_m not in mny_3.keys():mny_3.update({nbr_m: []})
            moneyness = pct_Ms.get(nbr_m)[0]
            errors = pct_Ms.get(nbr_m)[1]
            if type(moneyness) == float:
                moneyness = [moneyness]
                errors = [errors]
            for idx_m,mny in enumerate(moneyness):
                e = errors[idx_m]
                if math.isnan(e) :
                    print(e)
                    e = 0.0
                if mny <= 0.97:
                    mny_0.get(nbr_m).append(e)
                elif mny > 0.97 and mny <= 1.00 :
                    mny_1.get(nbr_m).append(e)
                elif mny > 1.00 and mny <= 1.03:
                    mny_2.get(nbr_m).append(e)
                else:
                    mny_3.get(nbr_m).append(e)
    return mny_0,mny_1,mny_2,mny_3

def get_1st_percentile_dates(daily_pct_hedge_errors):
    # 1st_percentile from 2015.9 to 2016.1
    results = {}
    for dt in daily_pct_hedge_errors:
        if dt > datetime.date(2015, 9, 1) and dt <= datetime.date(2016, 1, 29):
            results.update({dt:daily_pct_hedge_errors.get(dt)})
    return results

def get_2nd_percentile_dates(daily_pct_hedge_errors):
    # 1st_percentile from 2016.2 to 2016.7
    results = {}
    for dt in daily_pct_hedge_errors:
        if dt > datetime.date(2016, 1, 29) and dt <= datetime.date(2016, 7, 31):
            results.update({dt:daily_pct_hedge_errors.get(dt)})
    return results

def get_3rd_percentile_dates(daily_pct_hedge_errors):
    # 1st_percentile from 2016.8 to 2017.1
    results = {}
    for dt in daily_pct_hedge_errors:
        if dt > datetime.date(2016, 7, 31) and dt <= datetime.date(2017, 1, 28):
            results.update({dt:daily_pct_hedge_errors.get(dt)})
    return results

def get_4th_percentile_dates(daily_pct_hedge_errors):
    # 1st_percentile from 2017.2 to 2017.7
    results = {}
    for dt in daily_pct_hedge_errors:
        if dt > datetime.date(2017, 1, 28) and dt <= datetime.date(2017, 7, 30):
            results.update({dt:daily_pct_hedge_errors.get(dt)})
    return results