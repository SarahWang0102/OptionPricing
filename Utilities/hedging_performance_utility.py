import Utilities.hedging_utility as hedge_util
import QuantLib as ql
import math


def Date(d,m,y):
    return ql.Date(d,m,y)


def delta_hedge_svi(hedge_date,liquidition_date,daycounter,calendar,
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
        for idx_k, k in enumerate(strikes_h):
            if k in close_prices_l.keys():
                close_l = close_prices_l.get(k)
            else:
                continue
            close_h = close_prices_h.get(k)
            # No arbitrage condition
            ttm = daycounter.yearFraction(hedge_date, expiration_date_h)
            if close_h < k * math.exp(-rf * ttm) - spot_h:
                continue
            if close_h < 0.0001:
                continue
            delta = hedge_util.calculate_delta_svi(black_var_surface, hedge_date, daycounter, calendar,
                                                  spot_c, rf, k, expiration_date_h, optiontype)
            cash_on_hedge_date = hedge_util.calculate_cash_position(hedge_date, close_h, spot_h, delta)
            hedge_error = hedge_util.calculate_hedging_error(hedge_date, liquidition_date, daycounter, spot_l, close_l, delta,
                                                  cash_on_hedge_date, rf)
            hedge_error_pct = hedge_error / close_h
            if abs(hedge_error_pct) > 3:
                print(liquidition_date, ',', nbr_month, ',', k, 'too large error', hedge_error_pct)
                #continue
            hedge_error = round(hedge_error, 4)
            hedge_error_pct = round(hedge_error_pct, 4)
            hedge_errors.append(hedge_error)
            hedge_errors_pct.append(hedge_error_pct)
            moneyness.append(round(spot_h / k, 4))
        hedge_error_Ms.update({nbr_month: [moneyness, hedge_errors]})
        hedge_error_pct_Ms.update({nbr_month: [moneyness, hedge_errors_pct]})
    return hedge_error_Ms,hedge_error_pct_Ms
