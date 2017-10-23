from Utilities import utilities as util
import QuantLib as ql
import numpy as np
import math


class SviVolSurface:

    def __init__(self, evalDate, calibrated_params, daycounter, calendar):
        self.evalDate = evalDate
        self.calibrated_params = calibrated_params
        self.daycounter = daycounter
        self.calendar = calendar

    def get_black_var_surface(self,underlying,contractType, maturity_dates,dS = 0.0):
        if contractType == '50etf':
            strikes = np.arange(1.0, 5.0, 0.1 / 100)
            black_var_surface = self.get_black_var_surface_50etf(underlying,dS,strikes)
        elif contractType == 'm':
            strikes = np.arange(2400.0, 3200.0, 1.0)
            black_var_surface = self.get_black_var_surface_m(underlying,dS,strikes)
        elif contractType == 'sr':
            strikes = np.arange(5500.0, 7400.0, 1.0)
            black_var_surface = self.get_black_var_surface_sr(underlying,dS,strikes)
        else:
            black_var_surface = ''
        return black_var_surface

    def get_black_var_surface_50etf(self,spot, dS = 0.0,strikes=np.arange(1.0, 5.0, 0.1 / 100)):
        volset = []
        maturity_dates = self.calibrated_params.keys()
        #print(maturity_dates)
        maturity_dates = sorted(maturity_dates)
        #print(maturity_dates)
        for mdt in maturity_dates:
            params = self.calibrated_params.get(mdt)
            a_star, b_star, rho_star, m_star, sigma_star = params
            maturitydt = ql.Date(mdt.day,mdt.month,mdt.year)
            ttm = self.daycounter.yearFraction(self.evalDate, maturitydt)
            rf = util.get_rf_tbcurve(self.evalDate, self.daycounter, maturitydt)
            Ft = (spot+dS) * math.exp(rf * ttm)
            x_svi = np.log(strikes / Ft)
            vol = np.sqrt(np.maximum(0, a_star + b_star * (
                rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))))
            volset.append(vol)
        implied_vols = ql.Matrix(len(strikes), len(maturity_dates))
        for i in range(implied_vols.rows()):
            for j in range(implied_vols.columns()):
                implied_vols[i][j] = volset[j][i]
        black_var_surface = ql.BlackVarianceSurface(self.evalDate, self.calendar, util.to_ql_dates(maturity_dates), strikes,
                                                    implied_vols, self.daycounter)
        return black_var_surface

    def get_black_var_surface_50etf2(self, maturity_dates,spot, dS = 0.0,strikes=np.arange(1.0, 5.0, 0.1 / 100)):
        volset = []
        for idx_mdt, mdt in enumerate(maturity_dates):
            params = self.calibrated_params[idx_mdt]
            a_star, b_star, rho_star, m_star, sigma_star = params
            ttm = self.daycounter.yearFraction(self.evalDate, mdt)
            rf = util.get_rf_tbcurve(self.evalDate, self.daycounter, mdt)
            Ft = (spot+dS) * math.exp(rf * ttm)
            x_svi = np.log(strikes / Ft)
            vol = np.sqrt(np.maximum(0, a_star + b_star * (
                rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))))
            volset.append(vol)
        implied_vols = ql.Matrix(len(strikes), len(maturity_dates))
        for i in range(implied_vols.rows()):
            for j in range(implied_vols.columns()):
                implied_vols[i][j] = volset[j][i]
        black_var_surface = ql.BlackVarianceSurface(self.evalDate, self.calendar, maturity_dates, strikes,
                                                    implied_vols, self.daycounter)
        return black_var_surface


    def get_black_var_surface_m(self,underlying_prices, dS = 0.0,strikes=np.arange(2400.0, 3200.0, 1.0)):
        volset = []
        maturity_dates = sorted(self.calibrated_params.keys())
        for mdt in maturity_dates:
            params = self.calibrated_params.get(mdt)
            a_star, b_star, rho_star, m_star, sigma_star = params
            maturity_dates.append(mdt)
            #ttm = self.daycounter.yearFraction(self.evalDate, mdt)
            #rf = util.get_rf_tbcurve(self.evalDate, self.daycounter, mdt)
            spot = underlying_prices.get(mdt) + dS
            #Ft = spot * math.exp(rf * ttm)
            Ft = spot
            x_svi = np.log(strikes / Ft)
            vol = np.sqrt(np.maximum(0, a_star + b_star * (
                rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))))
            volset.append(vol)
        implied_vols = ql.Matrix(len(strikes), len(maturity_dates))
        for i in range(implied_vols.rows()):
            for j in range(implied_vols.columns()):
                implied_vols[i][j] = volset[j][i]
        black_var_surface = ql.BlackVarianceSurface(self.evalDate, self.calendar, util.to_ql_dates(maturity_dates),
                                                    strikes, implied_vols, self.daycounter)
        return black_var_surface


    def get_black_var_surface_sr(self,underlying_prices, dS = 0.0,strikes=np.arange(5500.0, 7400.0, 1.0)):
        volset = []
        maturity_dates = sorted(self.calibrated_params.keys())
        for mdt in maturity_dates:
            params = self.calibrated_params.get(mdt)
            a_star, b_star, rho_star, m_star, sigma_star = params
            #ttm = self.daycounter.yearFraction(self.evalDate, mdt)
            #rf = util.get_rf_tbcurve(self.evalDate, self.daycounter, mdt)
            spot = underlying_prices.get(mdt) + dS
            #Ft = spot * math.exp(rf * ttm)
            Ft = spot
            x_svi = np.log(strikes / Ft)
            vol = np.sqrt(np.maximum(0, a_star + b_star * (
                rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))))
            volset.append(vol)
        implied_vols = ql.Matrix(len(strikes), len(maturity_dates))
        for i in range(implied_vols.rows()):
            for j in range(implied_vols.columns()):
                implied_vols[i][j] = volset[j][i]
        black_var_surface = ql.BlackVarianceSurface(self.evalDate, self.calendar, util.to_ql_dates(maturity_dates),
                                                    strikes, implied_vols, self.daycounter)
        return black_var_surface