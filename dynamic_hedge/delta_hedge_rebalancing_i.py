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

def calculate_hist_vol(evalDate,calendar,underlyings):
    #start = calendar.advance(evalDate,ql.Period(-1,ql.Months))
    #start = calendar.advance(evalDate, ql.Period(-2, ql.Weeks))
    start = calendar.advance(evalDate, ql.Period(-4, ql.Days))
    #print(start,evalDate)
    yields = []
    while start < evalDate:
        price = underlyings.get(to_dt_date(start))
        t_1 = calendar.advance(start,ql.Period(1,ql.Days))
        price1 = underlyings.get(to_dt_date(t_1))
        r = (price-price1)/price1
        yields.append(r)
        start = calendar.advance(start,ql.Period(1,ql.Days))
    hist_vol = np.std(yields)*np.sqrt(252)
    #print(hist_vol)
    return hist_vol



with open(os.path.abspath('..')+'/intermediate_data/spotclose_i.pickle','rb') as f:
    underlyings = pickle.load(f)[0]

# Evaluation Settings
#begDate = ql.Date(26, 7, 2017)
#endDate = ql.Date(25, 8, 2017)
begDate = ql.Date(31, 7, 2017)
endDate = ql.Date(31, 8, 2017)
maturitydt = endDate

calendar = ql.China()
daycounter = ql.ActualActual()
#begDate = calendar.advance(begDate,ql.Period(1,ql.Days))

fee = 0.2/1000
dt = 1.0/365
rf = 0.03
optionType = ql.Option.Call

##############################################################################
results = {}
for strike in range(500,660,20):
    print('strike = ',strike)

    euro_option = OptionPlainEuropean(strike,maturitydt,optionType)
    ame_option = OptionPlainAmerican(strike,begDate, maturitydt, optionType)
    optionql = ame_option.option_ql

    S0 = underlyings.get(to_dt_date(begDate))
    underlying = ql.SimpleQuote(S0)

    eval_dates = []
    cont_dholding_bs = []
    cont_delta_bs = []
    cont_tradingcost_bs = []
    cont_hedgeerror_bs = []
    cont_replicate_bs = []
    cont_optionprice_bs = []
    cont_spot = []
    cont_pnl_bs = []
    cont_cash_bs = []
    # Calibration
    evalDate = begDate

    spot = S0
    underlying.setValue(spot)

    # Contract Hedge Portfolio
    evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
    evaluation = Evaluation(evalDate, daycounter, calendar)
    const_vol = calculate_hist_vol(evalDate,calendar,underlyings)
    process_bs = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
    engine_bs = ql.BinomialVanillaEngine(process_bs, 'crr', 801)
    optionql.setPricingEngine(engine_bs)
    price_bs = optionql.NPV()
    delta_bs = optionql.delta()

    tradingcost_bs = delta_bs*spot*fee
    cash_bs = price_bs - delta_bs*spot - tradingcost_bs

    replicate_bs = delta_bs*spot + cash_bs

    cont_delta_bs.append(delta_bs)
    cont_dholding_bs.append(delta_bs)
    cont_tradingcost_bs.append(tradingcost_bs)
    cont_replicate_bs.append(replicate_bs)
    cont_optionprice_bs.append(price_bs)
    cont_hedgeerror_bs.append(0.0)
    cont_pnl_bs.append(0.0)
    eval_dates.append(to_dt_date(evalDate))
    cont_cash_bs.append(cash_bs)
    cont_spot.append(spot)

    last_delta_bs = delta_bs
    last_price_bs = price_bs
    last_pnl_svi = 0.0
    last_pnl_bs = 0.0
    last_spot = spot

    while evalDate < endDate:
        evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
        eval_dates.append(to_dt_date(evalDate))
        evaluation = Evaluation(evalDate, daycounter, calendar)
        spot = underlyings.get(to_dt_date(evalDate))
        underlying.setValue(spot)
        const_vol = calculate_hist_vol(evalDate, calendar, underlyings)
        process_bs = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, const_vol)
        engine_bs = ql.BinomialVanillaEngine(process_bs, 'crr', 801)


        #try:
        if evalDate == endDate:
            price_svi = price_bs = max(0.0,spot-strike)
            delta_svi = delta_bs = 0.0
        else:
            optionql.setPricingEngine(engine_bs)
            price_bs = optionql.NPV()
            delta_bs = optionql.delta()


        cash_bs = cash_bs*math.exp(rf * dt)
        # 计算对冲误差
        replicate_bs = last_delta_bs*spot + cash_bs

        pnl_bs = replicate_bs - price_bs
        hedgeerror_bs2 = pnl_bs - last_pnl_bs

        last_pnl_bs = pnl_bs
        # 调仓
        dholding_bs = delta_bs - last_delta_bs
        tradingcost_bs = dholding_bs*spot*fee

        cash_bs = cash_bs - dholding_bs*spot - tradingcost_bs
        replicate_bs = delta_bs*spot + cash_bs

        last_delta_bs = delta_bs


        cont_delta_bs.append(delta_bs)
        cont_dholding_bs.append(delta_bs)
        cont_replicate_bs.append(replicate_bs)
        cont_hedgeerror_bs.append(hedgeerror_bs2)
        cont_tradingcost_bs.append(tradingcost_bs)
        cont_optionprice_bs.append(price_bs)
        cont_pnl_bs.append(pnl_bs)


        cont_cash_bs.append(cash_bs)
        cont_spot.append(spot)
        #last_spot = spot
        #underlyings, black_var_surface, const_vol = get_vol_data(evalDate, daycounter, calendar, contractType)
        #spot = underlyings.get(spot_maturity)

        #underlying.setValue(spot)
        #cont_spot.append(spot)
    #print('strike = ',strike)
    #print('cash_bs = ',cash_bs)
    #print('price_svi = ', price_svi)
    #print('price_bs = ',price_bs)
    #print('delta_bs = ',delta_bs)
    print("=" * 120)





    results.update({str(strike):cont_pnl_bs})
    results.update({str(strike) + ' option price bs': cont_optionprice_bs})
    results.update({'K=' + str(strike) : np.divide(cont_pnl_bs, cont_optionprice_bs[0])})

    print("%15s %15s  %15s %15s %15s %15s %15s " % ("evalDate","close","hedgeerror_bs",
                                                                    "delta_bs",
                                                                    "optionprice",
                                                               "pnl_bs",""))
    print("-" * 120)
    for idx,s in enumerate(cont_spot):
        print("%15s %15s  %15s %15s %15s %15s %15s" % (eval_dates[idx],round(s,4),

                                                           round(cont_hedgeerror_bs[idx],4),

                                                           round(cont_delta_bs[idx],4),
                                                           round(cont_optionprice_bs[idx],4),

                                                           round(cont_pnl_bs[idx], 4),
                                                           ''))
    print("-" * 120)
    print(cont_pnl_bs[-1]/cont_optionprice_bs[0])
    print("=" * 120)
results.update({'eval_dates': eval_dates})
results.update({'underlying': cont_spot})
df = pd.DataFrame(data=results)
df.to_csv('i dailyhedge_american.csv')



















