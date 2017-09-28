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

with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_calls_nobnd.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..') + '/intermediate_data/total_hedging_dates_calls_nobnd.pickle', 'rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_svi_dataset_calls_nobnd.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_bs_estimated_vols.pickle','rb') as f:
    estimated_vols = pickle.load(f)[0]

def get_vol_data(evalDate,daycounter,calendar,contractType):
    cal_vols, put_vols, maturity_dates, spot, risk_free_rates = daily_svi_dataset.get(to_dt_date(evalDate))
    paramset = daily_params.get(to_dt_date(evalDate))
    volSurface = SviVolSurface(evalDate, paramset, daycounter, calendar)
    svi = SviPricingModel(volSurface, spot, daycounter, calendar,
                            to_ql_dates(maturity_dates), ql.Option.Call, contractType)
    black_var_surface = svi.black_var_surface()
    const_vol = estimated_vols.get(to_dt_date(evalDate))
    return spot, black_var_surface, const_vol


# Evaluation Settings
begDate = ql.Date(19,1,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
begDate = calendar.advance(begDate,ql.Period(1,ql.Days))

fee = 0.6/100
dt = 1.0/365
rf = 0.03
c, p, maturity_dates, S0, r = daily_svi_dataset.get(to_dt_date(begDate))
maturity_date = maturity_dates[3]
maturitydt = to_ql_date(maturity_date)
print(maturitydt)
strike = S0
print(S0)
barrier = 2.33
optionType = ql.Option.Call
barrierType = ql.Barrier.DownIn
contractType = '50etf'
engineType = 'BinomialBarrierEngine'

optionBarrierEuropean = OptionBarrierEuropean(strike,maturitydt,optionType,barrier,barrierType)
barrier_option = optionBarrierEuropean.option_ql
underlying = ql.SimpleQuote(S0)

hist_spots = []
cont_dholding_svi = []
cont_dholding_bs = []
cont_delta_svi = []
cont_delta_bs = []
cont_tradingcost_svi = []
cont_tradingcost_bs = []
cont_hedgeerror_svi = []
cont_hedgeerror_bs = []
cont_replicate_svi = []
cont_replicate_bs = []
cont_optionprice_svi = []
cont_optionprice_bs = []
cont_spot = []
cont_pnl_svi = []
cont_pnl_bs = []
# Calibration
evalDate = begDate
spot, black_var_surface, const_vol = get_vol_data(evalDate,daycounter,calendar,contractType)
hist_spots.append(spot)
underlying.setValue(spot)

# Contract Hedge Portfolio
evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
evaluation = Evaluation(evalDate, daycounter, calendar)

process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
price_svi, delta_svi = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                           process_svi_h, engineType)
price_bs, delta_bs = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                         process_bs_h, engineType)


tradingcost_svi = delta_svi*spot*fee
tradingcost_bs = delta_bs*spot*fee
#cash_svi = price_svi - delta_svi*spot
#cash_bs = price_bs - delta_bs*spot
print('initial barrier option value : ',price_svi,price_bs)
cash_svi = - delta_svi*spot
cash_bs = - delta_bs*spot
replicate_svi = delta_svi*spot + cash_svi
replicate_bs = delta_bs*spot + cash_bs

cont_delta_svi.append(delta_svi)
cont_delta_bs.append(delta_bs)
cont_dholding_svi.append(delta_svi)
cont_dholding_bs.append(delta_bs)
cont_tradingcost_svi.append(tradingcost_svi)
cont_tradingcost_bs.append(tradingcost_bs)
cont_replicate_svi.append(replicate_svi)
cont_replicate_bs.append(replicate_bs)
cont_optionprice_svi.append(price_svi)
cont_optionprice_bs.append(price_bs)
cont_hedgeerror_svi.append(0.0)
cont_hedgeerror_bs.append(0.0)
cont_pnl_svi.append(0.0)
cont_pnl_bs.append(0.0)
#cont_spot.append(spot)

