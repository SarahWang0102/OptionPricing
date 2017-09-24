from pricing_engines.SviPricingModel import SviPricingModel
from pricing_engines.SviVolSurface import SviVolSurface
from pricing_engines.Evaluation import Evaluation
import Utilities.svi_prepare_vol_data as svi_data
from Utilities import utilities as util
from exotic_options import exotic_option_utilities as exotic
import QuantLib as ql
import pandas as pd
import os
import pickle
import numpy as np


with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_calls_nobnd.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_dates_calls_nobnd.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_svi_dataset_calls_nobnd.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Evaluation Settings
today = ql.Date(17,7,2017)
evaluation = Evaluation(today)
ql.Settings.instance().evaluationDate = today
calendar = ql.China()
daycounter = ql.ActualActual()
contractType = '50etf'
engineType = 'AnalyticEuropeanEngine'
facevalue = 10000
i = 3

# Vol Surface and bsm process
curve = svi_data.get_curve_treasury_bond(today,daycounter)
calibrated_params = daily_params.get(util.to_dt_date(today))  # on calibrate_date
cal_vols, put_vols, maturity_dates, spot, risk_free_rates = daily_svi_dataset.get(util.to_dt_date(today))

volSurface = SviVolSurface(today,calibrated_params,daycounter,calendar)
svi_model = SviPricingModel(volSurface,spot,daycounter,calendar,
                           util.to_ql_dates(maturity_dates),ql.Option.Call,contractType)
black_var_surface = svi_model.black_var_surface()
maturityDate = util.to_ql_date(maturity_dates[i])
print(maturityDate)
rf = util.get_rf_tbcurve(today,daycounter,maturityDate)
underlying = ql.SimpleQuote(spot)
process = evaluation.get_bsmprocess(daycounter,underlying,black_var_surface)


# Barrier Option
barrier = 2.45
strike = 2.75
optiontype = ql.Option.Call
barrierType = ql.Barrier.DownOut
exercise = ql.EuropeanExercise(maturityDate)
payoff = ql.PlainVanillaPayoff(optiontype, strike)
barrieroption = ql.BarrierOption(barrierType, barrier, 0.0,payoff, exercise)

ttm = daycounter.yearFraction(today,maturityDate)
strike_barrier = ((barrier)**2)/strike
strike_barrierforward = ((barrier*np.exp(rf*ttm))**2)/strike

print('underlying : ',spot)
print('barrier : ', barrier)
print('strike : ', strike)
print('barrier forward : ',barrier*np.exp(rf*ttm))

barrier_engine = ql.AnalyticBarrierEngine(process)
european_engine = ql.AnalyticEuropeanEngine(process)
barrieroption.setPricingEngine(barrier_engine)
barrier_price = barrieroption.NPV()

# Construct Replicaiton Portfolio
portfolio = ql.CompositeInstrument()

# Long a call struck at strike
call = ql.EuropeanOption(payoff,exercise)
call.setPricingEngine(european_engine)
call_price = call.NPV()
print('call value : ',call_price)
portfolio.add(call)


# short put_ratio shares of puts struck at k_put
k_put = strike_barrierforward
print('k` : ',k_put)
put_payoff = ql.PlainVanillaPayoff(ql.Option.Put, k_put)
put = ql.EuropeanOption(put_payoff,exercise)
put.setPricingEngine(european_engine)

'''
put_price = put.NPV()
put_ratio = np.sqrt(strike/k_put)
print('put_ratio : ',put_ratio,call_price/put_price,np.abs(put_price*np.sqrt(strike/k_put)-call_price))
print('put value : ',put.NPV())
# Find the shares of put that make replication portfolio = 0.0 at barrier
put_ratio2 = 1.0
diff = 10
for r in np.arange(0,2,0.001):
    portfolio1 = ql.CompositeInstrument()
    portfolio1.add(call)
    underlying.setValue(barrier)
    portfolio1.subtract(put, r)
    npv = portfolio1.NPV()
    if abs(npv - 0) < diff :
        diff = abs(npv - 0)
        put_ratio2 = r
print('put_ratio2 : ',put_ratio2)
'''
underlying.setValue(barrier)
callprice_at_barrier = call.NPV()
putprice_at_barrier = put.NPV()
put_ratio = callprice_at_barrier/putprice_at_barrier
print('put ratio : ',put_ratio)
portfolio.subtract(put,put_ratio)

'''
put_payoff2= ql.PlainVanillaPayoff(ql.Option.Put, strike_barrier)
put2 = ql.EuropeanOption(put_payoff2,exercise)
put2.setPricingEngine(european_engine)
print('callprice_at_barrier/putprice_at_barrier : ',put_ratio)
print('k_put/strike',np.sqrt(k_put/strike))
put_ratio2 = callprice_at_barrier/put2.NPV()
print('callprice_at_barrier/putprice2_at_barrier : ',put_ratio2)
print('strike_barrier/strike',np.sqrt(strike_barrier/strike))
'''

underlying.setValue(spot)
portfolio_value = portfolio.NPV()
print('reference npv :',barrier_price)
print('replicate npv :',portfolio_value)
print('hedge error : ',barrier_price-portfolio_value)
print("="*100)
print("%15s %25s %25s %25s %25s %25s" % ("spot","barrier_npv","euro_call","euro_put","replicate npv", "pnl"))
print("-"*100)
df = pd.DataFrame()
spot_range = np.arange(barrier-0.2,strike+0.2,0.01)
barrier_npvs = []
call_npvs = []
put_npvs = []
portfolio_values = []
pnls = []
for s in spot_range:
    underlying.setValue(s)
    barrier_npv = facevalue*exotic.barrier_npv_ql(today, [], barrierType, barrier, payoff, exercise, process)
    call_npv = facevalue*call.NPV()
    put_npv = facevalue*put.NPV()
    #barrier_npv = barrieroption.NPV()
    if s < barrier:
        portfolio_value = 0.0
    else:
        portfolio_value = facevalue*portfolio.NPV()
    pnl = portfolio_value - barrier_npv
    barrier_npvs.append(barrier_npv)
    call_npvs.append(call_npv)
    put_npvs.append((put_npv))
    portfolio_values.append(portfolio_value)
    pnls.append(pnl)
    print("%15s %25s %25s %25s %25s %25s" % (s, round(barrier_npv,2),round(call_npv,2),round(put_npv,2),
                                             round(portfolio_value,2), round(pnl,2)))
df['Spot'] = spot_range
df['barrier_npv'] = barrier_npvs
df['call_npv'] = call_npvs
df['put_npv'] = put_npvs
df['replicate_portfolio'] = portfolio_values
df['pnl'] = pnls
df.to_csv('static_hegde_knockout_call.csv')