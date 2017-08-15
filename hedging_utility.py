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

def calculate_delta_bs(hedge_date,daycounter,calendar,estimate_vol,spot,rf_h_d,strike,maturitydt,optiontype):
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
    hedging_error = delta*spot + cash_position*math.exp(rf_from_curve * t) - option_price
    return hedging_error
