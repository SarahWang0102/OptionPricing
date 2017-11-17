from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
from pricing_options.Options import OptionPlainEuropean,OptionBarrierEuropean
from pricing_options.OptionEngine import OptionEngine
import exotic_options.exotic_option_utilities as exotic_util
from pricing_options.Evaluation import Evaluation
from Utilities.utilities import *
from Utilities.PlotUtil import PlotUtil
from Utilities.svi_read_data import get_curve_treasury_bond
import matplotlib.pyplot as plt
import QuantLib as ql
import pandas as pd
import numpy as np
import math
import datetime
import os
import pickle



with open(os.path.abspath('..')+'/intermediate_data/svi_calibration_50etf_calls_noZeroVol.pickle','rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/svi_dataset_50etf_calls_noZeroVol.pickle','rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_bs_estimated_vols.pickle','rb') as f:
    estimated_vols = pickle.load(f)[0]

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


pu = PlotUtil()
# Evaluation Settings
evalDate = ql.Date(3,8,2017)
# endDate1 = ql.Date(28,8,2017)
#endDate1 = ql.Date(11,8,2017)
calendar = ql.China()
daycounter = ql.ActualActual()

fee = 0.6/100
dt = 1.0/365
rf = 0.03
svidata = svi_dataset.get(to_dt_date(evalDate))
S0 = svidata.spot
maturity_dates = sorted(svidata.dataSet.keys())
maturitydt = calendar.advance(evalDate,ql.Period(3,ql.Months))
print('maturity date : ',maturitydt)
# maturitydt = to_ql_date(maturity_date)
#print(maturitydt)
barrier =  2.8
# barrier =  2.6
strike =  2.6
optionType = ql.Option.Call
barrierType = ql.Barrier.UpIn
# optionType = ql.Option.Put
# barrierType = ql.Barrier.DownOut
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
# barrier_type = 'upout'
barrier_type = 'upin'

evaluation = Evaluation(evalDate,daycounter,calendar)
spot, black_var_surface, const_vol = get_vol_data(evalDate,daycounter,calendar,contractType) # 收盘价
optionBarrierEuropean = OptionBarrierEuropean(strike,maturitydt,optionType,barrier,barrierType)
barrier_option = optionBarrierEuropean.option_ql
option_call = OptionPlainEuropean(strike,maturitydt,ql.Option.Call)
plain_option = option_call.option_ql
underlying = ql.SimpleQuote(S0)
spot_range = np.arange(min(strike,barrier)-0.1,max(strike,barrier)+0.05,0.0005)


barrier_prices = []
plain_prices = []
barrier_deltas = []
plain_deltas = []
barrier_gammas = []
plain_gammas = []


for spot in spot_range:
    underlying.setValue(spot)
    process = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
    barrier_option.setPricingEngine(ql.BinomialBarrierEngine(process, 'crr', 400))
    plain_option.setPricingEngine(ql.BinomialVanillaEngine(process,'crr',400))
    delta = plain_option.delta()
    barrierdelta = barrier_option.delta()
    gamma = plain_option.gamma()
    barriergamma = barrier_option.gamma()
    barrierprice = barrier_option.NPV()
    optionprice = plain_option.NPV()
    barrier_deltas.append(barrierdelta)
    plain_deltas.append(delta)
    barrier_gammas.append(barriergamma)
    plain_gammas.append(gamma)
    barrier_prices.append(barrierprice)
    plain_prices.append(optionprice)

f_delta = pu.get_figure(list(spot_range),[barrier_deltas,plain_deltas],[barrier_type+' barrier call','plain vanilla call'],'spot','Delta')
f_delta.savefig(os.path.abspath('..') + '/results/'+barrier_type+'- delta.png',dpi = 300,format='png')
f_gamma = pu.get_figure(list(spot_range),[barrier_gammas,plain_gammas],[barrier_type+' barrier call','plain vanilla call'],'spot','Gamma')
f_gamma.savefig(os.path.abspath('..') + '/results/'+barrier_type+'- gamma.png',dpi = 300,format='png')
f_price = pu.get_figure(list(spot_range),[barrier_prices,plain_prices],[barrier_type+' barrier call','plain vanilla call'],'spot','Price')
f_price.savefig(os.path.abspath('..') + '/results/'+barrier_type+'- price.png',dpi = 300,format='png')



