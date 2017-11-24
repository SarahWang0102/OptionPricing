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

with open(os.path.abspath('..') + '/intermediate_data/svi_calibration_50etf_calls_noZeroVol_itd.pickle', 'rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/svi_dataset_50etf_calls_noZeroVol_itd.pickle', 'rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/total_hedging_bs_estimated_vols_call.pickle', 'rb') as f:
    estimated_vols = pickle.load(f)[0]


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


#######################################################################################################
begin_date = ql.Date(12, 3, 2016)
fee = 10.3 / 1000
# dt = 1.0 / 365
rf = 0.03
rf1 = 0.03
barrier_pct = -0.1

optionType = ql.Option.Call
barrierType = ql.Barrier.DownOut
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
calendar = ql.China()
daycounter = ql.ActualActual()
begin_date = calendar.advance(begin_date, ql.Period(1, ql.Days))  # contract effective date
maturitydt = calendar.advance(begin_date, ql.Period(3, ql.Months))  # contract maturity
# endDate = calendar.advance(maturitydt, ql.Period(-1, ql.Days))  # last hedging date

svidata = svi_dataset.get(to_dt_date(begin_date))
strike = svidata.spot
barrier = strike * (1 + barrier_pct)
optionBarrierEuropean = OptionBarrierEuropean(strike, maturitydt, optionType, barrier, barrierType)
barrier_option = optionBarrierEuropean.option_ql

print('barrier : ', barrier)
print('strike  : ', strike)
print('eval date : ', begin_date)
print('=' * 200)
print("%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s" % (
    "eval date", "spot", "svi vol", "bs vol", "delta svi", "delta bs", 'price_svi', 'price_bs', 'svi',
    'bs',
    'transaction','transaction'))
print('-' * 200)

hist_spots = []
barriers = []
dates = []
rebalancings = []
pnls_svi = []
pnls_bs = []
results = {}
#######################################################################################################
# Construct initial rebalancing portfolio
begDate = begin_date
evaluation = Evaluation(begDate, daycounter, calendar)
daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
ttm = daycounter.yearFraction(begDate, maturitydt)
price_svi, price_bs, delta_svi, delta_bs = 0.0, 0.0, 0.0, 0.0
try:

    price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics(
        evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
        black_var_surface, const_vol, engineType, ttm)
except Exception as e:
    print(e)
    print('initial price unavailable')
# init_svi = price_svi
# init_bs = price_bs
init_svi = init_bs = max(price_svi,price_bs)
init_spot = daily_close
# rebalancing positions
tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = exotic_util.calculate_hedging_positions(
    daily_close, price_svi, delta_svi, init_svi, fee)
tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e1 = exotic_util.calculate_hedging_positions(
    daily_close, price_bs, delta_bs, init_bs, fee)



last_delta_svi = delta_svi
last_delta_bs = delta_bs
last_price_svi = price_svi
last_price_bs = price_bs
last_s = daily_close
hist_spots.append(daily_close)

print('init option price, ', 'svi: ', price_svi, 'bs: ', price_bs)
print('-' * 200)
print("%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s" % (
    begDate, round(daily_close, 4), round(svi_vol, 4), round(const_vol, 4), round(delta_svi, 4), round(delta_bs, 4),
    round(price_svi, 4), round(price_bs, 4),
    round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_bs, 4),
    round(totalfees_svi / init_svi, 4)))

#######################################################################################################
# Rebalancing portfolio
marked = daily_close
while begDate < maturitydt:
    daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
    if daily_close <= barrier:
        print('barrier reached.', barrier, daily_close)
        break
    hist_spots.append(daily_close)
    # print(max(hist_spots))
    begDate = calendar.advance(begDate, ql.Period(1, ql.Days))
    if(begDate == maturitydt):
        print('')
    evaluation = Evaluation(begDate, daycounter, calendar)
    ttm = daycounter.yearFraction(begDate, maturitydt)

    datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
    intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_' + datestr + '.json')
    balanced = False
    for t in intraday_etf.index:
        s = intraday_etf.loc[t].values[0]
        condition2 = abs(marked - s) > 0.03 * daily_close
        if condition2:  # rebalancing
            try:
                price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics(
                    evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, s,
                    black_var_surface, const_vol, engineType, ttm)
                balanced = True
            except Exception as e:
                print(e)
                print('no npv at ', t, 'spot : ', s, '; barrier : ', barrier)
                continue
            # rebalancing positions
            tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = \
                exotic_util.calculate_hedging_positions(
                    daily_close, price_svi, delta_svi, cash_svi, fee,
                    last_delta_svi, rebalance_cont, totalfees_svi
                )
            tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e1 = \
                exotic_util.calculate_hedging_positions(
                    daily_close, price_bs, delta_bs, cash_bs, fee,
                    last_delta_bs, rebalance_cont, totalfees_bs)

            last_delta_svi = delta_svi
            last_delta_bs = delta_bs
            last_price_svi = price_svi
            last_price_bs = price_bs
            last_s = s
            marked = s
            print("%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s" % (
                t, round(s, 4), round(svi_vol, 4), round(const_vol, 4), round(delta_svi, 4),
                round(delta_bs, 4), round(price_svi, 4), round(price_bs, 4),
                round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_bs, 4),
                round(totalfees_svi / init_svi, 4),round(totalfees_bs / init_bs, 4)))
    if not balanced:
        try:
            daily_close = intraday_etf.loc[intraday_etf.index[-1]].values[0]
            price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics(
                evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
                black_var_surface, const_vol, engineType, ttm)
            # balanced = True
        except Exception as e:
            print(e)
            print('no npv at ', t, 'spot : ', s, '; barrier : ', barrier)
            continue
        # rebalancing positions
        tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = \
            exotic_util.calculate_hedging_positions(
                daily_close, price_svi, delta_svi, cash_svi, fee,
                last_delta_svi, rebalance_cont, totalfees_svi
            )
        tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e1 = \
            exotic_util.calculate_hedging_positions(
                daily_close, price_bs, delta_bs, cash_bs, fee,
                last_delta_bs, rebalance_cont, totalfees_bs)

        last_delta_svi = delta_svi
        last_delta_bs = delta_bs
        last_price_svi = price_svi
        last_price_bs = price_bs
        last_s = s
        marked = daily_close
        print("%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s" % (
            t, round(s, 4), round(svi_vol, 4), round(const_vol, 4), round(delta_svi, 4),
            round(delta_bs, 4), round(price_svi, 4), round(price_bs, 4),
            round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_bs, 4),
            round(totalfees_svi / init_svi, 4),round(totalfees_bs / init_bs, 4)))

print('=' * 200)
print("%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s" % (
    "eval date", "spot", "svi vol", "bs vol", "delta svi", "delta bs", 'price_svi', 'price_bs', 'portfolio_svi',
    'portfolio_bs',
    'transaction'))
