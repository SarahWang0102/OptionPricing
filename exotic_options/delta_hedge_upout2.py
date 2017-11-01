import pandas as pd
import numpy as np
import QuantLib as ql
import math
import pickle
import os
from datetime import datetime,date
from Utilities.utilities import *
from pricing_options.Options import OptionBarrierEuropean,OptionPlainEuropean
from pricing_options.Evaluation import Evaluation
from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
import exotic_options.exotic_option_utilities as exotic_util

def get_vol_data(evalDate,daycounter,calendar,contractType):
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


with open(os.path.abspath('..')+'/intermediate_data/svi_calibration_50etf_calls_noZeroVol.pickle','rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/svi_dataset_50etf_calls_noZeroVol.pickle','rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_bs_estimated_vols.pickle','rb') as f:
    estimated_vols = pickle.load(f)[0]

#barrier = 2.615
pct = 0.16
#pct_cont = [0.13,0.14,0.15,0.16,0.17]
pct_cont = [0.08,0.09,0.10,0.11,0.12]
optionType = ql.Option.Call
barrierType = ql.Barrier.UpOut
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
fee = 0.2/1000
#fee = 0.0
dt = 1.0/365
rf = 0.03
rf1 = 0.05
calendar = ql.China()
daycounter = ql.ActualActual()

