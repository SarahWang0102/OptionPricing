from pricing_options.Options import OptionBarrierEuropean, OptionPlainEuropean, OptionPlainAmerican
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
from scipy import stats
import numpy as np
import matplotlib.pyplot as plt
import Utilities.plot_util as pu
import math
import pandas as pd


def get_vol_data(evalDate, daycounter, calendar, contractType):
    svidata = svi_dataset.get(to_dt_date(evalDate))
    paramset = calibrered_params_ts.get(to_dt_date(evalDate))
    volSurface = SviVolSurface(evalDate, paramset, daycounter, calendar)
    underlyings = {}
    dataset = svidata.dataSet
    for mdate in svidata.dataSet.keys():
        underlyings.update({mdate: dataset.get(mdate).spot})
    maturity_dates = sorted(svidata.dataSet.keys())
    svi = SviPricingModel(volSurface, underlyings, daycounter, calendar,
                          to_ql_dates(maturity_dates), ql.Option.Call, contractType)
    black_var_surface = svi.black_var_surface()
    const_vol = estimated_vols.get(to_dt_date(evalDate))
    return underlyings, black_var_surface, const_vol


with open(os.path.abspath('..') + '/intermediate_data/svi_calibration_m_calls.pickle', 'rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/svi_dataset_m_calls.pickle', 'rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/bs_estimite_vols_m_calls.pickle', 'rb') as f:
    estimated_vols = pickle.load(f)[0]

#######################################################################################################
period = ql.Period(1, ql.Days)
rebalancerate = 0.03
fee = 0.3 / 1000
rf = 0.03
rf1 = 0.06
# **************#
begin_date = ql.Date(1, 4, 2017)
end_date = ql.Date(30, 6, 2017)
dt = 1.0 / 365
calendar = ql.China()
daycounter = ql.ActualActual()
optionType = ql.Option.Call
contractType = 'm'
engine_ame = 'BinomialEngine'
engine_euro = 'BinomialEngine'
#######################################################################################################


dates = []
option_init_svi = []
option_init_bs = []
svi_pnl = []
bs_pnl = []
transaction_svi = []
transaction_bs = []
holdings_svi = []
holdings_bs = []

print('=' * 200)
print("%20s %20s %20s %20s %20s %20s" % (
    "eval date", 'price_svi', 'price_bs', 'portfolio_svi', 'portfolio_bs',
    'transaction'))
print('=' * 200)
while begin_date < end_date:
    hist_spots = []
    deltacont_svi = []
    deltacont_bs = []
    tradedvalue_svi = 0.0
    tradedvalue_bs = 0.0
    begin_date = calendar.advance(begin_date, period)
    maturitydt = calendar.advance(begin_date, ql.Period(3, ql.Months))
    svidata = svi_dataset.get(to_dt_date(begin_date))
    underlyings, black_var_surface, const_vol = get_vol_data(begin_date, daycounter, calendar, contractType)

    begDate = begin_date
    # print(begDate)
    evaluation = Evaluation(begDate, daycounter, calendar)
    datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
    intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_m_' + datestr + '.json')
    daily_close = intraday_etf.loc[intraday_etf.index[-1]].values[0]
    daily_close = daily_close*1.0
    strike = daily_close
    # print(strike)
    euro_option = OptionPlainEuropean(strike, maturitydt, optionType)
    ame_option = OptionPlainAmerican(strike, begin_date, maturitydt, optionType)

    try:
        ttm = daycounter.yearFraction(begDate, maturitydt)
        price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics_plain(
            evaluation, daycounter, calendar, euro_option, hist_spots, daily_close,
            black_var_surface, const_vol, engine_euro, ttm)
    except Exception as e:
        print(e)
        print('initial price unavailable')

    init_svi = price_svi
    init_bs = price_bs
    init_spot = daily_close
    # init_svi = init_bs = max(price_bs, price_svi)
    if init_svi <= 0.001 or init_bs <= 0.001: continue
    # rebalancing positions
    tradingcost_svi, cash_svi, portfolio_net_svi, totalfees_svi, rebalance_cont = \
        exotic_util.calculate_hedging_positions(daily_close, price_svi, delta_svi, init_svi, fee)
    tradingcost_bs, cash_bs, portfolio_net_bs, totalfees_bs, e1 = \
        exotic_util.calculate_hedging_positions(daily_close, price_bs, delta_bs, init_bs, fee)
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
    marked = daily_close

    while begDate < maturitydt:
        underlyings, black_var_surface, const_vol = get_vol_data(begin_date, daycounter, calendar, contractType)
        begDate = calendar.advance(begDate, ql.Period(1, ql.Days))
        evaluation = Evaluation(begDate, daycounter, calendar)
        ttm = daycounter.yearFraction(begDate, maturitydt)

        datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
        intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_m_' + datestr + '.json')
        balanced = False
        for t in intraday_etf.index:
            s = intraday_etf.loc[t].values[0]*1.0
            condition2 = abs(marked - s) > rebalancerate * daily_close
            if condition2:  # rebalancing
                try:
                    price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics_plain(
                        evaluation, daycounter, calendar, euro_option, hist_spots, daily_close,
                        black_var_surface, const_vol, engine_euro, ttm)
                    balanced = True
                except Exception as e:
                    print(e)
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
        if not balanced:
            try:
                daily_close = intraday_etf.loc[intraday_etf.index[-1]].values[0]*1.0
                price_svi, delta_svi, price_bs, delta_bs, svi_vol = exotic_util.calculate_matrics_plain(
                    evaluation, daycounter, calendar, euro_option, hist_spots, daily_close,
                    black_var_surface, const_vol, engine_euro, ttm)
                # balanced = True
            except Exception as e:
                print(e)
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
            last_s = daily_close
            marked = daily_close
        if cash_svi < 0:
            r = rf1
        else:
            r = rf
        cash_svi = cash_svi * math.exp(r * dt)
        cash_bs = cash_bs * math.exp(r * dt)

    dates.append(begin_date)
    svi_pnl.append(portfolio_net_svi / init_svi)
    bs_pnl.append(portfolio_net_bs / init_bs)
    transaction_svi.append(tradedvalue_svi)
    transaction_bs.append(tradedvalue_bs)
    holdings_svi.append(sum(deltacont_svi) / len(deltacont_svi))
    holdings_bs.append(sum(deltacont_bs) / len(deltacont_bs))
    option_init_bs.append(init_bs)
    option_init_svi.append(init_svi)
    print("%20s %20s %20s %20s %20s %20s %20s" % (
        begin_date, round(init_svi, 4), round(init_bs, 4),
        round(portfolio_net_svi / init_svi, 4), round(portfolio_net_bs / init_bs, 4),
        round(tradedvalue_svi / init_svi, 4), round(tradedvalue_bs / init_bs, 4)))
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
df.to_csv(os.path.abspath('..') + '/results/dh_plain_'+contractType + '_r=' + str(rebalancerate)  + '.csv')

t, p = stats.ttest_ind(svi_pnl, bs_pnl)

print(t, p)