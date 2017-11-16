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

with open(os.path.abspath('..') + '/intermediate_data/svi_calibration_50etf_calls_noZeroVol.pickle', 'rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/svi_dataset_50etf_calls_noZeroVol.pickle', 'rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/total_hedging_bs_estimated_vols.pickle', 'rb') as f:
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

# def calculate_matrics(evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
#                       black_var_surface,const_vol, engineType,barrier,strike):
#     ttm = daycounter.yearFraction(begDate, maturitydt)
#     # if abs(barrier - spot) < 0.02*spot or abs(strike - spot) < 0.02*spot:
#     if abs(barrier - spot) < 0.02*spot :
#         # print('m')
#         svi_vol = black_var_surface.blackVol(ttm, daily_close)*math.sqrt(daycounter.yearFraction(begDate, maturitydt))
#     else:
#         svi_vol = black_var_surface.blackVol(ttm, daily_close)
#     price_svi, delta_svi = exotic_util.calculate_barrier_price_vol(
#         evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
#         svi_vol, engineType)
#     price_bs, delta_bs = exotic_util.calculate_barrier_price_vol(
#         evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
#         const_vol, engineType)
#     return price_svi, delta_svi,price_bs,delta_bs,svi_vol

def calculate_matrics(evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
                      black_var_surface,const_vol, engineType,barrier,strike):
    ttm = daycounter.yearFraction(begDate, maturitydt)
    svi_vol = black_var_surface.blackVol(ttm, daily_close)
    price_svi, delta_svi = exotic_util.calculate_barrier_price_vol_binomial(
            evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
            svi_vol, engineType)
    price_bs, delta_bs = exotic_util.calculate_barrier_price_vol_binomial(
            evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
            const_vol, engineType)
    delta_svi = max(delta_svi,0.3)
    if abs(barrier - spot) < 0.1 * spot and ttm < 15.0 / 365:
        # print('m')
        delta_svi = max(0.0,delta_svi)
        delta_bs = max(0.0,delta_bs)

    return price_svi, delta_svi,price_bs,delta_bs,svi_vol

def calculate_hedging_positions(spot, option_price, delta, cash, fee,
                                last_delta=0.0, rebalance_cont=0, total_fees=0.0,
                                r=0.0, dt=1.0 / 365):
    tradingcost = abs(delta - last_delta) * spot * fee
    cash += - (delta - last_delta) * spot - tradingcost
    replicate = delta * spot + cash
    portfolio_net = replicate - option_price
    total_fees += -tradingcost
    rebalance_cont += 1
    cash = cash*math.exp(r * dt)
    return tradingcost, cash, portfolio_net, total_fees, rebalance_cont

#######################################################################################################

begin_date = ql.Date(1, 3, 2016)
end_date = ql.Date(1, 6, 2017)
fee = 0.2 / 1000
# dt = 1.0 / 365
rf = 0.03
rf1 = 0.03
barrier_pct = 0.15

optionType = ql.Option.Call
barrierType = ql.Barrier.UpOut
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
calendar = ql.China()
daycounter = ql.ActualActual()

dates = []
svi_pnl = []
bs_pnl = []
transaction_svi = []
transaction_bs = []

print('=' * 200)
print("%20s %20s %20s %20s %20s %20s" % (
    "eval date", 'price_svi', 'price_bs', 'portfolio_svi', 'portfolio_bs',
    'transaction'))
