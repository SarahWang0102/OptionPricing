from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
from pricing_options.Options import OptionPlainEuropean,OptionBarrierEuropean
from pricing_options.OptionEngine import OptionEngine
from pricing_options.Evaluation import Evaluation
from Utilities import utilities as util
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


with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_calls_nobnd.pickle','rb') as f:
    daily_params_c = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_puts.pickle','rb') as f:
    daily_params_p = pickle.load(f)[0]


date = datetime.date(2017,7,17)
date_ql = util.to_ql_date(date)
daycounter = ql.ActualActual()
calendar = ql.China()
evaluation = Evaluation(date_ql,daycounter,calendar)

paramset_c = daily_params_c.get(date)
paramset_p = daily_params_p.get(date)
dataset = daily_svi_dataset.get(date)
cal_vols, put_vols, maturity_dates, underlying, rfs = dataset
index = 3
mdate = maturity_dates[index]
maturitydt = util.to_ql_date(mdate)
print(maturitydt)
params_c = paramset_c[index]
params_p = paramset_p[index]
rf = util.get_rf_tbcurve(date_ql,daycounter,maturitydt)
ttm = daycounter.yearFraction(date_ql,maturitydt)
discount = math.exp(-rf*ttm)

# Example
strike = 2.4
dS = 0.001
iscall = True
curve = get_curve_treasury_bond(date_ql, daycounter)
yield_ts = util.get_yield_ts(date_ql,curve,maturitydt,daycounter)
dividend_ts = util.get_dividend_ts(date_ql,daycounter)
spot_range = np.arange(2.1,2.5,0.0025)
#spot_range = np.arange(2.3,2.7,0.0025)
contractType = '50etf'
engineType = 'AnalyticEuropeanEngine'
barrier_type = 'barrier downout call'

barrier = 2.2
#barrier = 2.6
option_call = OptionPlainEuropean(strike,maturitydt,ql.Option.Call)
optionql_call = option_call.option_ql
barrier_option = OptionBarrierEuropean(strike,maturitydt,ql.Option.Call,barrier,ql.Barrier.DownOut)
barrierql = barrier_option.option_ql
volSurface_call = SviVolSurface(date_ql,paramset_c,daycounter,calendar)
svi_call = SviPricingModel(volSurface_call,underlying,daycounter,calendar,
                           util.to_ql_dates(maturity_dates),ql.Option.Call,contractType)
vol_surface_call = svi_call.black_var_surface()

barrier_prices = []
plain_prices = []
barrier_deltas = []
plain_deltas = []
barrier_gammas = []
plain_gammas = []

underlying_ql = ql.SimpleQuote(0.0)
process = evaluation.get_bsmprocess(daycounter, underlying_ql, vol_surface_call)
for spot in spot_range:
    underlying_ql.setValue(spot)
    optionql_call.setPricingEngine(ql.BinomialVanillaEngine(process,'crr',801))
    barrierql.setPricingEngine(ql.BinomialBarrierEngine(process,'crr',801))
    delta = optionql_call.delta()
    barrierdelta = barrierql.delta()
    gamma = optionql_call.gamma()
    barriergamma = barrierql.gamma()

    barrierprice = barrierql.NPV()
    optionprice = optionql_call.NPV()
    barrier_deltas.append(barrierdelta)
    plain_deltas.append(delta)
    barrier_gammas.append(barriergamma)
    plain_gammas.append(gamma)
    barrier_prices.append(barrierprice)
    plain_prices.append(optionprice)

pu = PlotUtil()
# strike = 2.4, barrier = 2.2/2.6
f_delta = pu.get_figure(list(spot_range),[barrier_deltas,plain_deltas],[barrier_type,'plain vanilla call'],'spot','Delta')
f_delta.savefig(barrier_type+' delta.png',dpi = 300,format='png')
f_gamma = pu.get_figure(list(spot_range),[barrier_gammas,plain_gammas],[barrier_type,'plain vanilla call'],'spot','Gamma')
f_gamma.savefig(barrier_type+' gamma.png',dpi = 300,format='png')
f_price = pu.get_figure(list(spot_range),[barrier_prices,plain_prices],[barrier_type,'plain vanilla call'],'spot','Price')
f_price.savefig(barrier_type+' price.png',dpi = 300,format='png')


plt.show()
