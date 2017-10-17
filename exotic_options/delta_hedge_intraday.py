import pandas as pd
import QuantLib as ql
import math
import pickle
import os
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
intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_2017-08-28' + '.json')
#print(intraday_etf)
timestamps = list(intraday_etf.index)

evalDate = ql.Date(28,8,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
lastDate = calendar.advance(evalDate,ql.Period(-1,ql.Days))

fee = 0.6/100
dt = 1.0/365
rf = 0.03
#c, p, maturity_dates, S0, r = daily_svi_dataset.get(to_dt_date(begDate))
maturitydt = ql.Date(27,9,2017)
#print(maturitydt)
barrier =  2.81
strike =  2.75
cash_svi =  0.04621701830367859
cash_bs =  0.03427679513349334
price_svi =  0.0010942761186805224
price_bs =  0.0007716880768042928
delta_svi =  -0.016135143611148525
delta_bs =  -0.01207675453899006
#print(S0)

optionType = ql.Option.Call
barrierType = ql.Barrier.UpOut
contractType = '50etf'
engineType = 'BinomialBarrierEngine'

evaluation = Evaluation(evalDate, daycounter, calendar)


optionBarrierEuropean = OptionBarrierEuropean(strike,maturitydt,optionType,barrier,barrierType)
barrier_option = optionBarrierEuropean.option_ql


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
# 开盘拟合曲线
spot, black_var_surface, const_vol = get_vol_data(lastDate,daycounter,calendar,contractType)
#s, x, const_vol = get_vol_data(lastDate,daycounter,calendar,contractType)
ttm = daycounter.yearFraction(evalDate, maturitydt)
Ft = spot * math.exp(rf*ttm)
moneyness = math.log(strike/Ft, math.e)
print(const_vol)
print(moneyness)
hist_spots.append(spot)
underlying = ql.SimpleQuote(spot)


# Contract Hedge Portfolio
process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
#price_svi, delta_svi = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
#                                                           process_svi_h, engineType)
#price_bs, delta_bs = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
#                                                         process_bs_h, engineType)


#print('initial barrier option value : ',price_svi,price_bs)


last_delta_svi = delta_svi
last_delta_bs = delta_bs
last_price_svi = price_svi
last_price_bs = price_bs
last_pnl_svi = 0.0
last_pnl_bs = 0.0
last_spot = spot

cont_delta_svi.append(delta_svi)
cont_delta_bs.append(delta_bs)
cont_dholding_svi.append(delta_svi)
cont_dholding_bs.append(delta_bs)
cont_tradingcost_svi.append(0.0)
cont_tradingcost_bs.append(0.0)
cont_replicate_svi.append(0.0)
cont_replicate_bs.append(0.0)
cont_optionprice_svi.append(price_svi)
cont_optionprice_bs.append(price_bs)
cont_hedgeerror_svi.append(0.0)
cont_hedgeerror_bs.append(0.0)
cont_pnl_svi.append(last_pnl_svi)
cont_pnl_bs.append(last_pnl_bs)
eval_dates.append('2017-8-28 开盘')
cont_cash_svi.append(cash_svi)
cont_cash_bs.append(cash_bs)

hist_spots.append(spot)
cont_spot.append(spot)

ttm = daycounter.yearFraction(evalDate,maturitydt)
print(black_var_surface.blackVol(ttm,strike))
# Rebalancing

#for idx,spotlist in enumerate(intraday_etf.values):
for idx in range(len(intraday_etf.values)):
    spot = intraday_etf.values[idx][0]
    underlying.setValue(spot)
    process_svi_h = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
    process_bs_h = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)

    barrier_option.setPricingEngine(ql.BinomialBarrierEngine(process_svi_h, 'crr', 801))
    barrier_option.setPricingEngine(ql.BinomialBarrierEngine(process_bs_h, 'crr', 801))
    try:
        price_svi, delta_svi = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                                   process_svi_h, engineType)
        price_bs, delta_bs = exotic_util.calculate_barrier_price(evaluation, optionBarrierEuropean, hist_spots,
                                                                 process_bs_h, engineType)
    except Exception as e:
        # p(e)
        price_svi = last_price_svi
        price_bs = last_price_bs
        delta_svi = last_delta_svi
        delta_bs = last_delta_bs
    if evalDate == maturitydt or price_svi == 0.0:
        # 复制组合清仓
        delta_svi = 0.0
        delta_bs = 0.0
        # continue

    #cash_svi = cash_svi * math.exp(rf * dt)
    #cash_bs = cash_bs * math.exp(rf * dt)
    # 计算对冲误差
    replicate_svi = last_delta_svi * spot + cash_svi
    replicate_bs = last_delta_bs * spot + cash_bs
    # hedgeerror_svi = replicate_svi - price_svi
    # hedgeerror_bs = replicate_bs - price_bs
    #hedgeerror_svi = last_delta_svi * (spot - last_spot) - (price_svi - last_price_svi)
    #hedgeerror_bs = last_delta_bs * (spot - last_spot) - (price_bs - last_price_bs)
    pnl_svi = replicate_svi - price_svi
    pnl_bs = replicate_bs - price_bs
    hedgeerror_svi2 = pnl_svi - last_pnl_svi
    hedgeerror_bs2 = pnl_bs - last_pnl_bs

    last_pnl_svi = pnl_svi
    last_pnl_bs = pnl_bs
    # 调仓
    dholding_svi = delta_svi - last_delta_svi
    dholding_bs = delta_bs - last_delta_bs
    tradingcost_svi = dholding_svi * spot * fee
    tradingcost_bs = dholding_bs * spot * fee

    cash_svi = cash_svi - dholding_svi * spot - tradingcost_svi
    cash_bs = cash_bs - dholding_bs * spot - tradingcost_bs
    replicate_svi = delta_svi * spot + cash_svi
    replicate_bs = delta_bs * spot + cash_bs

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
    cont_spot.append(spot)
    eval_dates.append(intraday_etf.index[idx])
    cont_cash_svi.append(cash_svi)
    cont_cash_bs.append(cash_bs)
    #last_spot = spot

    hist_spots.append(spot)

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
df.to_csv('UpOut_intradayhedge.csv')


print("=" * 120)
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
