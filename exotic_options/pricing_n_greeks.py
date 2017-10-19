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


# Evaluation Settings
evalDate = ql.Date(3,8,2017)
endDate1 = ql.Date(28,8,2017)
#endDate1 = ql.Date(11,8,2017)
calendar = ql.China()
daycounter = ql.ActualActual()

fee = 0.6/100
dt = 1.0/365
rf = 0.03
svidata = svi_dataset.get(to_dt_date(evalDate))
S0 = svidata.spot
maturity_dates = sorted(svidata.dataSet.keys())
maturity_date = maturity_dates[1]
print('maturity date : ',maturity_date)
maturitydt = to_ql_date(maturity_date)
#print(maturitydt)
barrier =  2.8
strike =  2.6
optionType = ql.Option.Call
barrierType = ql.Barrier.UpOut
contractType = '50etf'
engineType = 'BinomialBarrierEngine'
barrier_type = 'upout'

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
    barrier_option.setPricingEngine(ql.BinomialBarrierEngine(process, 'crr', 801))
    plain_option.setPricingEngine(ql.BinomialVanillaEngine(process,'crr',801))
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

pu = PlotUtil()
f_delta = pu.get_figure(list(spot_range),[barrier_deltas,plain_deltas],[barrier_type+' barrier call','plain vanilla call'],'spot','Delta')
f_delta.savefig(barrier_type+'-'+str(evalDate)+' delta.png',dpi = 300,format='png')
f_gamma = pu.get_figure(list(spot_range),[barrier_gammas,plain_gammas],[barrier_type+' barrier call','plain vanilla call'],'spot','Gamma')
f_gamma.savefig(barrier_type+'-'+str(evalDate)+' gamma.png',dpi = 300,format='png')
f_price = pu.get_figure(list(spot_range),[barrier_prices,plain_prices],[barrier_type+' barrier call','plain vanilla call'],'spot','Price')
f_price.savefig(barrier_type+'-'+str(evalDate)+' price.png',dpi = 300,format='png')


plt.show()
