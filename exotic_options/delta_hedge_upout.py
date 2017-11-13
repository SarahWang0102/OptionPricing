import pandas as pd
import numpy as np
import QuantLib as ql
import math
import pickle
import os
from datetime import datetime, date
from Utilities.utilities import *
from pricing_options.Options import OptionBarrierEuropean, OptionPlainEuropean
from pricing_options.Evaluation import Evaluation
from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
import exotic_options.exotic_option_utilities as exotic_util


def get_vol_data(evalDate, daycounter, calendar, contractType):
    svidata = svi_dataset.get(to_dt_date(evalDate))
    paramset = calibrered_params_ts.get(to_dt_date(evalDate))
    volSurface = SviVolSurface(evalDate, paramset, daycounter, calendar)
    spot = svidata.spot
    maturity_dates = sorted(svidata.dataSet.keys())
    svi = SviPricingModel(volSurface, spot, daycounter, calendar,
                          to_ql_dates(maturity_dates), ql.Option.Call, contractType)
    black_var_surface = svi.black_var_surface()
    const_vol = estimated_vols.get(to_dt_date(evalDate))
    return spot, black_var_surface, const_vol



with open(os.path.abspath('..') + '/intermediate_data/svi_calibration_50etf_calls_noZeroVol.pickle', 'rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/svi_dataset_50etf_calls_noZeroVol.pickle', 'rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/total_hedging_bs_estimated_vols.pickle', 'rb') as f:
    estimated_vols = pickle.load(f)[0]

pct = 0.15
optionType = ql.Option.Call
barrierType = ql.Barrier.UpOut
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
fee = 0.2 / 1000
# fee = 0.0
dt = 1.0 / 365
rf = 0.03
rf1 = 0.03
calendar = ql.China()
daycounter = ql.ActualActual()

barriers = []
dates = []
rebalancings = []
pnls_svi = []
pnls_bs = []
results = {}
totalfees_svi = 0.0
begin_date = ql.Date(15, 5, 2016)
# begin_date = ql.Date(15, 6, 2017)
print('barrier pct : ', pct)
print('=' * 100)
# print("%15s %20s %20s %20s " % ("begin_date", "rebalencing cont", "svi hedge pnl", "bs hedge pnl"))
print("%20s %20s %20s %20s %20s %20s %20s %20s %20s %20s" % (
    "eval date", "spot", "delta", "vol", 'price_svi', 'portfolio_svi', 'portfolio_bs',
    "svi hedge pnl", "bs hedge pnl", 'transaction'))
print('-' * 100)
# for pct in barrier_cont:
begin_date = calendar.advance(begin_date, ql.Period(1, ql.Days))
maturitydt = calendar.advance(begin_date, ql.Period(3, ql.Months))
# Evaluation Settings
begDate = begin_date
svidata = svi_dataset.get(to_dt_date(begin_date))
strike = svidata.spot
barrier = strike * (1 + pct)
endDate = calendar.advance(maturitydt, ql.Period(-1, ql.Days))

################Barrier Option Info#####################

optionBarrierEuropean = OptionBarrierEuropean(strike, maturitydt, optionType, barrier, barrierType)
barrier_option = optionBarrierEuropean.option_ql
hist_spots = []
#########################################################
# construct vol surface on last day's close prices.
evaluation = Evaluation(begDate, daycounter, calendar)
daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
underlying = ql.SimpleQuote(daily_close)
y = daycounter.yearFraction(begDate, maturitydt)
x = daily_close
svi_vol = black_var_surface.blackVol(y,x)
process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)

price_bs, delta_bs = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                         process_bs_h, engineType)
try:
    # price_svi, delta_svi = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
    #                                                            process_svi_h, engineType)
    price_svi, delta_svi = exotic_util.calculate_barrier_price_vol(
        evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
        svi_vol, engineType)
except:
    print('initial price unavailable')

