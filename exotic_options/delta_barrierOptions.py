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
#spot_range = np.arange(2,3.5,0.05)
spot_range = np.arange(2.3,2.7,0.0025)
contractType = '50etf'
engineType = 'AnalyticEuropeanEngine'
barrier_type = 'barrier upout call'

print('strike = ',strike,', option type : call')
print('='*100)
print("%10s %25s %25s %25s %25s %25s" % ("Spot","barrier_delta","european_delta","delta_total","delta_eff","diff"))
print('-'*100)
#barrier = 2.2
barrier = 2.6
option_call = OptionPlainEuropean(strike,maturitydt,ql.Option.Call)
optionql_call = option_call.option_ql
barrier_option = OptionBarrierEuropean(strike,maturitydt,ql.Option.Call,barrier,ql.Barrier.UpOut)
barrierql = barrier_option.option_ql
volSurface_call = SviVolSurface(date_ql,paramset_c,daycounter,calendar)
svi_call = SviPricingModel(volSurface_call,underlying,daycounter,calendar,
                           util.to_ql_dates(maturity_dates),ql.Option.Call,contractType)
vol_surface_call = svi_call.black_var_surface()

call_delta_total = []
call_delta_cnst = []
call_delta_eff = []
call_diff = []
call_barrierdelta = []
#index=['data_total','data_const']
result = pd.DataFrame()
underlying_ql = ql.SimpleQuote(0.0)
process = evaluation.get_bsmprocess(daycounter, underlying_ql, vol_surface_call)
for spot in spot_range:
    underlying_ql.setValue(spot)
    #engine = OptionEngine(process, engineType).engine
    optionql_call.setPricingEngine(ql.BinomialVanillaEngine(process,'crr',801))
    barrierql.setPricingEngine(ql.BinomialBarrierEngine(process,'crr',801))
    delta = optionql_call.delta()
    barrierdelta = barrierql.delta()
    # 全Delta
    delta_total = svi_call.calculate_total_delta(evaluation,option_call,engineType,spot,spot*0.0001)
    # Effective Delta
    delta_eff = svi_call.calculate_effective_delta(evaluation,option_call,engineType,spot, dS)

    delta1 = round(delta, 4)
    barrierdelta1 = round(barrierdelta,4)
    delta_t1 = round(delta_total, 4)
    delta_eff1 = round(delta_eff, 4)
    call_barrierdelta.append(barrierdelta)
    call_delta_total.append(delta_total)
    call_delta_cnst.append(delta)
    call_delta_eff.append(delta_eff)
    call_diff.append(delta_total-delta)
    print("%10s %25s %25s %25s %25s %25s" % (spot,barrierdelta1,delta1,delta_t1,delta_eff1,round(delta_total-delta,4)))
print('='*100)
result['Spot'] = spot_range
result['Barrier_Delta_Call'] = call_barrierdelta
result['TotalDelta_m_call'] = call_delta_total
result['EffectiveDelta_m_call'] = call_delta_eff
result['TotalDelta_k_call'] = call_delta_cnst

pu = PlotUtil()
# strike = 2.4, barrier = 2.2/2.6
f = pu.get_figure(list(spot_range),[call_barrierdelta,call_delta_cnst],[barrier_type,'plain vanilla call'],'spot','Delta')
plt.show()
f.savefig(barrier_type+'.png',dpi = 300,format='png')
#result.to_csv('delta_barrier_do.csv')