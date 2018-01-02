import math
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime
import os
import pickle
import QuantLib as ql
from WindPy import w
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from OptionStrategyLib.calibration import SVICalibration


def calculate_implied_vol(ql_optiontype,ql_mdt,strike,spot,option_price):
    exercise = ql.EuropeanExercise(ql_mdt)
    payoff = ql.PlainVanillaPayoff(ql_optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)
    flat_vol_ts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(ql_evalDate, calendar, 0.0, daycounter))
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_evalDate, 0.0, daycounter))
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_evalDate, rf, daycounter))
    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,
                                           flat_vol_ts)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))

    try:
        implied_vol = option.impliedVolatility(option_price, process, 1.0e-4, 300, 0.0, 10.0)
    except RuntimeError:
        implied_vol = 0.0
    return implied_vol

##################################################################################################
evalDate = datetime.date(2017,12,8)
ql_evalDate = ql.Date(evalDate.day,evalDate.month,evalDate.year)
rf = 0.03
calendar = ql.China()
daycounter = ql.ActualActual()
ql.Settings.instance().evaluationDate = ql_evalDate

##################################################################################################
ql_mdt = calendar.advance(ql_evalDate,ql.Period(3,ql.Months))

spot_300 = 4030.49
spot_50 = 2879.64
spot_500 = 6199.36
strike_300 = spot_300
strike_50 = spot_50
strike_500 = spot_500
option_300_call = spot_300*3.97/100.0
option_300_put = spot_300*3.5/100.0
option_50_call = spot_50*4.1/100.0
option_50_put = spot_50*3.16/100.0
option_500_call = spot_500*3.8/100.0
option_500_put = spot_500*4.76/100.0
iv_300_call = calculate_implied_vol(ql.Option.Call,ql_mdt,strike_300,spot_300,option_300_call)
iv_300_put = calculate_implied_vol(ql.Option.Put,ql_mdt,strike_300,spot_300,option_300_put)
iv_50_call = calculate_implied_vol(ql.Option.Call,ql_mdt,strike_50,spot_50,option_50_call)
iv_50_put = calculate_implied_vol(ql.Option.Put,ql_mdt,strike_50,spot_50,option_50_put)
iv_500_call = calculate_implied_vol(ql.Option.Call,ql_mdt,strike_500,spot_500,option_500_call)
iv_500_put = calculate_implied_vol(ql.Option.Put,ql_mdt,strike_500,spot_500,option_500_put)
print('iv_300_call : ',iv_300_call)
print('iv_300_put : ',iv_300_put)
print('iv_50_call : ',iv_50_call)
print('iv_50_put : ',iv_50_put)
print('iv_500_call : ',iv_500_call)
print('iv_500_put : ',iv_500_put)
##################################################################################################



