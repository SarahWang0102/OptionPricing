import svi_read_data as wind_data
from hedging_utility import get_spot_price, get_1st_percentile_dates, get_2nd_percentile_dates, \
    get_3rd_percentile_dates, get_4th_percentile_dates, hedging_performance, calculate_cash_position, \
    calculate_delta_sviVolSurface, get_local_volatility_surface_smoothed, get_local_volatility_surface, \
    calculate_delta_svi, calculate_hedging_error
from utilities import convert_datelist_from_datetime_to_ql as to_ql_dates
from utilities import convert_datelist_from_ql_to_datetime as to_dt_dates
from utilities import convert_date_from_ql_to_datetime as to_dt_date
from utilities import convert_date_from_datetime_to_ql as to_ql_date
import svi_prepare_vol_data as svi_data
import svi_calibration_utility as svi_util
import QuantLib as ql
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import pandas as pd
import math
import numpy as np
from WindPy import w
import datetime
import timeit
import os
import pickle

start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()


def Date(d, m, y):
    return ql.Date(d, m, y)

def get_black_variance_surface(calibrated_params,maturity_dates_c,calibrate_date,daycounter,calendar,spot,rfs):
    strikes = np.arange(1.0, 5.0, 0.1 / 100)
    data_BVS = []
    for idx_mdt,mdt in enumerate(maturity_dates_c):
        params = calibrated_params[idx_mdt]
        a_star, b_star, rho_star, m_star, sigma_star = params
        ttm = daycounter.yearFraction(calibrate_date,mdt)
        rf = rfs.get(idx_mdt)
        Ft = spot * math.exp(rf * ttm)
        x_svi =  np.log(strikes/Ft)
        vol = np.sqrt(np.maximum(0,a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))))
        #vol = np.sqrt(np.sqrt(np.maximum(0, a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))))
        data_BVS.append(vol)
    implied_vols = ql.Matrix(len(strikes), len(maturity_dates_c))
    for i in range(implied_vols.rows()):
        for j in range(implied_vols.columns()):
            implied_vols[i][j] = data_BVS[j][i]
    black_var_surface = ql.BlackVarianceSurface(calibrate_date, calendar,maturity_dates_c, strikes,implied_vols, daycounter)
    return black_var_surface

def get_black_variance_surface_smoothed(calibrated_params_list,maturity_dates_c,calibrate_dates,daycounter,calendar,spot,rfs):
    strikes = np.arange(1.0, 5.0, 0.1 / 100)
    data_BVS = []

    for idx_mdt,mdt in enumerate(maturity_dates_c):
        vol_list = []
        avg_vols = []
        for idx_calibrate,calibrated_params in enumerate(calibrated_params_list):
            params = calibrated_params[idx_mdt]
            a_star, b_star, rho_star, m_star, sigma_star = params
            calibrate_date = calibrate_dates[idx_calibrate]
            ttm = daycounter.yearFraction(calibrate_date,mdt)
            rf = rfs.get(idx_mdt)
            Ft = spot * math.exp(rf * ttm)
            x_svi =  np.log(strikes/Ft)
            vol = np.sqrt(np.maximum(0,a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))))
            #vol = np.sqrt(np.sqrt(np.maximum(0, a_star + b_star * (
            #rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)))))
            vol_list.append(vol)
        for idx_v,v in enumerate(vol_list[0]):
            avg_vol = 0.0
            for vols in vol_list:
                avg_vol += vols[idx_v]
            avg_vol = avg_vol/len(vol_list)
            avg_vols.append(avg_vol)
        data_BVS.append(avg_vols)
    implied_vols = ql.Matrix(len(strikes), len(maturity_dates_c))
    for i in range(implied_vols.rows()):
        for j in range(implied_vols.columns()):
            implied_vols[i][j] = data_BVS[j][i]
    black_var_surface = ql.BlackVarianceSurface(calibrate_dates[0], calendar,maturity_dates_c, strikes,implied_vols, daycounter)
    return black_var_surface

