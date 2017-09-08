import exotic_options.exotic_option_utilities as exotic_util
import Utilities.svi_prepare_vol_data as svi_data
from bs_model import bs_estimate_vol as bs_vol
from Utilities.utilities import *
import Utilities.hedging_utility as hedge_util
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
import Utilities.plot_util as pu
import math

with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_puts.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/total_hedging_dates_puts.pickle', 'rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_bs_estimated_vols.pickle','rb') as f:
    estimated_vols = pickle.load(f)[0]

# Evaluation Settings
begDate = ql.Date(19,1,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
begDate = calendar.advance(begDate,ql.Period(1,ql.Days))

fee = 0.6/100
# Down and out Call
optiontype = ql.Option.Put


curve = svi_data.get_curve_treasury_bond(begDate,daycounter)
c, p, maturity_dates, S0, r = daily_svi_dataset.get(to_dt_date(begDate))
maturityDate = to_ql_date(maturity_dates[3])

#barriers = S0 - np.arange(0.01,0.1,0.01)
strike = S0
# Knock out : Barrier at OTM
barriers = [S0+0.1]
barrierType = ql.Barrier.UpOut
# Reverse knock out : Barrier at ATM
#barriers = [S0-0.1]
#barrierType = ql.Barrier.DownOut

rebalance = 1 # days
underlying = ql.SimpleQuote(S0)
plot = True
print("=" * 120)
print("%15s %20s %20s %20s %20s  " % ("barrier", "hedge_error_bs", "hedge_error_svi",
                                          "hedge_cost_bs", "hedge_cost_svi"))
for barrier in barriers:
    barrier_flag = False
    if plot:
        print("="*100)
        print("%15s %25s %25s %25s" % ("maturityDate","barrier","strike", "spot"))
        print("%15s %25s %25s %25s" % (maturityDate,barrier,strike, S0))
        print("="*100)

    if plot:
        print("="*120)
        print("%15s %15s %15s %15s %15s %15s %15s" % ("date","spot","hedging_error_bs",
                                                                "hedging_error_svi","replicate_bs",
                                                                "replicate_svi","reference_npv"))
        print("-"*120)
    delta_bs_previous = 0.0
    delta_svi_previous = 0.0
    hedging_errors_bs = []
    hedging_errors_svi = []
    hedging_costs_bs = []
    hedging_costs_svi = []
    hist_spots = []
    # Delta Hedge
    c_date = calendar.advance(begDate, ql.Period(-1, ql.Days))
    l_date = calendar.advance(begDate, ql.Period(2, ql.Days))
    while l_date <= maturityDate:
        try:
            c_date = calendar.advance(c_date, ql.Period(1, ql.Days))
            h_date = calendar.advance(c_date, ql.Period(1, ql.Days)) # hedge date
            l_date = calendar.advance(c_date, ql.Period(2, ql.Days)) # liquidation date

            exercise = ql.EuropeanExercise(maturityDate)
            payoff = ql.PlainVanillaPayoff(optiontype, strike)

            # calibration date
            cal_vols_c, put_vols_c, maturity_dates_c, spot_c, risk_free_rates_c = daily_svi_dataset.get(to_dt_date(c_date))
            calibrated_params = daily_params.get(to_dt_date(c_date))  # on calibrate_date
            black_var_surface_c = hedge_util.get_local_volatility_surface(calibrated_params, to_ql_dates(maturity_dates_c),
                                                                        c_date, daycounter, calendar, spot_c,
                                                                        risk_free_rates_c)
            const_vol_c = estimated_vols.get(to_dt_date(c_date))

            # create hedge portfolio
            curve_h = svi_data.get_curve_treasury_bond(h_date, daycounter)
            rf_h = curve_h.zeroRate(maturityDate, daycounter, ql.Continuous).rate()
            cal_vols_h, put_vols_h, maturity_dates_h, spot_h, risk_free_rates_h = daily_svi_dataset.get(to_dt_date(h_date))
            yield_h = ql.YieldTermStructureHandle(curve_h)
            dividend_h = ql.YieldTermStructureHandle(ql.FlatForward(h_date, 0.0, daycounter))
            underlying.setValue(spot_c)
            process_svi_h = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying), dividend_h,
                                                         yield_h, ql.BlackVolTermStructureHandle(black_var_surface_c))
            hist_spots.append(spot_c)
            option_price_h = exotic_util.barrier_npv_ql(h_date,hist_spots,barrierType, barrier, payoff, exercise,process_svi_h)
            if option_price_h == 0.0:
                print('0')
                delta_bs = 0.0
                delta_svi = 0.0
            else:
                delta_bs = hedge_util.calculate_delta_bs(h_date, daycounter, calendar,
                                                         const_vol_c, spot_c, rf_h, strike, maturityDate, optiontype)
                delta_svi = hedge_util.calculate_delta_svi(black_var_surface_c, h_date, daycounter, calendar, spot_c,
                                                           curve_h.zeroRate(maturityDate, daycounter, ql.Continuous).rate(),
                                                           strike, maturityDate, optiontype)
            cash_svi_h = option_price_h - delta_svi*spot_h
            cash_bs_h = option_price_h - delta_bs*spot_h
            replicate_svi_h = delta_svi * spot_h + cash_svi_h
            replicate_bs_h = delta_bs * spot_h + cash_bs_h
            #ratio_svi = replicate_svi_h/option_price_h
            #ratio_bs = replicate_bs_h / option_price_h
            #print(ratio_bs,ratio_svi)
            # liquidate replication portfolio
            cal_vols_l, put_vols_l, maturity_dates_l, spot_l, risk_free_rates_l = daily_svi_dataset.get(to_dt_date(l_date))
            params = daily_params.get(to_dt_date(h_date))  # on calibrate_date
            black_var_surface_h = hedge_util.get_local_volatility_surface(calibrated_params, to_ql_dates(maturity_dates_c),
                                                                        c_date, daycounter, calendar, spot_c,
                                                                        risk_free_rates_c)
            hist_spots.append(spot_h)
            curve_l = svi_data.get_curve_treasury_bond(h_date, daycounter)
            yield_l = ql.YieldTermStructureHandle(curve_l)
            dividend_l = ql.YieldTermStructureHandle(ql.FlatForward(l_date, 0.0, daycounter))
            underlying.setValue(spot_h)
            process_svi_l = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying), dividend_l,
                                                         yield_l, ql.BlackVolTermStructureHandle(black_var_surface_h))
            option_price_l = exotic_util.barrier_npv_ql(l_date, hist_spots, barrierType, barrier, payoff, exercise,
                                                        process_svi_l)

            t = daycounter.yearFraction(h_date, l_date)
            cash_svi_l = cash_svi_h*math.exp(curve_h.zeroRate(maturityDate, daycounter, ql.Continuous).rate()* t)
            cash_bs_l = cash_bs_h*math.exp(curve_h.zeroRate(maturityDate, daycounter, ql.Continuous).rate()* t)
            replicate_svi_l = delta_svi * spot_l + cash_svi_l
            replicate_bs_l = delta_bs * spot_l + cash_bs_l
            hedging_error_bs = replicate_bs_l  - option_price_l
            hedging_error_svi = replicate_svi_l  - option_price_l
            hedging_errors_bs.append(hedging_error_bs)
            hedging_errors_svi.append(hedging_error_svi)
            #hedging_costs_bs.append(hedge_cost_bs)
            #hedging_costs_svi.append(hedge_cost_svi)
            if plot: print("%15s %15s %15s %15s %15s %15s %15s" % (l_date,
                                                                  round(spot_l,4),
                                                                  round(hedging_error_bs,4),
                                                                  round(hedging_error_svi,4),
                                                                  round(replicate_bs_l,4),
                                                                  round(replicate_svi_l,4),
                                                                  round(option_price_l,4)))
        except Exception as e:
            #print(e)
            continue
    if plot:
        print("=" * 120)
        print("%15s %20s %20s %20s %20s  " % ("barrier", "hedge_error_bs", "hedge_error_svi",
                                          "hedge_cost_bs", "hedge_cost_svi"))
        print("-" * 120)
    print("%15s %20s %20s %20s %20s  " % (barrier, round(sum(hedging_errors_bs), 4),
                                         round(sum(hedging_errors_svi), 4),
                                         round(sum(hedging_costs_bs), 4),
                                         round(sum(hedging_costs_svi), 4)))
print("=" * 120)









