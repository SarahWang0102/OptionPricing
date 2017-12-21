import pandas as pd
import numpy as np
from svi_model.svi_NelderMead_optimization import  SVI_NelderMeadOptimization

class SVICalibration():

    def __init__(self,evalDate,initparams=[0.1, 0.1 ,0.1 ,0.1 ,0.1],sim_no=10):
        self.evalDate = evalDate
        self.initparams = initparams
        self.sim_no = sim_no

    def calibrate_rawsvi(self,strikes,maturity_dates,underlying_prices,option_prices,implied_vols,rfs):
        df = pd.DataFrame({'strikes':strikes,
                           'maturity_dates':maturity_dates,
                           'underlying_prices':underlying_prices,
                           'option_prices':option_prices,
                           'implied_vols':option_prices,
                           'risk_free_rates':rfs})
        ttms = []
        for mdt in maturity_dates:
            ttm = (mdt - self.evalDate).days / 365.0
            ttms.append(ttm)
        df['ttm'] = ttms
        df['forwards'] = df['underlying_prices']*np.exp(df['risk_free_rates'])
        df['logmoneyness'] = np.log(df['strikes']/df['forwards'])
        df['totalvariance'] = (df['implied_vols']**2)*df['ttm']
        mdates_uqique = df['maturity_dates'].unique()
        for mdate in mdates_uqique:
            c1 = df['maturity_dates']==mdate
            logmoneyness = df[c1]['logmoneyness']
            totalvariance = df[c1]['totalvariance']
            ttm = df[c1]['ttm'].iloc[0]
            data = [logmoneyness,totalvariance]
            min_sse = 100
            calibrated_params = None
            for iter in range(self.sim_no):
                ms_0 = self.initparams[0:2]
                adc_0 = self.initparams[2:]
                nm = SVI_NelderMeadOptimization(data, adc_0, ms_0, 1e-7)
                calibrated_params, obj = nm.optimization()
                _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
                sse = 0.0
                for i, m in enumerate(logmoneyness):
                    tv = totalvariance[i]
                    y_1 = np.divide((m - m_star), sigma_star)
                    tv_1 = _a_star + _d_star * y_1 + _c_star * np.sqrt(y_1 ** 2 + 1)
                    sse += (tv - tv_1) ** 2
                if sse >= min_sse: continue
                min_sse = sse
            _a_star, _d_star, _c_star, m_star, sigma_star = calibrated_params
            a_star = np.divide(_a_star, ttm)
            b_star = np.divide(_c_star, (sigma_star * ttm))
            rho_star = np.divide(_d_star, _c_star)
            params_dict = {'dt_date': self.evalDate,'dt_maturity':mdate,
                           'a':a_star,'b':b_star,'rho':rho_star,'m':m_star,'sigma':sigma_star}
            return params_dict