maturities = []
maturities.append(calendar.advance(evalDate,ql.Period(1,ql.Months)))
maturities.append(calendar.advance(evalDate,ql.Period(1,ql.Weeks)))
maturities.append(calendar.advance(evalDate,ql.Period(2,ql.Days)))
maturities.append(calendar.advance(evalDate,ql.Period(1,ql.Days)))

lgds = ['1月到期','1周到期','2天到期','1天到期']
# lgds = ['1周到期','2天到期','1天到期']
# delta_maturities = {}
ff, axx = plt.subplots()
ff1, axx1 = plt.subplots()
# ff2, axx2 = plt.subplots()
# ff3, axx3 = plt.subplots()
for cont in range(len(maturities)):
    maturitydt = maturities[cont]
    optionBarrierEuropean = OptionBarrierEuropean(strike, maturitydt, optionType, barrier, barrierType)
    barrier_option = optionBarrierEuropean.option_ql
    deltas = []
    gammas = []
    vegas = []
    tdeltas = []
    for spot in spot_range:
        underlying.setValue(spot)
        vol = black_var_surface.blackVol(daycounter.yearFraction(evalDate, maturitydt),spot)
        # process = evaluation.get_bsmprocess(daycounter, underlying, black_var_surface)
        process = evaluation.get_bsmprocess_cnstvol(daycounter,calendar,underlying,vol)
        barrier_option.setPricingEngine(ql.BinomialBarrierEngine(process, 'crr', 400))
        delta = barrier_option.delta()
        gamma = barrier_option.gamma()
        deltas.append(delta)
        gammas.append(gamma)
        # price = barrier_option.NPV()
        # vol2 = black_var_surface.blackVol(daycounter.yearFraction(evalDate, maturitydt),spot+0.1)
        # process2 = evaluation.get_bsmprocess_cnstvol(daycounter,calendar,underlying,vol2)
        # barrier_option.setPricingEngine(ql.BinomialBarrierEngine(process2, 'crr', 800))
        # price2 = barrier_option.NPV()
        # vega = (price2-price)/(vol2-vol)
        # dsigma_ds = (vol2-vol)/0.1
        # print(vol,vol2,vega,dsigma_ds)
        # vegas.append(vega)
        # tdeltas.append(delta+vega*dsigma_ds)
    # delta_maturities.update({maturitydt:deltas})
    t = daycounter.yearFraction(evalDate,maturitydt)
    pu.plot_line(axx,cont,list(spot_range),deltas,lgds[cont],'spot','Delta')
    pu.plot_line(axx1,cont,list(spot_range),gammas,lgds[cont],'spot','Gamma')
    # pu.plot_line(axx2,cont,list(spot_range),vegas,lgds[cont],'spot','Vega')
    # pu.plot_line(axx3,cont,list(spot_range),tdeltas,lgds[cont],'spot','Total Delta')
# axx = pu.set_frame([axx])[0]
# pu.plot_line(axx,cont+1,[barrier*1.01]*len(spot_range),np.arange(-2,10,12/len(spot_range)),'','spot','Delta')
# maxd = 10
# mind = -2
maxd = 8.5
mind = 0
rate = -0.01
x = np.arange(barrier*(1+rate),barrier,-barrier*rate/100)
axx.plot([barrier*(1+rate)]*len(spot_range),np.arange(mind,maxd,(maxd-mind)/len(spot_range)), color=pu.c6, linestyle='--', linewidth=1)
axx.plot([barrier+0.001]*len(spot_range),np.arange(mind,maxd,(maxd-mind)/len(spot_range)), color=pu.c6, linestyle='--', linewidth=1)
axx.plot(x,[mind]*len(x), color=pu.c6, linestyle='--', linewidth=1)
axx.plot(x,[maxd]*len(x), color=pu.c6, linestyle='--', linewidth=1)

plt.show()
ff.savefig(os.path.abspath('..') + '/results/'+barrier_type+'-'+'maturities deltas.png',dpi = 300,format='png')
ff1.savefig(os.path.abspath('..') + '/results/'+barrier_type+'-'+'maturities gammas.png',dpi = 300,format='png')
