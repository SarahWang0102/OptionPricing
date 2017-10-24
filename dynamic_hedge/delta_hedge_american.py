from pricing_options.Options import OptionBarrierEuropean,OptionPlainEuropean,OptionPlainAmerican
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
import pandas as pd

def get_vol_data(evalDate,daycounter,calendar,contractType):
    svidata = svi_dataset.get(to_dt_date(evalDate))
    paramset = calibrered_params_ts.get(to_dt_date(evalDate))
    volSurface = SviVolSurface(evalDate, paramset, daycounter, calendar)
    spot = svidata.spot
    maturity_dates = sorted(svidata.dataSet.keys())
    svi = SviPricingModel(volSurface, spot, daycounter, calendar,
                            to_ql_dates(maturity_dates), ql.Option.Call, contractType)
    black_var_surface = svi.black_var_surface()
    return spot, black_var_surface


with open(os.path.abspath('..')+'/intermediate_data/svi_calibration_m_calls.pickle','rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/svi_dataset_m_calls.pickle','rb') as f:
    svi_dataset = pickle.load(f)[0]

# Evaluation Settings
begDate = ql.Date(26, 7, 2017)
endDate = ql.Date(27, 8, 2017)
maturitydt = endDate

calendar = ql.China()
daycounter = ql.ActualActual()
begDate = calendar.advance(begDate,ql.Period(1,ql.Days))

fee = 0.6/100
dt = 1.0/365
rf = 0.03

strike =  2.7
optionType = ql.Option.Call
contractType = 'm'

euro_option = OptionPlainEuropean(strike,maturitydt,optionType)
ame_option = OptionPlainAmerican(strike,begDate, maturitydt, optionType)
optionql_euro = euro_option.option_ql

svidata = svi_dataset.get(to_dt_date(begDate))
S0 = svidata.spot
maturity_dates = sorted(svidata.dataSet.keys())
maturity_date = maturity_dates[1]
print('maturity date : ',maturity_date)
maturitydt = to_ql_date(maturity_date)
underlying = ql.SimpleQuote(S0)

eval_dates = []
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
cont_cash_svi = []
cont_cash_bs = []
# Calibration
evalDate = begDate
spot, black_var_surface = get_vol_data(evalDate,daycounter,calendar,contractType)
hist_spots.append(spot)
underlying.setValue(spot)

# Contract Hedge Portfolio
evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
evaluation = Evaluation(evalDate, daycounter, calendar)

process = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
engine = ql.BinomialVanillaEngine(process, 'crr', 801)
optionql_euro.setPricingEngine(engine)
price_euro = optionql_euro.NPV()
delta_euro = optionql_euro.delta()

tradingcost_svi = delta_svi*spot*fee
tradingcost_bs = delta_bs*spot*fee
cash_svi = price_svi - delta_svi*spot - tradingcost_svi
cash_bs = price_bs - delta_bs*spot - tradingcost_bs
print('initial barrier option value : ',price_svi,price_bs)
#cash_svi = - delta_svi*spot
#cash_bs = - delta_bs*spot
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
eval_dates.append(to_dt_date(evalDate))
cont_cash_svi.append(cash_svi)
cont_cash_bs.append(cash_bs)
#cont_spot.append(spot)

