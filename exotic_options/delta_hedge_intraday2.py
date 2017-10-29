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

# barrier = 2.615

results = {}
barrier_cont = np.arange(2.61, 2.65, 0.005)  # Evaluation Settings
barrier = 2.615
begDate = ql.Date(1, 8, 2017)
endDate = ql.Date(29, 9, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()
fee = 0.2 / 1000
dt = 1.0 / 365
rf = 0.05
svidata = svi_dataset.get(to_dt_date(begDate))
maturity_dates = sorted(svidata.dataSet.keys())
maturity_date = maturity_dates[1]
maturitydt = to_ql_date(maturity_date)
################Barrier Option Info#####################

strike = 2.75
optionType = ql.Option.Call
barrierType = ql.Barrier.DownIn
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
optionBarrierEuropean = OptionBarrierEuropean(strike, maturitydt, optionType, barrier, barrierType)
barrier_option = optionBarrierEuropean.option_ql
hist_spots = []
#########################################################
# construct vol surface on last day's close prices.
evaluation = Evaluation(begDate, daycounter, calendar)
daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
print('init spot : ',daily_close)
underlying = ql.SimpleQuote(daily_close)
process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
price_svi, delta_svi = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                           process_svi_h, engineType)
price_bs, delta_bs = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                         process_bs_h, engineType)
init_svi = price_svi
init_bs = price_bs
tradingcost_svi = delta_svi * daily_close * fee
tradingcost_bs = delta_bs * daily_close * fee
cash_svi = price_svi - delta_svi * daily_close - tradingcost_svi
cash_bs = price_bs - delta_bs * daily_close - tradingcost_bs
replicate_svi = delta_svi * daily_close + cash_svi
replicate_bs = delta_bs * daily_close + cash_bs
last_delta_svi = delta_svi
last_delta_bs = delta_bs
hist_spots.append(daily_close)
rebalance_cont = 0

while begDate < endDate:
    # Contruct vol surfave at previous date
    daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
    print('daily close',daily_close)
    hist_spots.append(daily_close)
    begDate = calendar.advance(begDate, ql.Period(1, ql.Days))
    evaluation = Evaluation(begDate, daycounter, calendar)
    marked = daily_close
    balanced = False
    datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
    intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_' + datestr + '.json')

    for t in intraday_etf.index:
        s = intraday_etf.loc[t].values[0]
        if abs(marked - s) > 0.02 :  # rebalancing
            print('###',t,s,'###')
            marked = s
            balanced = True
            underlying.setValue(s)
            process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
            process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
            price_svi, delta_svi = exotic_util.calculate_barrier_price(
                evaluation, optionBarrierEuropean, hist_spots, process_svi_h, engineType)
            price_bs, delta_bs = exotic_util.calculate_barrier_price(
                evaluation, optionBarrierEuropean, hist_spots, process_bs_h, engineType)
            print('delta : ',delta_svi,delta_bs)
            dholding_svi = delta_svi - last_delta_svi
            dholding_bs = delta_bs - last_delta_bs
            print('dholding',dholding_svi,dholding_bs)
            tradingcost_svi = dholding_svi * s * fee
            tradingcost_bs = dholding_bs * s * fee
            cash_svi = cash_svi - dholding_svi * s - tradingcost_svi
            cash_bs = cash_bs - dholding_bs * s - tradingcost_bs
            replicate_svi = delta_svi * s + cash_svi
            replicate_bs = delta_bs * s + cash_bs
            last_delta_svi = delta_svi
            last_delta_bs = delta_bs
            rebalance_cont += 1
    if not balanced:  # rebalancing at close price
        daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
        print('###',begDate,'@ close',daily_close,'###')
        s = daily_close
        underlying.setValue(s)
        process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
        process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
        price_svi, delta_svi = exotic_util.calculate_barrier_price(
            evaluation, optionBarrierEuropean, hist_spots, process_svi_h, engineType)
        price_bs, delta_bs = exotic_util.calculate_barrier_price(
            evaluation, optionBarrierEuropean, hist_spots, process_bs_h, engineType)
        print('delta : ', delta_svi, delta_bs)
        dholding_svi = delta_svi - last_delta_svi
        dholding_bs = delta_bs - last_delta_bs
        print('dholding', dholding_svi, dholding_bs)
        tradingcost_svi = dholding_svi * s * fee
        tradingcost_bs = dholding_bs * s * fee
        cash_svi = cash_svi - dholding_svi * s - tradingcost_svi
        cash_bs = cash_bs - dholding_bs * s - tradingcost_bs
        replicate_svi = delta_svi * s + cash_svi
        replicate_bs = delta_bs * s + cash_bs
        last_delta_svi = delta_svi
        last_delta_bs = delta_bs
        rebalance_cont += 1
    cash_svi = cash_svi * math.exp(rf * dt)
    cash_bs = cash_bs * math.exp(rf * dt)
    print('cash',cash_svi,cash_bs)
print('=' * 100)
print("%15s %20s %20s %20s " % ("barrier", "rebalencing cont", "svi hedge pnl",
                                "bs hedge pnl"))
print('-' * 100)
print("%15s %20s %20s %20s " % (barrier, rebalance_cont, replicate_svi / init_svi,
                                replicate_bs / init_bs))
print('=' * 100)
