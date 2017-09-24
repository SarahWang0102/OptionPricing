from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
from pricing_options.OptionPlainVanilla import OptionPlainVanilla
from pricing_options.OptionEngine import OptionEngine
from pricing_options.Evaluation import Evaluation
from Utilities import utilities as util
from Utilities.svi_read_data import get_curve_treasury_bond
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
evaluation = Evaluation(date_ql)

daycounter = ql.ActualActual()
calendar = ql.China()


paramset_c = daily_params_c.get(date)
paramset_p = daily_params_p.get(date)
dataset = daily_svi_dataset.get(date)
cal_vols, put_vols, maturity_dates, underlying, rfs = dataset
index = 3
mdate = maturity_dates[index]
maturitydt = util.to_ql_date(mdate)
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
spot_range = np.arange(2,3.5,0.025)
contractType = '50etf'
engineType = 'AnalyticEuropeanEngine'

print('strike = ',strike,', option type : call')
print('='*100)
print("%10s %25s %25s %25s %25s" % ("Spot","delta_total","delta_eff","delta_constant_vol ","diff"))
print('-'*100)

option_call = OptionPlainVanilla(strike,maturitydt,ql.Option.Call).get_european_option()

volSurface_call = SviVolSurface(date_ql,paramset_c,daycounter,calendar)
svi_call = SviPricingModel(volSurface_call,underlying,daycounter,calendar,
                           util.to_ql_dates(maturity_dates),ql.Option.Call,contractType)
vol_surface_call = svi_call.black_var_surface()

call_delta_total = []
call_delta_cnst = []
call_delta_eff = []
call_diff = []
#index=['data_total','data_const']
result = pd.DataFrame()
underlying_ql = ql.SimpleQuote(0.0)
process = evaluation.get_bsmprocess(daycounter, underlying_ql, vol_surface_call)
for spot in spot_range:
    underlying_ql.setValue(spot)
    engine = OptionEngine(process, engineType).engine
    option_call.setPricingEngine(engine)
    delta = option_call.delta()
    # 全Delta
    delta_total = svi_call.calculate_total_delta(evaluation,option_call,engineType,spot,strike,maturitydt,spot*0.0001)
    # Effective Delta
    delta_eff = svi_call.calculate_effective_delta(evaluation,option_call,engineType,spot, dS)

    delta1 = round(delta, 4)
    delta_t1 = round(delta_total, 4)
    delta_eff1 = round(delta_eff, 4)
    call_delta_total.append(delta_total)
    call_delta_cnst.append(delta)
    call_delta_eff.append(delta_eff)
    call_diff.append(delta_total-delta)
    print("%10s %25s %25s %25s %25s" % (spot,delta_t1,delta_eff1,delta1,round(delta_total-delta,4)))
print('='*100)
result['Spot'] = spot_range
result['TotalDelta_m_call'] = call_delta_total
result['EffectiveDelta_m_call'] = call_delta_eff
result['TotalDelta_k_call'] = call_delta_cnst


print('strike = ',strike,', option type : put')
print('='*100)
print("%10s %25s %25s %25s %25s" % ("Spot","delta_total","delta_eff","delta_constant_vol ","diff"))
print('-'*100)

option_put = OptionPlainVanilla(strike,maturitydt,ql.Option.Put).get_european_option()
volSurface_put = SviVolSurface(date_ql,paramset_p,daycounter,calendar)
svi_put = SviPricingModel(volSurface_put,underlying,daycounter,calendar,
                          util.to_ql_dates(maturity_dates),ql.Option.Put,'50etf')
vol_surface_put = svi_put.black_var_surface()

put_delta_total = []
put_delta_cnst = []
put_delta_eff = []
put_diff = []

process = evaluation.get_bsmprocess(daycounter, underlying_ql, vol_surface_put)
for spot in spot_range:
    underlying_ql.setValue(spot)
    engine = OptionEngine(process, engineType).engine
    option_put.setPricingEngine(engine)
    delta = option_put.delta()
    # 全Delta
    delta_total = svi_call.calculate_total_delta(evaluation,option_put,engineType,spot,strike,maturitydt,spot*0.0001)
    # Effective Delta
    delta_eff = svi_call.calculate_effective_delta(evaluation,option_put,engineType,spot, dS)

    delta1 = round(delta, 4)
    delta_t1 = round(delta_total, 4)
    delta_eff1 = round(delta_eff, 4)
    put_delta_total.append(delta_total)
    put_delta_cnst.append(delta)
    put_delta_eff.append(delta_eff)
    put_diff.append(delta_total-delta)
    print("%10s %25s %25s %25s %25s" % (spot,delta_t1,delta_eff1,delta1,round(delta_total-delta,4)))
print('='*100)


result['TotalDelta_m_put'] = put_delta_total
result['EffectiveDelta_m_put'] = put_delta_eff
result['TotalDelta_k_put'] = put_delta_cnst
#result['diff_put'] = put_diff
result.to_csv('delta_ql_50etf1.csv')