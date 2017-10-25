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
    underlyings = {}
    dataset = svidata.dataSet
    for mdate in svidata.dataSet.keys():
        underlyings.update({mdate:dataset.get(mdate).spot})
    maturity_dates = sorted(svidata.dataSet.keys())
    svi = SviPricingModel(volSurface, underlyings, daycounter, calendar,
                            to_ql_dates(maturity_dates), ql.Option.Call, contractType)
    black_var_surface = svi.black_var_surface()
    const_vol = estimated_vols.get(to_dt_date(evalDate))
    return underlyings, black_var_surface, const_vol

with open(os.path.abspath('..')+'/intermediate_data/svi_calibration_sr_calls.pickle','rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/svi_dataset_sr_calls.pickle','rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/bs_estimite_vols_sr_calls.pickle','rb') as f:
    estimated_vols = pickle.load(f)[0]

# Evaluation Settings
begDate = ql.Date(26, 7, 2017)
endDate = ql.Date(25, 8, 2017)
maturitydt = endDate

calendar = ql.China()
daycounter = ql.ActualActual()
begDate = calendar.advance(begDate,ql.Period(1,ql.Days))

fee = 0.2/1000
dt = 1.0/365
rf = 0.03

##############################################################################
results = {}
for strike in range(5650,6950,100):
    print('strike = ',strike)
    optionType = ql.Option.Call
    contractType = 'sr'
    underlyingid = '1801'
    #spot_maturity = datetime.date(2017,12,7)
    spot_maturity = datetime.date(2017, 11, 24)
    euro_option = OptionPlainEuropean(strike,maturitydt,optionType)
    ame_option = OptionPlainAmerican(strike,begDate, maturitydt, optionType)
    optionql = euro_option.option_ql
    ###############################################################################


    svidata = svi_dataset.get(to_dt_date(begDate))
    S0 = svidata.spot
    #maturity_dates = sorted(svidata.dataSet.keys())
    #maturity_date = maturity_dates[1]
    #print('maturity date : ',maturity_date)
    #maturitydt = to_ql_date(maturity_date)
    underlying = ql.SimpleQuote(S0)

    eval_dates = []
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
    underlyings, black_var_surface,const_vol = get_vol_data(evalDate,daycounter,calendar,contractType)

    spot = underlyings.get(spot_maturity)
    underlying.setValue(spot)

    # Contract Hedge Portfolio
    evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
    evaluation = Evaluation(evalDate, daycounter, calendar)

    process_svi = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
    process_bs = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
    engine_svi = ql.BinomialVanillaEngine(process_svi, 'crr', 801)
    engine_bs = ql.BinomialVanillaEngine(process_bs, 'crr', 801)
    optionql.setPricingEngine(engine_svi)
    price_svi = optionql.NPV()
    delta_svi = optionql.delta()
    optionql.setPricingEngine(engine_bs)
    price_bs = optionql.NPV()
    delta_bs = optionql.delta()

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
    cont_spot.append(spot)

    last_delta_svi = delta_svi
    last_delta_bs = delta_bs
    last_price_svi = price_svi
    last_price_bs = price_bs
    last_pnl_svi = 0.0
    last_pnl_bs = 0.0
    last_spot = spot
    #underlyings, black_var_surface,const_vol = get_vol_data(evalDate,daycounter,calendar,contractType)
    #spot = underlyings.get(spot_maturity)
    #underlying.setValue(spot)
    #cont_spot.append(spot)
    # Rebalancing

    while evalDate < endDate:
        evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
        eval_dates.append(to_dt_date(evalDate))
        evaluation = Evaluation(evalDate, daycounter, calendar)
        underlyings, black_var_surface, const_vol = get_vol_data(evalDate, daycounter, calendar, contractType)
        spot = underlyings.get(spot_maturity)
        underlying.setValue(spot)
        #cont_spot.append(spot)
        try:
            get_vol_data(evalDate,daycounter,calendar,contractType)
        except:
            continue
        #print(evalDate, spot)

        process_svi = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
        process_bs = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
        engine_svi = ql.BinomialVanillaEngine(process_svi, 'crr', 801)
        engine_bs = ql.BinomialVanillaEngine(process_bs, 'crr', 801)


        #try:
        if evalDate == endDate:
            price_svi = price_bs = max(0.0,spot-strike)
            delta_svi = delta_bs = 0.0
        else:
            optionql.setPricingEngine(engine_svi)
            price_svi = optionql.NPV()
            delta_svi = optionql.delta()
            optionql.setPricingEngine(engine_bs)
            price_bs = optionql.NPV()
            delta_bs = optionql.delta()

        #except Exception as e:
            #p(e)
            #price_svi = last_price_svi
            #price_bs = last_price_bs
            #delta_svi = last_delta_svi
            #delta_bs = last_delta_bs
        #if evalDate == maturitydt or price_svi == 0.0:
            # 复制组合清仓
         #   delta_svi = 0.0
         #   delta_bs = 0.0
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
        #last_price_svi = price_svi
        #last_price_bs = price_bs


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
        #underlyings, black_var_surface, const_vol = get_vol_data(evalDate, daycounter, calendar, contractType)
        #spot = underlyings.get(spot_maturity)

        #underlying.setValue(spot)
        #cont_spot.append(spot)
    print('strike = ',strike)
    print('cash_svi = ',cash_svi)
    print('cash_bs = ',cash_bs)
    print('price_svi = ', price_svi)
    print('price_bs = ',price_bs)
    print('delta_svi = ',delta_svi)
    print('delta_bs = ',delta_bs)
    print("=" * 120)




    results.update({str(strike)+' svi':cont_pnl_svi})

    results.update({str(strike)+' bs':cont_pnl_bs})
    results.update({str(strike) + ' option price svi': cont_optionprice_svi})
    results.update({str(strike) + ' option price bs': cont_optionprice_bs})

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
results.update({'eval_dates': eval_dates})
results.update({'underlying': cont_spot})
df = pd.DataFrame(data=results)
df.to_csv(contractType+' dailyhedge_european.csv')



