last_delta_svi = delta_svi
last_delta_bs = delta_bs
last_price_svi = price_svi
last_price_bs = price_bs
last_spot = spot
spot, black_var_surface, const_vol = get_vol_data(evalDate,daycounter,calendar,contractType) # 收盘价
hist_spots.append(spot)
underlying.setValue(spot)
cont_spot.append(spot)
# Rebalancing
while evalDate < maturitydt:

    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    try:
        get_vol_data(evalDate,daycounter,calendar,contractType)
    except:
        continue
    #print(evalDate, spot)
    evaluation = Evaluation(evalDate, daycounter, calendar)
    process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
    process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
    barrier_option.setPricingEngine(ql.BinomialBarrierEngine(process_svi_h, 'crr', 801))
    barrier_option.setPricingEngine(ql.BinomialBarrierEngine(process_bs_h, 'crr', 801))
    try:
        price_svi,delta_svi = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                                process_svi_h, engineType)
        price_bs,delta_bs = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                               process_bs_h, engineType)
    except Exception as e:
        #p(e)
        price_svi = last_price_svi
        price_bs = last_price_bs
        delta_svi = last_delta_svi
        delta_bs = last_delta_bs
    #if evalDate == maturitydt or price_svi == 0.0:
        # 复制组合清仓
        #continue

    cash_svi = cash_svi*math.exp(rf * dt)
    cash_bs = cash_bs*math.exp(rf * dt)
    # 计算对冲误差
    replicate_svi = last_delta_svi*spot + cash_svi
    replicate_bs = last_delta_bs*spot + cash_bs
    #hedgeerror_svi = replicate_svi - price_svi
    #hedgeerror_bs = replicate_bs - price_bs
    hedgeerror_svi = last_delta_svi*(spot-last_spot) - (price_svi-last_price_svi)
    hedgeerror_bs = last_delta_bs*(spot-last_spot) - (price_bs-last_price_bs)

    pnl_svi = replicate_svi - price_svi
    pnl_bs = replicate_bs - price_bs

    # 调仓
    dholding_svi = delta_svi - last_delta_svi
    dholding_bs = delta_bs - last_delta_bs
    cash_svi = cash_svi - dholding_svi*spot
    cash_bs = cash_bs - dholding_bs*spot
    replicate_svi = delta_svi*spot + cash_svi
    replicate_bs = delta_bs*spot + cash_bs
    tradingcost_svi = dholding_svi*spot*fee
    tradingcost_bs = dholding_bs*spot*fee

    last_delta_svi = delta_svi
    last_delta_bs = delta_bs
    last_price_svi = price_svi
    last_price_bs = price_bs


    cont_delta_svi.append(delta_svi)
    cont_delta_bs.append(delta_bs)
    cont_dholding_svi.append(delta_svi)
    cont_dholding_bs.append(delta_bs)
    cont_replicate_svi.append(replicate_svi)
    cont_replicate_bs.append(replicate_bs)
    cont_hedgeerror_svi.append(hedgeerror_svi)
    cont_hedgeerror_bs.append(hedgeerror_bs)
    cont_tradingcost_svi.append(tradingcost_svi)
    cont_tradingcost_bs.append(tradingcost_bs)
    cont_optionprice_svi.append(price_svi)
    cont_optionprice_bs.append(price_bs)
    cont_pnl_svi.append(pnl_svi)
    cont_pnl_bs.append(pnl_bs)
    #cont_spot.append(spot)

    last_spot = spot
    spot, black_var_surface, const_vol = get_vol_data(evalDate,daycounter,calendar,contractType)
    hist_spots.append(spot)
    underlying.setValue(spot)
    cont_spot.append(spot)
print("=" * 120)
print("%15s %15s %15s %15s %15s %15s %15s %15s %15s" % ("spot","hedgeerror_svi","hedgeerror_bs",
                                                                "delta_svi","delta_bs",
                                                                "optionprice","pnl_svi",
                                                           "pnl_bs",""))
print("-" * 120)
for idx,s in enumerate(cont_spot):
    print("%15s %15s %15s %15s %15s %15s %15s %15s %15s" % (round(s,4),
                                                       round(cont_hedgeerror_svi[idx],4),
                                                       round(cont_hedgeerror_bs[idx],4),
                                                       round(cont_delta_svi[idx],4),
                                                       round(cont_delta_bs[idx],4),
                                                       round(cont_optionprice_svi[idx],4),
                                                       round(cont_pnl_svi[idx],4),
                                                       round(cont_pnl_bs[idx], 4),
                                                       ''))
print("=" * 120)















































































