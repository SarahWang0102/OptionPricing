from WindPy import *
import QuantLib as ql
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
# Get Wind Market Data
w.start()
# 50ETF currently trading contracts
options     = w.wset("optioncontractbasicinfo","exchange=sse;windcode=510050.SH;status=all")
optionFlds  = options.Fields
optionData = options.Data
# 50ETF market price data
mkt         = w.wset("optiondailyquotationstastics","startdate=2017-06-12;enddate=2017-06-12;exchange=sse;windcode=510050.SH;field=date,option_code,option_name,amount,pre_settle,open,highest,lowest,close,settlement_price")
mktFlds     = mkt.Fields
mktData     = mkt.Data
# Uderlying market price
underlying   = w.wsd("510050.SH", "close,settle", "2017-06-12", "2017-06-12", "")
spot  = underlying.Data[0][0]
#################################
#print(mktFlds)
#['date', 'option_code', 'option_name', 'amount', 'pre_settle', 'open', 'highest', 'lowest', 'close', 'settlement_price']
#print(optionFlds)
#['wind_code', 'sec_name', 'option_mark_code', 'option_type', 'call_or_put', 'exercise_mode', 'exercise_price',
#'contract_unit', 'limit_month', 'listed_date', 'expire_date', 'exercise_date', 'settlement_date', 'reference_price',
#'settle_mode', 'contract_state']
##################################
# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(12,6,2017)
ql.Settings.instance().evaluationDate = evalDate
risk_free_rate = 0.0
dividend_rate = 0.0
yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,risk_free_rate,daycounter))
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,dividend_rate,daycounter))
flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, 0.0, daycounter))
# Prepare strikes,maturity dates for BlackVarianceSurface
optionids   = mktData[mktFlds.index('option_code')]
nbr_options = len(optionids)
maturitydates_call = []
strikes_call = []
mktclose_call = []
vol1 = []
vol2 = []
vol3 = []
vol4 = []
strike_BVS = [2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6]
tempcontainer = [2.299, 2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6]
for idx in range(nbr_options):
    optionid        = optionids[idx]
    optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
    if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
        optiontype  = ql.Option.Call
        strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
        mdate       = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
        maturitydt  = ql.Date(mdate.day,mdate.month,mdate.year)
        mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
        close       = mktData[mktFlds.index('close')][mktindex]
        exercise    = ql.EuropeanExercise(maturitydt)
        payoff      = ql.PlainVanillaPayoff(optiontype,strike)
        option      = ql.EuropeanOption(payoff,exercise)
        process     = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)),dividend_ts,yield_ts,flat_vol_ts)
        option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
        try:
            implied_vol = option.impliedVolatility(close,process,1.0e-1,300,0.0,4.0)
        except RuntimeError:
            implied_vol = 0.001
        voldata = w.wss(optionid+'.SH', "us_impliedvol","tradeDate=20170612")
        implied_vol = voldata.Data[0][0]
        maturitydates_call.append(maturitydt)
        strikes_call.append(strike)
        mktclose_call.append(close)
        if strike in tempcontainer:
            if mdate.month == evalDate.month():
                vol1.append(implied_vol)
                dt1 = maturitydt
            elif mdate.month == evalDate.month() + 1:
                vol2.append(implied_vol)
                dt2 = maturitydt
            elif mdate.month == evalDate.month() + 3:
                vol3.append(implied_vol)
                dt3 = maturitydt
            elif mdate.month == evalDate.month() + 6:
                vol4.append(implied_vol)
                dt4 = maturitydt
# Construct BlackVarianceSurface
data_BVS = [vol1,vol2,vol3,vol4]
mdts_BVS = [dt1,dt2,dt3,dt4]
implied_vols = ql.Matrix(len(strike_BVS), len(mdts_BVS))
for i in range(implied_vols.rows()):
    for j in range(implied_vols.columns()):
        implied_vols[i][j] = data_BVS[j][i]
black_var_surface = ql.BlackVarianceSurface(
    evalDate, calendar,
    mdts_BVS, strike_BVS,
    implied_vols, daycounter)

# Plot
plot_years = np.arange(0, 0.5, 0.05)
plot_strikes = np.arange(2.3, 2.6, 0.03)
fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))

surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.1)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()


w.stop()