barriers = []
dates = []
rebalancings = []
pnls_svi = []
pnls_bs = []
results = {}
for pct in pct_cont:
    begin_date = ql.Date(29, 4, 2017)
    begin_date2 = ql.Date(30, 6, 2017)
    print('barrier pct : ',pct)
    #strike = 2.65
    print('='*100)
    print("%15s %20s %20s %20s " % ("begin_date", "rebalencing cont", "svi hedge pnl","bs hedge pnl"))
    #print("%20s %20s %20s %20s %20s %20s %20s %20s" % ("eval date","spot","delta","cash", "option svi", "svi hedge pnl",
    #                                          "bs hedge pnl","replicate svi"))
    print('-'*100)
    #for pct in barrier_cont:
    while begin_date < begin_date2:
        begin_date = calendar.advance(begin_date,ql.Period(1,ql.Days))
        maturitydt = calendar.advance(begin_date,ql.Period(3,ql.Months))
        # Evaluation Settings
        begDate = begin_date
        svidata = svi_dataset.get(to_dt_date(begin_date))
        strike = svidata.spot
        barrier = strike*(1+pct)
        endDate = calendar.advance(maturitydt,ql.Period(-1,ql.Days))
        ################Barrier Option Info#####################
        #print('barrier/strike',barrier/strike)

        optionBarrierEuropean = OptionBarrierEuropean(strike,maturitydt,optionType,barrier,barrierType)
        barrier_option = optionBarrierEuropean.option_ql
        hist_spots = []
        #########################################################
        # construct vol surface on last day's close prices.
        evaluation = Evaluation(begDate, daycounter, calendar)
        daily_close, black_var_surface, const_vol = get_vol_data(begDate,daycounter,calendar,contractType)
        #print('init spot : ',daily_close)
        underlying = ql.SimpleQuote(daily_close)
        process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
        process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
        price_svi, delta_svi = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                                   process_svi_h, engineType)
        price_bs, delta_bs = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                                 process_bs_h, engineType)
        init_svi = price_svi
        init_bs = price_bs
        init_spot = daily_close
        tradingcost_svi = abs(delta_svi)*daily_close*fee
        tradingcost_bs = abs(delta_bs)*daily_close*fee
        cash_svi = price_svi - delta_svi*daily_close - tradingcost_svi
        cash_bs = price_bs - delta_bs*daily_close - tradingcost_bs
        replicate_svi = delta_svi*daily_close + cash_svi
        replicate_bs = delta_bs*daily_close + cash_bs
        init_replicate_svi = replicate_svi
        init_replicate_bs = replicate_bs
        #pnl_svi = replicate_svi - price_svi
        #pnl_bs = replicate_bs - price_bs
        pnl_svi = 0.0
        pnl_bs = 0.0
        last_delta_svi = delta_svi
        last_delta_bs = delta_bs
        last_price_svi = price_svi
        last_price_bs = price_bs
        hist_spots.append(daily_close)
        rebalance_cont = 0

        while begDate < endDate:
            # Contruct vol surfave at previous date
            daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
            if daily_close >= barrier:
                print('barrier reached.',barrier,daily_close)
                break
            hist_spots.append(daily_close)
            begDate = calendar.advance(begDate, ql.Period(1, ql.Days))
            evaluation = Evaluation(begDate, daycounter, calendar)
            marked = daily_close
            balanced = False
            datestr = str(begDate.year()) + "-" + str(begDate.month()) + "-" + str(begDate.dayOfMonth())
            intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_' + datestr + '.json')
            #barrier_close = False
            #print('std : ',np.std(intraday_etf.values))
            for t in intraday_etf.index:
                s = intraday_etf.loc[t].values[0]
                #if abs(barrier-s)<0.005:
                #    barrier_close = True
                #if abs(marked-s)>0.02 or abs(barrier-s)<0.01: # rebalancing
                condition1 = abs(barrier-s)<0.01 and abs(marked-s)>0.0075
                condition2 = abs(barrier-s)>=0.01 and abs(marked-s)>0.015
                #if abs(barrier-s)<0.01 and abs(marked-s)>0.01:
                if condition1 or condition2 :  # rebalancing
                #    barrier_close = False
                    #print(t,s)
                    marked = s
                    #balanced = True
                    underlying.setValue(s)
                    process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
                    process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
                    price_svi, delta_svi = exotic_util.calculate_barrier_price(
                        evaluation, optionBarrierEuropean, hist_spots,process_svi_h, engineType)
                    price_bs, delta_bs = exotic_util.calculate_barrier_price(
                        evaluation, optionBarrierEuropean, hist_spots,process_bs_h, engineType)
                    #print('delta : ',delta_svi,delta_bs)
                    dholding_svi = delta_svi - last_delta_svi
                    dholding_bs = delta_bs - last_delta_bs
                    #print('dholding',dholding_svi,dholding_bs)
                    tradingcost_svi = abs(dholding_svi) * s * fee
                    tradingcost_bs = abs(dholding_bs) * s * fee
                    cash_svi = cash_svi - dholding_svi * s - tradingcost_svi
                    cash_bs = cash_bs - dholding_bs * s - tradingcost_bs
                    replicate_svi = delta_svi * s + cash_svi
                    replicate_bs = delta_bs * s + cash_bs
                    #pnl_svi = replicate_svi - price_svi
                    #pnl_bs = replicate_bs - price_bs
                    pnl_svi += last_delta_svi * (price_svi - last_price_svi) - tradingcost_svi
                    pnl_bs += last_delta_bs * (price_bs - last_price_bs) - tradingcost_bs
                    last_delta_svi = delta_svi
                    last_delta_bs = delta_bs
                    last_price_svi = price_svi
                    last_price_bs = price_bs
                    rebalance_cont += 1
            if not balanced: # rebalancing at close price
                daily_close, black_var_surface, const_vol = get_vol_data(begDate, daycounter, calendar, contractType)
                #print(begDate,'@ close')
                s = daily_close
                underlying.setValue(s)
                process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
                process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
                price_svi, delta_svi = exotic_util.calculate_barrier_price(
                    evaluation, optionBarrierEuropean, hist_spots, process_svi_h, engineType)
                price_bs, delta_bs = exotic_util.calculate_barrier_price(
                    evaluation, optionBarrierEuropean, hist_spots, process_bs_h, engineType)
                #print('delta : ', delta_svi, delta_bs)
                dholding_svi = delta_svi - last_delta_svi
                dholding_bs = delta_bs - last_delta_bs
                if cash_svi < 0: r = rf1
                else: r = rf
                interest_svi = cash_svi*(math.exp(r * dt)-1)
                interest_bs = cash_bs*(math.exp(r * dt)-1)
                tradingcost_svi = abs(dholding_svi)*s*fee
                tradingcost_bs = abs(dholding_bs)*s*fee
                cash_svi = cash_svi-dholding_svi*s-tradingcost_svi
                cash_bs = cash_bs-dholding_bs*s-tradingcost_bs
                replicate_svi = delta_svi * s + cash_svi
                replicate_bs = delta_bs * s + cash_bs
                #pnl_svi = replicate_svi - price_svi
                #pnl_bs = replicate_bs - price_bs

                pnl_svi += last_delta_svi*(price_svi-last_price_svi)-tradingcost_svi+interest_svi
                pnl_bs += last_delta_bs*(price_bs-last_price_bs)-tradingcost_bs+interest_bs
                #pnl_svi = replicate_svi - init_replicate_svi - price_svi + init_svi
                #pnl_bs = replicate_bs - init_replicate_bs - price_bs + init_bs
                last_delta_svi = delta_svi
                last_delta_bs = delta_bs
                last_price_svi = price_svi
                last_price_bs = price_bs
                rebalance_cont += 1
            if cash_svi > 0:
                cash_svi = cash_svi * math.exp(rf * dt)
                cash_bs = cash_bs * math.exp(rf * dt)
            else:
                cash_svi = cash_svi * math.exp(rf1 * dt)
                cash_bs = cash_bs * math.exp(rf1 * dt)
            #print("%20s %20s %20s %20s %20s %20s %20s %20s" % (
            #    begDate, daily_close, delta_svi, cash_svi, price_svi, (pnl_svi- (price_svi - init_svi)) / init_spot,
            #    (pnl_bs-(price_bs - init_bs)) / init_spot, replicate_svi))
        pnl_svi += - (price_svi - init_svi)
        pnl_bs += -(price_bs - init_bs)
        total_return_svi = pnl_svi/init_spot
        total_return_bs = pnl_bs/init_spot
        print("%15s %20s %20s %20s " % (begin_date, rebalance_cont, total_return_svi,total_return_bs))

        barriers.append(pct)
        dates.append(to_dt_date(begin_date))
        rebalancings.append(rebalance_cont)
        pnls_svi.append(total_return_svi)
        pnls_bs.append(total_return_bs)
    print('='*100)
    print('avg pnl svi',np.sum(pnls_svi)/len(pnls_svi))
    print('avg pnl bs',np.sum(pnls_bs)/len(pnls_bs))
    print('='*100)

results.update({'date': dates})
results.update({'barrier': barriers})
results.update({'rebalance cont': rebalancings})
results.update({'pnl svi': pnls_svi})
results.update({'pnl bs': pnls_bs})

df = pd.DataFrame(data=results)
#print(df)
df.to_csv(os.path.abspath('..')+'/results/delta_hedge_upout_8-12.csv')