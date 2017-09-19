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
simDates = 50
np.random.seed()
noise = np.random.normal(0, 1, simDates)

curve = svi_data.get_curve_treasury_bond(begDate,daycounter)
cal_vols, put_vols, maturity_dates, S0, risk_free_rates = daily_svi_dataset.get(to_dt_date(begDate))
maturityDate = to_ql_date(maturity_dates[3])

# Down and out Call
optiontype = ql.Option.Call

strike = S0
# Knock out : Barrier at OTM
barriers = [S0-0.1]
barrierType = ql.Barrier.DownOut
# Reverse knock out : Barrier at ATM
#barriers = [S0+0.1]
#barrierType = ql.Barrier.IpOut

exercise = ql.EuropeanExercise(maturityDate)
payoff = ql.PlainVanillaPayoff(optiontype, strike)
underlying = ql.SimpleQuote(S0)

calibrated_params = daily_params.get(to_dt_date(begDate))  # on calibrate_date
black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params, to_ql_dates(maturity_dates),
                                                            begDate, daycounter, calendar, S0,
                                                            risk_free_rates)
const_vol = estimated_vols.get(to_dt_date(begDate))
yield_ts = ql.YieldTermStructureHandle(curve)
dividend = ql.YieldTermStructureHandle(ql.FlatForward(begDate, 0.0, daycounter))
rf = curve.zeroRate(maturityDate, daycounter, ql.Continuous).rate()
process_svi = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying), dividend,
                                             yield_ts, ql.BlackVolTermStructureHandle(black_var_surface))
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
    path = []
    delta_t = 1.0/251
    spot = S0
    ttm = daycounter.yearFraction(begDate, maturityDate)
    vol_svi = black_var_surface.blackVol(ttm, strike)
    underlying.setValue(spot)
    option_price = exotic_util.barrier_npv_ql(begDate, path, barrierType, barrier, payoff, exercise,
                                              process_svi)
    for nbr_date in range(simDates):
        date = calendar.advance(begDate,ql.Period(nbr_date,ql.Days))
        # Delta hedge
        if option_price == 0.0:
            delta_bs = 0.0
            delta_svi = 0.0
        else:
            delta_bs = hedge_util.calculate_delta_bs(date, daycounter, calendar,
                                                     const_vol, spot, rf, strike, maturityDate, optiontype)
            delta_svi = hedge_util.calculate_delta_svi(black_var_surface, date, daycounter, calendar, spot,
                                                       curve.zeroRate(maturityDate, daycounter, ql.Continuous).rate(),
                                                       strike, maturityDate, optiontype)
        underlying.setValue(spot)
        option_price = exotic_util.barrier_npv_ql(begDate, path, barrierType, barrier, payoff, exercise,
                                                  process_svi)
        path.append(spot)

        spot = spot + rf * spot * delta_t + vol_svi * spot * np.sqrt(delta_t) * noise.item(nbr_date)
        cash_svi = (option_price - delta_svi * spot)* math.exp(rf* delta_t)
        cash_bs = (option_price - delta_bs * spot)* math.exp(rf* delta_t)
        replicate_svi = delta_svi * spot + cash_svi
        replicate_bs = delta_bs * spot + cash_bs
        hedging_error_bs = replicate_bs - option_price
        hedging_error_svi = replicate_svi - option_price
        hedging_errors_bs.append(hedging_error_bs)
        hedging_errors_svi.append(hedging_error_svi)
        # hedging_costs_bs.append(hedge_cost_bs)
        # hedging_costs_svi.append(hedge_cost_svi)
        if plot: print("%15s %15s %15s %15s %15s %15s %15s" % (date,
                                                               round(spot, 4),
                                                               round(hedging_error_bs, 4),
                                                               round(hedging_error_svi, 4),
                                                               round(replicate_bs, 4),
                                                               round(replicate_svi, 4),
                                                               round(option_price, 4)))

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
