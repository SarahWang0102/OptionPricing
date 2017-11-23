import pandas as pd
import numpy as np
import QuantLib as ql
import math
import pickle
import os
from datetime import datetime, date
from scipy import stats
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
    return black_var_surface, const_vol



#######################################################################################################

begin_date = ql.Date(1, 9, 2015)
end_date = ql.Date(30, 6, 2017)
fee = 0.2 / 1000
# dt = 1.0 / 365
rf = 0.0
rf1 = 0.03
barrier_pct = -0.15
dt = 1.0/365

optionType = ql.Option.Call
barrierType = ql.Barrier.DownIn
barrier_type = 'downincall'
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
calendar = ql.China()
daycounter = ql.ActualActual()

dates = []
option_init_svi = []
option_init_bs = []
svi_pnl = []
bs_pnl = []
transaction_svi = []
transaction_bs = []
holdings_svi = []
holdings_bs =[]
tradedvalue_svi = 0.0
tradedvalue_bs = 0.0
print('=' * 200)
print("%20s %20s %20s %20s %20s %20s" % (
    "eval date", 'price_svi', 'price_bs', 'portfolio_svi', 'portfolio_bs',
    'transaction'))
print('=' * 200)
while begin_date < end_date:
    begin_date = calendar.advance(begin_date, ql.Period(1, ql.Days))  # contract effective date
    maturitydt = calendar.advance(begin_date, ql.Period(3, ql.Months))  # contract maturity
    endDate = calendar.advance(maturitydt, ql.Period(-1, ql.Days))  # last hedging date
    svidata = svi_dataset.get(to_dt_date(begin_date))
    strike = svidata.spot
    barrier = strike * (1 + barrier_pct)
    optionBarrierEuropean = OptionBarrierEuropean(strike, maturitydt, optionType, barrier, barrierType)
    barrier_option = optionBarrierEuropean.option_ql
    hist_spots = []
    deltacont_svi = []
    deltacont_bs = []
    #######################################################################################################
    # Construct initial rebalancing portfolio
    begDate = begin_date
    evaluation = Evaluation(begDate, daycounter, calendar)
    black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
    datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
    intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_' + datestr + '.json')
    daily_close = intraday_etf.loc[intraday_etf.index[-1]].values[0]
    price_svi, price_bs, delta_svi, delta_bs = 0.0, 0.0, 0.0, 0.0

    try:
        ttm = daycounter.yearFraction(begDate, maturitydt)
        price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics(
            evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
            black_var_surface, const_vol, engineType,ttm)
    except Exception as e:
        print(e)
        print('initial price unavailable')
    # init_svi = price_svi
    # init_bs = price_bs
    init_svi = init_bs = max(price_bs, price_svi)
    init_spot = daily_close

    if init_svi <= 0.001 or init_bs <= 0.001 :
        # print('init <= 0.005 ', init_svi,init_bs)
        # init_svi = init_bs = 0.001
        continue
    # if init_bs < 0.001 or init_svi < 0.001: continue
    # rebalancing positions
    tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = exotic_util.calculate_hedging_positions(
        daily_close, price_svi, delta_svi, init_svi, fee)
    tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e1 = exotic_util.calculate_hedging_positions(
        daily_close, price_bs, delta_bs, init_bs, fee)
    tradedvalue_svi += abs(delta_svi) * daily_close
    tradedvalue_bs += abs(delta_bs) * daily_close
    deltacont_svi.append(abs(delta_svi))
    deltacont_bs.append(abs(delta_bs))
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
        black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
        # if daily_close >= barrier:
        #     print('barrier reached.', barrier, daily_close)
        #     break
        datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
        intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_' + datestr + '.json')
        daily_close = intraday_etf.loc[intraday_etf.index[-1]].values[0]
        hist_spots.append(daily_close)
        hist_spots.append(daily_close)
        begDate = calendar.advance(begDate, ql.Period(1, ql.Days))
        # black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
        evaluation = Evaluation(begDate, daycounter, calendar)
        ttm = daycounter.yearFraction(begDate, maturitydt)
        marked = daily_close
        datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
        intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_' + datestr + '.json')
        for t in intraday_etf.index:
            s = intraday_etf.loc[t].values[0]

            condition2 = abs(marked - s) > 0.04*daily_close
            if condition2:  # rebalancing
                # if begDate == maturitydt:
                #     if s > barrier:
                #         price_svi = price_bs = 0.0
                #     else:
                #         price_svi = price_bs = max(0, s - strike)
                #     delta_svi = delta_bs = 0.0
                # else:
                try:

                    price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics(
                            evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, s,
                            black_var_surface, const_vol, engineType,ttm)
                except Exception as e:
                    print(e)
                    print('no npv at ', t,'spot : ',s,'; barrier : ',barrier)
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
                tradedvalue_svi += abs(delta_svi) * daily_close
                tradedvalue_bs += abs(delta_bs) * daily_close
                deltacont_svi.append(abs(delta_svi))
                deltacont_bs.append(abs(delta_bs))
                last_delta_svi = delta_svi
                last_delta_bs = delta_bs
                last_price_svi = price_svi
                last_price_bs = price_bs
                last_s = s
                marked = s

        # Rebalancing on close price
        # if begDate == maturitydt:
        #     if daily_close > barrier:
        #         price_svi = price_bs = 0.0
        #     else:
        #         price_svi = price_bs = max(0, daily_close - strike)
        #     delta_svi = delta_bs = 0.0
        # else:
        # try:
        #
        #     price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics(
        #             evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
        #             black_var_surface, const_vol, engineType,ttm)
        # except Exception as e:
        #     print(e)
        #     print('no npv at ', begDate)
        #     continue
        if cash_svi < 0:
            r = rf1
        else:
            r = rf
        cash_svi = cash_svi * math.exp(r * dt)
        cash_bs = cash_bs * math.exp(r * dt)

        # rebalancing positions
        # tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = \
        #     exotic_util.calculate_hedging_positions(
        #         daily_close, price_svi, delta_svi, cash_svi, fee,
        #         last_delta_svi, rebalance_cont, totalfees_svi, r
        #     )
        # tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e2 = \
        #     exotic_util.calculate_hedging_positions(
        #         daily_close, price_bs, delta_bs, cash_bs, fee,
        #         last_delta_bs, rebalance_cont, totalfees_bs, r)
        #
        # last_delta_svi = delta_svi
        # last_delta_bs = delta_bs
        # last_price_svi = price_svi
        # last_price_bs = price_bs
        # last_s = daily_close
        # marked = daily_close

    dates.append(begin_date)
    svi_pnl.append(portfolio_net_svi / init_svi)
    bs_pnl.append(portfolio_net_bs / init_bs)
    transaction_svi.append(tradedvalue_svi)
    transaction_bs.append(tradedvalue_bs)
    holdings_svi.append(sum(deltacont_svi) / len(deltacont_svi))
    holdings_bs.append(sum(deltacont_bs) / len(deltacont_bs))
    option_init_bs.append(init_bs)
    option_init_svi.append(init_svi)
    print("%20s %20s %20s %20s %20s %20s" % (
        begin_date, round(init_svi, 4), round(init_bs, 4),
        round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_bs, 4),
        round(totalfees_svi / init_svi, 4)))
print('=' * 200)
print("%20s %20s %20s %20s %20s %20s %20s %20s" % (
    "eval date", "spot", "delta", 'price_svi', 'price_bs', 'portfolio_svi', 'portfolio_bs',
    'transaction'))
print('svi_pnl', sum(svi_pnl) / len(svi_pnl))
print('bs_pnl', sum(bs_pnl) / len(bs_pnl))
results = {}
results.update({'date': dates})
results.update({'pnl svi': svi_pnl})
results.update({'pnl bs': bs_pnl})
results.update({'option init svi': option_init_svi})
results.update({'option init bs': option_init_bs})
results.update({'transaction svi': transaction_svi})
results.update({'transaction bs': transaction_bs})
results.update({'holdings svi': holdings_svi})
results.update({'holdings bs': holdings_bs})

df = pd.DataFrame(data=results)
# print(df)
df.to_csv(os.path.abspath('..') + '/results/t2_delta_hedge_'+barrier_type+'b='+str(barrier_pct*100)+'.csv')

t,p = stats.ttest_ind(svi_pnl,bs_pnl)
print(t,p)