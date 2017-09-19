import Utilities.hedging_utility as hedge_util
from pricing_engines.svimodel import svimodel
from pricing_engines.blackcalculator import blackcalculator
import QuantLib as ql
import math


def Date(d,m,y):
    return ql.Date(d,m,y)


def delta_hedge_svi(hedge_date,liquidition_date,daycounter,calendar,
                spot_c,spot_h,spot_l,black_var_surface,calibrated_params,
                orgnized_data_l,orgnized_data_h,rfs,optiontype):
    hedge_error_Ms = {}
    hedge_error_pct_Ms = {}
    if optiontype == ql.Option.Call: iscall = True
    else: iscall = False
    for nbr_month in range(4):
        params_Mi = calibrated_params[nbr_month]
        rf = rfs.get(nbr_month)
        moneyness_l, strikes_l, close_prices_l, expiration_date_l = orgnized_data_l.get(nbr_month)
        moneyness_h, strikes_h, close_prices_h, expiration_date_h = orgnized_data_h.get(nbr_month)
        temp_date = calendar.advance(liquidition_date, ql.Period(5, ql.Days))
        if expiration_date_l <= temp_date: continue
        hedge_errors = []
        hedge_errors_pct = []
        moneyness = []
        ttm = daycounter.yearFraction(hedge_date,expiration_date_h)
        svi = svimodel(ttm,params_Mi)
        discount = math.exp(-rf * ttm)
        forward = spot_c / math.exp(-rf * ttm)
        for idx_k, k in enumerate(strikes_h):
            if k in close_prices_l.keys():
                close_l = close_prices_l.get(k)
            else:
                continue
            close_h = close_prices_h.get(k)
            # No arbitrage condition
            if close_h < k * math.exp(-rf * ttm) - spot_h:
                continue
            if close_h < 0.0001:
                continue
            #delta = hedge_util.calculate_delta_svi(black_var_surface, hedge_date, daycounter, calendar,
            #                                     spot_c, rf, k, expiration_date_h, optiontype)
            dSigma_dK = svi.calculate_dSigma_dK(k,forward,ttm)
            stdDev = svi.svi_iv_function(math.log(k/forward, math.e))*math.sqrt(ttm)
            black = blackcalculator(k, forward, stdDev, discount, iscall)
            delta = black.delta_total(spot_c,dSigma_dK)
            #delta = hedge_util.calculate_effective_delta_svi(hedge_date,daycounter,calendar,params_Mi,spot_c,rf,k,expiration_date_h,optiontype)
            #cash_on_hedge_date = hedge_util.calculate_cash_position(hedge_date, close_h, spot_h, delta)
            #hedge_error = hedge_util.calculate_hedging_error(hedge_date, liquidition_date, daycounter, spot_l, close_l, delta,
            #                                     cash_on_hedge_date, rf)
            t = daycounter.yearFraction(hedge_date, liquidition_date)
            cash_h = close_h - delta * spot_h
            pnl = delta * spot_l + cash_h * math.exp(rf * t) - close_l
            pnl_pct = pnl / close_h
            if abs(pnl_pct) > 10:
                #print(liquidition_date, ',', nbr_month, ',', k, 'too large error', pnl_pct)
                continue
            hedge_error = round(pnl, 4)
            pnl_pct = round(pnl_pct, 4)
            hedge_errors.append(hedge_error)
            hedge_errors_pct.append(pnl_pct)
            moneyness.append(round(spot_h / k, 4))
        hedge_error_Ms.update({nbr_month: [moneyness, hedge_errors]})
        hedge_error_pct_Ms.update({nbr_month: [moneyness, hedge_errors_pct]})
    return hedge_error_Ms,hedge_error_pct_Ms

def delta_hedge_svi_effdelta(hedge_date,liquidition_date,daycounter,calendar,
                spot_c,spot_h,spot_l,black_var_surface,calibrated_params,
                orgnized_data_l,orgnized_data_h,rfs,optiontype):
    hedge_error_Ms = {}
    hedge_error_pct_Ms = {}
    for nbr_month in range(4):
        params_Mi = calibrated_params[nbr_month]
        rf = rfs.get(nbr_month)
        moneyness_l, strikes_l, close_prices_l, expiration_date_l = orgnized_data_l.get(nbr_month)
        moneyness_h, strikes_h, close_prices_h, expiration_date_h = orgnized_data_h.get(nbr_month)
        temp_date = calendar.advance(liquidition_date, ql.Period(5, ql.Days))
        if expiration_date_l <= temp_date: continue
        hedge_errors = []
        hedge_errors_pct = []
        moneyness = []
        ttm = daycounter.yearFraction(hedge_date,expiration_date_h)
        svi = svimodel(ttm,params_Mi)
        for idx_k, k in enumerate(strikes_h):
            if k in close_prices_l.keys():
                close_l = close_prices_l.get(k)
            else:
                continue
            close_h = close_prices_h.get(k)
            # No arbitrage condition
            if close_h < k * math.exp(-rf * ttm) - spot_h:
                continue
            if close_h < 0.0001:
                continue
            #delta = hedge_util.calculate_delta_svi(black_var_surface, hedge_date, daycounter, calendar,
            #                                     spot_c, rf, k, expiration_date_h, optiontype)
            delta = svi.calculate_effective_delta(spot_c,0.0005,k,math.exp(-rf*ttm),False)
            #delta = hedge_util.calculate_effective_delta_svi(hedge_date,daycounter,calendar,params_Mi,spot_c,rf,k,expiration_date_h,optiontype)
            #cash_on_hedge_date = hedge_util.calculate_cash_position(hedge_date, close_h, spot_h, delta)
            #hedge_error = hedge_util.calculate_hedging_error(hedge_date, liquidition_date, daycounter, spot_l, close_l, delta,
            #                                     cash_on_hedge_date, rf)
            t = daycounter.yearFraction(hedge_date, liquidition_date)
            cash_h = close_h - delta * spot_h
            pnl = delta * spot_l + cash_h * math.exp(rf * t) - close_l
            pnl_pct = pnl / close_h
            if abs(pnl_pct) > 10:
                #print(liquidition_date, ',', nbr_month, ',', k, 'too large error', pnl_pct)
                continue
            hedge_error = round(pnl, 4)
            pnl_pct = round(pnl_pct, 4)
            hedge_errors.append(hedge_error)
            hedge_errors_pct.append(pnl_pct)
            moneyness.append(round(spot_h / k, 4))
        hedge_error_Ms.update({nbr_month: [moneyness, hedge_errors]})
        hedge_error_pct_Ms.update({nbr_month: [moneyness, hedge_errors_pct]})
    return hedge_error_Ms,hedge_error_pct_Ms