print('=' * 200)
while begin_date < end_date:
    begin_date = calendar.advance(begin_date, ql.Period(2, ql.Days))  # contract effective date
    maturitydt = calendar.advance(begin_date, ql.Period(3, ql.Months))  # contract maturity
    endDate = calendar.advance(maturitydt, ql.Period(-1, ql.Days))  # last hedging date
    svidata = svi_dataset.get(to_dt_date(begin_date))
    strike = svidata.spot
    barrier = strike * (1 + barrier_pct)
    optionBarrierEuropean = OptionBarrierEuropean(strike, maturitydt, optionType, barrier, barrierType)
    barrier_option = optionBarrierEuropean.option_ql
    hist_spots = []

    #######################################################################################################
    # Construct initial rebalancing portfolio
    begDate = begin_date
    evaluation = Evaluation(begDate, daycounter, calendar)
    daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)

    price_svi, price_bs, delta_svi, delta_bs = 0.0, 0.0, 0.0, 0.0

    try:
        price_svi, delta_svi, price_bs, delta_bs, svi_vol = calculate_matrics(
            evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
            black_var_surface, const_vol, engineType, barrier, strike)
    except Exception as e:
        print(e)
        print('initial price unavailable')
    init_svi = price_svi
    init_bs = price_bs
    init_spot = daily_close
    if init_bs==0.0 or init_svi==0.0:continue
    # rebalancing positions
    tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = calculate_hedging_positions(
        daily_close, price_svi, delta_svi,init_svi, fee)
    tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e1 = calculate_hedging_positions(
        daily_close, price_bs, delta_bs,init_bs, fee)

    last_delta_svi = delta_svi
    last_delta_bs = delta_bs
    last_price_svi = price_svi
    last_price_bs = price_bs
    last_s = daily_close
    hist_spots.append(daily_close)

    #######################################################################################################
    # Rebalancing portfolio
    while begDate < endDate:
        # Contruct vol surfave at previous date
        daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
        if daily_close >= barrier:
            print('barrier reached.', barrier, daily_close)
            break
        hist_spots.append(daily_close)
        begDate = calendar.advance(begDate, ql.Period(1, ql.Days))
        daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
        evaluation = Evaluation(begDate, daycounter, calendar)
        marked = daily_close
        datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
        intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_' + datestr + '.json')
        for t in intraday_etf.index:
            s = intraday_etf.loc[t].values[0]

            condition2 =  abs(marked - s) > 0.02*daily_close
            if condition2:  # rebalancing
                if begDate == maturitydt:
                    if s>barrier: price_svi = price_bs = 0.0
                    else: price_svi = price_bs = max(0, s - strike)
                    delta_svi = delta_bs = 0.0
                else:
                    try:

                        price_svi, delta_svi, price_bs, delta_bs, svi_vol = calculate_matrics(
                            evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, s,
                            black_var_surface, const_vol, engineType, barrier, strike)
                    except Exception as e:
                        print(e)
                        print('no npv at ', t)
                        continue

                # rebalancing positions
                tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = \
                    calculate_hedging_positions(
                        daily_close, price_svi, delta_svi, cash_svi, fee,
                        last_delta_svi, rebalance_cont, totalfees_svi
                    )
                tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e1 = \
                    calculate_hedging_positions(
                        daily_close, price_bs, delta_bs, cash_bs, fee,
                        last_delta_bs, rebalance_cont, totalfees_bs)

                last_delta_svi = delta_svi
                last_delta_bs = delta_bs
                last_price_svi = price_svi
                last_price_bs = price_bs
                last_s = s
                marked = s

        # Rebalancing on close price
        if begDate == maturitydt:
            if daily_close > barrier:
                price_svi = price_bs = 0.0
            else:
                price_svi = price_bs = max(0, daily_close - strike)
            delta_svi = delta_bs = 0.0
        else:
            try:

                price_svi, delta_svi, price_bs, delta_bs, svi_vol = calculate_matrics(
                    evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
                    black_var_surface, const_vol, engineType, barrier, strike)
            except Exception as e:
                print(e)
                print('no npv at ', begDate)
                continue
        if cash_svi < 0:
            r = rf1
        else:
            r = rf

        # rebalancing positions
        tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = \
            calculate_hedging_positions(
                daily_close, price_svi, delta_svi, cash_svi, fee,
                last_delta_svi, rebalance_cont, totalfees_svi,r
            )
        tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e2 = \
            calculate_hedging_positions(
                daily_close, price_bs, delta_bs, cash_bs, fee,
                last_delta_bs, rebalance_cont, totalfees_bs,r)

        last_delta_svi = delta_svi
        last_delta_bs = delta_bs
        last_price_svi = price_svi
        last_price_bs = price_bs
        last_s = daily_close

    dates.append(begin_date)
    svi_pnl.append(portfolio_net_svi / init_svi)
    bs_pnl.append(portfolio_net_bs / init_bs)
    transaction_svi.append(totalfees_svi)
    transaction_bs.append(totalfees_bs)
    print("%20s %20s %20s %20s %20s %20s" % (
            begin_date, round(init_svi, 4),round(init_bs, 4),
            round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_bs, 4),
            round(totalfees_svi / init_svi, 4)))
print('=' * 200)
print("%20s %20s %20s %20s %20s %20s %20s %20s" % (
            "eval date", "spot", "delta", 'price_svi','price_bs', 'portfolio_svi', 'portfolio_bs',
            'transaction'))
print('svi_pnl',sum(svi_pnl)/len(svi_pnl))
print('bs_pnl',sum(bs_pnl)/len(bs_pnl))
