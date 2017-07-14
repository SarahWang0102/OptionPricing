from WindPy import *
import QuantLib as ql
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from VolatilityData_Copied import *
from scipy.optimize import root
from scipy.optimize import least_squares
from CalibrationPerformenceFuns import *

# Evaluation Settings
w.start()
calendar        = ql.China()
daycounter      = ql.ActualActual()
evalDate        = ql.Date(12,6,2017)
# Construct interest rate term structure from depo
curve           = get_curve_depo(evalDate, daycounter)
yield_ts        = ql.YieldTermStructureHandle(curve)
dividend_ts     = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
flat_vol_ts     = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, 0.0, daycounter))
ql.Settings.instance().evaluationDate = evalDate
summary         = []

# Vol Surface matrix data
#data,expiration_dates,strikes,spot  = get_impliedvolmat_call_BS(evalDate, daycounter,calendar)
data,expiration_dates,strikes,spot = get_impliedvolmat_call_wind(evalDate)
init1 = (0.02,0.2,0.5,0.1,0.01)
########################################################################################################################
# Calibrate using QuantLib Levenberg-Marquardt Solver
print('1. Calibrate using QuantLib Levenberg-Marquardt Solver')
model1,engine1 = setup_model(yield_ts, dividend_ts, spot, init_condition= init1)
heston_helpers1,grid_data1 = setup_helpers(engine1,expiration_dates,strikes,data,evalDate,spot,yield_ts,dividend_ts,calendar)
lm = ql.LevenbergMarquardt(1.0e-8,1.0e-8,1.0e-8)
model1.calibrate(heston_helpers1,lm,ql.EndCriteria(500,300,1.0e-8,1.0e-8,1.0e-8))
theta,kappa,sigma,rho,v0 = model1.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers1,grid_data1,True)
summary.append(["QL LM1", error] + list(model1.params()))

########################################################################################################################
# Calibrate using Scipy Levenberg-Marquardt Solver
print('2. Calibrate using Scipy Levenberg-Marquardt Solver')
model2, engine2 = setup_model(yield_ts, dividend_ts, spot, init_condition = init1)
heston_helpers2, grid_data2 = setup_helpers( engine2, expiration_dates, strikes, data,evalDate, spot, yield_ts, dividend_ts,calendar)
initial_condition = list(model2.params())
cost_function = cost_function_generator(model2, heston_helpers2)
sol = root(cost_function,np.array(initial_condition), method='lm')
theta, kappa, sigma, rho, v0 = model2.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers2, grid_data2,True)
summary.append(["Scipy LM1", error] + list(model2.params()))

########################################################################################################################
# Calibrate using Scipy Least Squares Method
print('3. Calibrate using Scipy Least Squares Method')
model3, engine3 = setup_model(yield_ts, dividend_ts, spot,init_condition = init1)
heston_helpers3, grid_data3 = setup_helpers( engine3, expiration_dates, strikes, data,evalDate, spot, yield_ts, dividend_ts,calendar)
initial_condition = list(model3.params())
cost_function = cost_function_generator(model3, heston_helpers3)
sol3 = least_squares(cost_function, initial_condition)
theta, kappa, sigma, rho, v0 = model3.params()
print("theta = %f, kappa = %f, sigma = %f, rho = %f, v0 = %f" % (theta, kappa, sigma, rho, v0))
error = calibration_report(heston_helpers3, grid_data3,True)
summary.append(["Scipy LS1", error] + list(model3.params()))

########################################################################################################################


w.stop()