last_delta_svi = delta_svi
last_delta_bs = delta_bs
last_price_svi = price_svi
last_price_bs = price_bs
last_pnl_svi = 0.0
last_pnl_bs = 0.0
last_spot = spot
spot, black_var_surface, const_vol = get_vol_data(evalDate,daycounter,calendar,contractType) # 收盘价
hist_spots.append(spot)
underlying.setValue(spot)
cont_spot.append(spot)
# Rebalancing
while evalDate < endDate1:
    eval_dates.append(to_dt_date(evalDate))
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
    if evalDate == maturitydt or price_svi == 0.0:
        # 复制组合清仓
        delta_svi = 0.0
        delta_bs = 0.0
        #continue

    cash_svi = cash_svi*math.exp(rf * dt)
    cash_bs = cash_bs*math.exp(rf * dt)
    # 计算对冲误差
    replicate_svi = last_delta_svi*spot + cash_svi
    replicate_bs = last_delta_bs*spot + cash_bs
    #hedgeerror_svi = replicate_svi - price_svi
    #hedgeerror_bs = replicate_bs - price_bs
    #hedgeerror_svi = last_delta_svi*(spot-last_spot) - (price_svi-last_price_svi)
    #hedgeerror_bs = last_delta_bs*(spot-last_spot) - (price_bs-last_price_bs)

    pnl_svi = replicate_svi - price_svi
    pnl_bs = replicate_bs - price_bs
    hedgeerror_svi2 = pnl_svi - last_pnl_svi
    hedgeerror_bs2 = pnl_bs - last_pnl_bs

    last_pnl_svi = pnl_svi
    last_pnl_bs = pnl_bs
    # 调仓
    dholding_svi = delta_svi - last_delta_svi
    dholding_bs = delta_bs - last_delta_bs
    tradingcost_svi = dholding_svi*spot*fee
    tradingcost_bs = dholding_bs*spot*fee

    cash_svi = cash_svi - dholding_svi*spot - tradingcost_svi
    cash_bs = cash_bs - dholding_bs*spot - tradingcost_bs
    replicate_svi = delta_svi*spot + cash_svi
    replicate_bs = delta_bs*spot + cash_bs

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
    cont_hedgeerror_svi.append(hedgeerror_svi2)
    cont_hedgeerror_bs.append(hedgeerror_bs2)
    cont_tradingcost_svi.append(tradingcost_svi)
    cont_tradingcost_bs.append(tradingcost_bs)
    cont_optionprice_svi.append(price_svi)
    cont_optionprice_bs.append(price_bs)
    cont_pnl_svi.append(pnl_svi)
    cont_pnl_bs.append(pnl_bs)


    cont_cash_svi.append(cash_svi)
    cont_cash_bs.append(cash_bs)
    cont_spot.append(spot)
    #last_spot = spot
    spot, black_var_surface, const_vol = get_vol_data(evalDate,daycounter,calendar,contractType)

    hist_spots.append(spot)

    underlying.setValue(spot)
    #cont_spot.append(spot)
print('barrier = ',barrier)
print('strike = ',strike)
print('cash_svi = ',cash_svi)
print('cash_bs = ',cash_bs)
print('price_svi = ', price_svi)
print('price_bs = ',price_bs)
print('delta_svi = ',delta_svi)
print('delta_bs = ',delta_bs)
print("=" * 120)

results = {}
results.update({'0-eval_dates':eval_dates})
results.update({'1-underlying':cont_spot})
results.update({'11-option_price_svi':cont_optionprice_svi})
results.update({'12-delta_svi':cont_delta_svi})
results.update({'13-replicate_svi':cont_replicate_svi})
results.update({'14-holding_change_svi':cont_dholding_svi})
results.update({'15-cash_svi':cont_cash_svi})
results.update({'16-single_pnl_svi':cont_hedgeerror_svi})
results.update({'17-accu_pnl_svi':cont_pnl_svi})

results.update({'18-option_price_bd':cont_optionprice_bs})
results.update({'19-delta_bd':cont_delta_bs})
results.update({'20-replicate_bs':cont_replicate_bs})
results.update({'21-holding_change_bs':cont_dholding_bs})
results.update({'22-cash_bs':cont_cash_bs})
results.update({'23-single_pnl_bs':cont_hedgeerror_bs})
results.update({'24-accu_pnl_bs':cont_pnl_bs})
df = pd.DataFrame(data=results)
df.to_csv('UpOut_dailyhedge.csv')

print("%15s %15s  %15s %15s %15s %15s %15s %15s %15s %15s" % ("evalDate","close","hedgeerror_svi","hedgeerror_bs",
                                                                "delta_svi","delta_bs",
                                                                "optionprice","pnl_svi",
                                                           "pnl_bs",""))
print("-" * 120)
for idx,s in enumerate(cont_spot):
    print("%15s %15s  %15s %15s %15s %15s %15s %15s %15s %15s" % (eval_dates[idx],round(s,4),
                                                       round(cont_hedgeerror_svi[idx],4),
                                                       round(cont_hedgeerror_bs[idx],4),
                                                       round(cont_delta_svi[idx],4),
                                                       round(cont_delta_bs[idx],4),
                                                       round(cont_optionprice_svi[idx],4),
                                                       round(cont_pnl_svi[idx],4),
                                                       round(cont_pnl_bs[idx], 4),
                                                       ''))
print("=" * 120)


print(barrierType)












































