init_svi = price_svi
init_bs = price_bs
init_spot = daily_close
tradingcost_svi = abs(delta_svi) * daily_close * fee
tradingcost_bs = abs(delta_bs) * daily_close * fee
cash_svi = price_svi - delta_svi * daily_close - tradingcost_svi
cash_bs = price_bs - delta_bs * daily_close - tradingcost_bs
replicate_svi = delta_svi * daily_close + cash_svi
replicate_bs = delta_bs * daily_close + cash_bs
# init_replicate_svi = replicate_svi
# init_replicate_bs = replicate_bs
pnl_svi = 0.0
pnl_bs = 0.0
last_delta_svi = delta_svi
last_delta_bs = delta_bs
last_price_svi = price_svi
last_price_bs = price_bs
last_s = daily_close
totalfees_svi += -tradingcost_svi
hist_spots.append(daily_close)
rebalance_cont = 0
portfolio_net_svi = replicate_svi - price_svi
portfolio_net_bs = replicate_bs - price_bs
print('barrier  : ', barrier)
print('strike  : ', strike)
print('init option price, ', 'svi: ', price_svi, 'bs: ', price_bs)
print('replicate svi : ', replicate_svi)
print('-' * 100)
print("%20s %20s %20s %20s %20s %20s %20s %20s %20s %20s" % (
    begDate, round(daily_close, 4), round(delta_svi, 4), 0.0, round(price_svi, 4),
    round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_svi, 4), round(pnl_svi / init_svi, 4),
    round(pnl_bs / init_svi, 4), round(totalfees_svi / init_svi, 4)))
