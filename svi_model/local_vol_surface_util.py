import QuantLib as ql
import math
import numpy as np

def Date(d, m, y):
    return ql.Date(d, m, y)

def get_black_variance_surface_m(calibrated_params,maturity_dates_c,calibrate_date,daycounter,calendar,spot,rfs):
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

