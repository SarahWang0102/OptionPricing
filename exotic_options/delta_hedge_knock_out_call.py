from pricing_options.Options import OptionBarrierEuropean,OptionPlainEuropean
from pricing_options.Evaluation import Evaluation
from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
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

with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_calls_1.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/total_hedging_dates_calls_1.pickle', 'rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_svi_dataset_calls_1.pickle','rb') as f:
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
optiontype = ql.Option.Call


#curve = svi_data.get_curve_treasury_bond(begDate,daycounter)
c, p, maturity_dates, S0, r = daily_svi_dataset.get(to_dt_date(begDate))
maturityDate = to_ql_date(maturity_dates[3])

#barriers = S0 - np.arange(0.01,0.1,0.01)
strike = S0
# Knock out : Barrier at OTM
#barriers = [S0-0.1]
barriers = [2.50]
barrierType = ql.Barrier.UpOut
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
# Reverse knock out : Barrier at ATM
#barriers = [S0+0.1]
#barrierType = ql.Barrier.IpOut

rebalance = 1 # days
underlying = ql.SimpleQuote(S0)
plot = True
#print("=" * 120)
#print("%15s %20s %20s %20s %20s  " % ("barrier", "pnl_bs", "pnl_delta1",
#                                          "pnl_deltatree", "pnl_totaldelta"))
for barrier in barriers:
    barrier_flag = False
    if plot:
        print("="*100)
        print("%15s %25s %25s %25s" % ("maturityDate","barrier","strike", "spot"))
        print("%15s %25s %25s %25s" % (maturityDate,barrier,strike, S0))
        print("="*100)

    if plot:
        print("="*120)
        print("%15s %15s %15s %15s %15s %15s %15s %15s" % ("date","spot","pnl_bs",
                                                                "pnl_svi","replicate_bs",
                                                                "barrier_bs","replicate_svi",
                                                           "barrier_svi"))
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
    barrier_option = OptionBarrierEuropean(strike, maturityDate, optiontype, barrier, barrierType)
    barrierql = barrier_option.option_ql
    while l_date <= maturityDate:
        try:

            c_date = calendar.advance(c_date, ql.Period(1, ql.Days))
            h_date = calendar.advance(c_date, ql.Period(1, ql.Days)) # hedge date
            l_date = calendar.advance(c_date, ql.Period(2, ql.Days)) # liquidation date

            exercise = ql.EuropeanExercise(maturityDate)
            payoff = ql.PlainVanillaPayoff(optiontype, strike)

            # calibration date
            cal_vols_c, put_vols_c, maturity_dates_c, spot_c, risk_free_rates_c = daily_svi_dataset.get(to_dt_date(c_date))
            if spot_c > barrier: break
            paramset_c = daily_params.get(to_dt_date(c_date))  # on calibrate_date

            try:
                volSurface_c = SviVolSurface(c_date, paramset_c, daycounter, calendar)
                svi_c = SviPricingModel(volSurface_c, spot_c, daycounter, calendar,
                                       to_ql_dates(maturity_dates_c), ql.Option.Call, contractType)
                black_var_surface_c = svi_c.black_var_surface()
                const_vol_c = estimated_vols.get(to_dt_date(c_date))
            except Exception as e:
                print(e)
                continue
            hist_spots.append(spot_c)

            # hedge date
            evaluation = Evaluation(h_date, daycounter, calendar)
            cal_vols_h, put_vols_h, maturity_dates_h, spot_h, risk_free_rates_h = daily_svi_dataset.get(to_dt_date(h_date))
            underlying.setValue(spot_c) # spot is last day's close price

            process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface_c)
            process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar,underlying, const_vol_c)

            optionprice_svi_h = exotic_util.calculate_barrier_price(evaluation,barrier_option,hist_spots,
                                                                    process_svi_h,engineType)
            optionprice_bs_h = exotic_util.calculate_barrier_price(evaluation, barrier_option, hist_spots,
                                                                    process_bs_h, engineType)
            if optionprice_svi_h == 0.0:
                delta_binomial = 0.0
                delta_bs = 0.0
            else:
                barrierql.setPricingEngine(ql.BinomialBarrierEngine(process_svi_h,'crr',801))
                delta_binomial = barrierql.delta()
                barrierql.setPricingEngine(ql.BinomialBarrierEngine(process_bs_h, 'crr', 801))
                delta_bs = barrierql.delta()
            # Construct replicate portfolio
            cash_svi_h = optionprice_svi_h - delta_binomial * spot_h
            cash_bs_h = optionprice_bs_h - delta_bs*spot_h
            replicate_svi_h = delta_binomial * spot_h + cash_svi_h
            replicate_bs_h = delta_bs * spot_h + cash_bs_h

            # liquidate replication portfolio
            evaluation = Evaluation(l_date, daycounter, calendar)
            cal_vols_l, put_vols_l, maturity_dates_l, spot_l, risk_free_rates_l = daily_svi_dataset.get(to_dt_date(l_date))
            underlying.setValue(spot_h) # spot is last day's close price
            paramset_h = daily_params.get(to_dt_date(h_date))
            try:
                volSurface_h = SviVolSurface(h_date, paramset_h, daycounter, calendar)
                svi_h = SviPricingModel(volSurface_h, spot_h, daycounter, calendar,
                                       to_ql_dates(maturity_dates_l), ql.Option.Call, contractType)
                black_var_surface_h = svi_h.black_var_surface()
                const_vol_h = estimated_vols.get(to_dt_date(h_date))
            except Exception as e:
                print(e)
                continue
            hist_spots.append(spot_h)

            #black_var_surface_h = hedge_util.get_local_volatility_surface(
            # paramset_h, to_ql_dates(maturity_dates_c),
            # c_date, daycounter, calendar, spot_c,risk_free_rates_c)

            process_svi_l = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface_h)
            process_bs_l = evaluation.get_bsmprocess_cnstvol(daycounter,calendar,underlying,const_vol_h)

            #barrierql.setPricingEngine(ql.BinomialBarrierEngine(process_svi_l, 'crr', 801))

            optionprice_svi_l = exotic_util.calculate_barrier_price(evaluation,barrier_option,hist_spots,
                                                                    process_svi_l,engineType)
            optionprice_bs_l = exotic_util.calculate_barrier_price(evaluation, barrier_option, hist_spots,
                                                                    process_bs_l, engineType)
            t = daycounter.yearFraction(h_date, l_date)
            rf = get_rf_tbcurve(h_date,daycounter,maturityDate)
            cash_svi_l = cash_svi_h*math.exp(rf* t)
            cash_bs_l = cash_bs_h*math.exp(rf* t)
            replicate_svi_l = delta_binomial * spot_l + cash_svi_l
            replicate_bs_l = delta_bs * spot_l + cash_bs_l
            hedging_error_bs = replicate_bs_l  - optionprice_bs_l
            hedging_error_svi = replicate_svi_l  - optionprice_svi_l
            hedging_errors_bs.append(hedging_error_bs)
            hedging_errors_svi.append(hedging_error_svi)
            #hedging_costs_bs.append(hedge_cost_bs)
            #hedging_costs_svi.append(hedge_cost_svi)
            if plot: print("%15s %15s %15s %15s %15s %15s %15s %15s" % (l_date,round(spot_l,4),
                            round(hedging_error_bs,4),round(hedging_error_svi,4),
                            round(replicate_bs_l, 4),round(optionprice_bs_l, 4),
                            round(replicate_svi_l, 4),round(optionprice_svi_l, 4)))
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