while begDate <= endDate:
    # Contruct vol surfave at previous date
    daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
    if daily_close >= barrier:
        print('barrier reached.', barrier, daily_close)
        break
    hist_spots.append(daily_close)
    begDate = calendar.advance(begDate, ql.Period(1, ql.Days))
    evaluation = Evaluation(begDate, daycounter, calendar)
    marked = daily_close
    datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
    intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_' + datestr + '.json')
    for t in intraday_etf.index:
        s = intraday_etf.loc[t].values[0]
        condition1 = abs(barrier - s) < 0.02 and abs(marked - s) > 0.004
        # condition2 = abs(barrier - s) >= 0.02 and abs(marked - s) > 0.004
        if condition1:  # rebalancing
            # print('balanced, ',begDate,t,s)
            underlying.setValue(s)
            y = daycounter.yearFraction(begDate, maturitydt)
            x = s
            svi_vol = black_var_surface.blackVol(y, x)
            # process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
            # process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
            try:
                # price_svi, delta_svi = exotic_util.calculate_barrier_price(
                #     evaluation, optionBarrierEuropean, hist_spots, process_svi_h, engineType)
                price_svi, delta_svi = exotic_util.calculate_barrier_price_vol(
                    evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, s,
                    svi_vol, engineType)
            except:
                print('NO NPV')
                continue
                # price_svi = last_price_svi
                # delta_svi = last_delta_svi

            price_bs, delta_bs = exotic_util.calculate_barrier_price(
                evaluation, optionBarrierEuropean, hist_spots, process_bs_h, engineType)
            # dholding_svi = delta_svi - last_delta_svi
            # dholding_bs = delta_bs - last_delta_bs
            tradingcost_svi = abs(delta_svi - last_delta_svi) * s * fee
            tradingcost_bs = abs(delta_bs - last_delta_bs) * s * fee
            cash_svi += - (delta_svi - last_delta_svi) * s - tradingcost_svi
            cash_bs += - (delta_bs - last_delta_bs) * s - tradingcost_bs
            replicate_svi = delta_svi * s + cash_svi
            replicate_bs = delta_bs * s + cash_bs
            pnl_svi += last_delta_svi * (s - last_s) - tradingcost_svi
            pnl_bs += last_delta_bs * (s - last_s) - tradingcost_bs
            pnl_svi += - (price_svi - last_price_svi)
            pnl_bs += -(price_bs - last_price_bs)
            portfolio_net_svi = replicate_svi - price_svi
            portfolio_net_bs = replicate_bs - price_bs

            last_delta_svi = delta_svi
            last_delta_bs = delta_bs
            last_price_svi = price_svi
            last_price_bs = price_bs
            last_s = s
            totalfees_svi += -tradingcost_svi
            rebalance_cont += 1
            marked = s

            print("%20s %20s %20s %20s %20s %20s %20s %20s %20s %20s" % (
                t, round(s, 4), round(delta_svi, 4), round(svi_vol, 4), round(price_svi, 4),
                round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_svi, 4),
                round(pnl_svi / init_svi, 4),
                round(pnl_bs / init_svi, 4), round(totalfees_svi / init_svi, 4)))

    daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
    s = daily_close
    underlying.setValue(s)
    process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
    process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
    y = daycounter.yearFraction(begDate, maturitydt)
    x = daily_close
    svi_vol = black_var_surface.blackVol(y, x)
    if begDate == maturitydt:
        price_svi = price_bs = max(0, s - strike)
        delta_svi = delta_bs = 0.0
    else:
        try:
            # price_svi, delta_svi = exotic_util.calculate_barrier_price(
            #     evaluation, optionBarrierEuropean, hist_spots, process_svi_h, engineType)
            price_svi, delta_svi = exotic_util.calculate_barrier_price_vol(
                evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, s,
                svi_vol, engineType)
        except:
            print('NO NPV')
            price_svi = last_price_svi
            delta_svi = last_delta_svi
        price_bs, delta_bs = exotic_util.calculate_barrier_price(
            evaluation, optionBarrierEuropean, hist_spots, process_bs_h, engineType)
    dholding_svi = delta_svi - last_delta_svi
    dholding_bs = delta_bs - last_delta_bs
    if cash_svi < 0:
        r = rf1
    else:
        r = rf

    interest_svi = cash_svi * (math.exp(r * dt) - 1)
    interest_bs = cash_bs * (math.exp(r * dt) - 1)
    tradingcost_svi = abs(dholding_svi) * s * fee
    tradingcost_bs = abs(dholding_bs) * s * fee
    cash_svi = cash_svi - dholding_svi * s - tradingcost_svi
    cash_bs = cash_bs - dholding_bs * s - tradingcost_bs
    replicate_svi = delta_svi * s + cash_svi
    replicate_bs = delta_bs * s + cash_bs

    pnl_svi += last_delta_svi * (s - last_s) - tradingcost_svi + interest_svi
    pnl_bs += last_delta_bs * (s - last_s) - tradingcost_bs + interest_bs
    pnl_svi += - (price_svi - last_price_svi)
    pnl_bs += -(price_bs - last_price_bs)
    portfolio_net_svi = replicate_svi - price_svi
    portfolio_net_bs = replicate_bs - price_bs
    last_delta_svi = delta_svi
    last_delta_bs = delta_bs
    last_price_svi = price_svi
    last_price_bs = price_bs
    last_s = daily_close
    rebalance_cont += 1
    totalfees_svi += -tradingcost_svi

    if cash_svi > 0:
        cash_svi = cash_svi * math.exp(rf * dt)
        cash_bs = cash_bs * math.exp(rf * dt)
    else:
        cash_svi = cash_svi * math.exp(rf1 * dt)
        cash_bs = cash_bs * math.exp(rf1 * dt)

    print("%20s %20s %20s %20s %20s %20s %20s %20s %20s %20s" % (
        begDate, round(daily_close, 4), round(delta_svi, 4), round(svi_vol, 4), round(price_svi, 4),
        round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_svi, 4), round(pnl_svi / init_svi, 4),
        round(pnl_bs / init_svi, 4), round(totalfees_svi / init_svi, 4)))
    # print("%15s %20s %20s %20s " % (begin_date, rebalance_cont, total_return_svi, total_return_bs))
print('=' * 100)
print("%20s %20s %20s %20s %20s %20s %20s %20s %20s %20s" % (
    "eval date", "spot", "delta", "vol", 'price_svi', 'portfolio_svi', 'portfolio_bs',
    "svi hedge pnl", "bs hedge pnl", 'transaction'))
