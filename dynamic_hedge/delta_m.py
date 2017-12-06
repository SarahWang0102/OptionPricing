from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
from Utilities import utilities as util
from Utilities.svi_read_data import get_curve_treasury_bond
import QuantLib as ql
import pandas as pd
import numpy as np
import math
import datetime
import os
import pickle


with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_params_calls_noZeroVol.pickle','rb') as f:
    daily_params_c = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_svi_dataset_calls_noZeroVol.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_params_puts_noZeroVol.pickle','rb') as f:
    daily_params_p = pickle.load(f)[0]


date = datetime.date(2017,7,17)
contractType = 'm'
daycounter = ql.ActualActual()
calendar = ql.China()
date_ql = util.to_ql_date(date)

paramset_c = daily_params_c.get(date)
paramset_p = daily_params_p.get(date)
dataset = daily_svi_dataset.get(date)
cal_vols, put_vols, maturity_dates, underlying, rfs = dataset
contractId = '1801'
maturitydt = util.get_mdate_by_contractid(contractType,contractId,calendar)
params_c = paramset_c.get(contractId)
params_p = paramset_p.get(contractId)
rf = util.get_rf_tbcurve(date_ql,daycounter,maturitydt)
ttm = daycounter.yearFraction(date_ql,maturitydt)
discount = math.exp(-rf*ttm)

# Example
strike = 2700
dS = 0.001
iscall = True
curve = get_curve_treasury_bond(date_ql, daycounter)
yield_ts = util.get_yield_ts(date_ql,curve,maturitydt,daycounter)
dividend_ts = util.get_dividend_ts(date_ql,daycounter)

print('strike = ',strike,', option type : call')
print('='*100)
print("%10s %25s %25s %25s %25s" % ("Spot","delta_total","delta_eff","delta_constant_vol ","diff"))
print('-'*100)

volSurface_call = SviVolSurface(date_ql,paramset_c,daycounter,calendar)
svi_call = SviPricingModel(date_ql,volSurface_call,underlying,daycounter,calendar,util.to_ql_dates(maturity_dates),ql.Option.Call,contractType)

call_delta_total = []
call_delta_cnst = []
call_delta_eff = []
call_diff = []
#index=['data_total','data_const']
result = pd.DataFrame()
for spot in np.arange(2400.0,3200.0,10.0):

    delta = svi_call.get_option(spot,strike,maturitydt,ql.Option.Call).delta()
    # 全Delta
    delta_total = svi_call.calculate_total_delta(spot,strike,maturitydt,ql.Option.Call,spot*0.0001)
    # Effective Delta
    delta_eff = svi_call.calculate_effective_delta(spot,strike,maturitydt,ql.Option.Call, dS)

    delta1 = round(delta, 4)
    delta_t1 = round(delta_total, 4)
    delta_eff1 = round(delta_eff, 4)
    call_delta_total.append(delta_total)
    call_delta_cnst.append(delta)
    call_delta_eff.append(delta_eff)
    call_diff.append(delta_total-delta)
    print("%10s %25s %25s %25s %25s" % (spot,delta_t1,delta_eff1,delta1,round(delta_total-delta,4)))
print('='*100)
result['Spot'] = np.arange(2400.0,3200.0,10.0)
result['TotalDelta_m_call'] = call_delta_total
result['EffectiveDelta_m_call'] = call_delta_eff
result['TotalDelta_k_call'] = call_delta_cnst


print('strike = ',strike,', option type : put')
print('='*100)
print("%10s %25s %25s %25s %25s" % ("Spot","delta_total","delta_eff","delta_constant_vol ","diff"))
print('-'*100)

volSurface_put = SviVolSurface(date_ql,paramset_p,daycounter,calendar)
svi_put = SviPricingModel(date_ql,volSurface_put,underlying,daycounter,calendar,util.to_ql_dates(maturity_dates),ql.Option.Put,contractType)

put_delta_total = []
put_delta_cnst = []
put_delta_eff = []
put_diff = []

for spot in np.arange(2400.0,3200.0,10.0):

    delta = svi_call.get_option(spot,strike,maturitydt,ql.Option.Put).delta()
    # 全Delta
    delta_total = svi_call.calculate_total_delta(spot,strike,maturitydt,ql.Option.Put,spot*0.0001)
    # Effective Delta
    delta_eff = svi_call.calculate_effective_delta(spot,strike,maturitydt,ql.Option.Put, dS)

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
result.to_csv('delta_ql_m.csv')