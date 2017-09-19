from pricing_engines.blackcalculator import blackcalculator
import numpy as np
import math
class svimodel:

    def __init__(self,ttm,params = [0.02,0.05,-0.8,-0.2,0.1]):
        # 虽然params有defalt值，但必须先对当天数据进行SVI模型校准，直接用default值计算结果肯定是不对的。
        a_star, b_star, rho_star, m_star, sigma_star = params
        self.a = a_star
        self.b = b_star
        self.rho = rho_star
        self.m = m_star
        self.sigma = sigma_star
        self.ttm = ttm

    def svi_iv_function(self,x_svi):
        return np.sqrt( self.a + self.b * (self.rho * (x_svi - self.m) +
                                           np.sqrt((x_svi - self.m) ** 2 + self.sigma ** 2)))

    # 计算隐含波动率对行权价的一阶倒数（dSigma_dK），用于全Delta计算
    def calculate_dSigma_dK(self,strike,forward,ttm):
        x = math.log(strike / forward, math.e)
        temp = np.sqrt((x-self.m)**2+self.sigma**2)
        temp1 = (x-self.m)/temp
        temp2 = np.sqrt(self.a+self.b*(self.rho*(x-self.m)+temp))
        dVol_dX = self.b*(self.rho+temp1)/(2*temp2)
        dX_dK = 1/strike
        dSigma_dK = dVol_dX*dX_dK
        return dSigma_dK

    # 计算Effective Delta
    def calculate_effective_delta(self, spot, dS, strike, discount, iscall):
        s_plus = spot + dS
        s_minus = spot - dS
        f_plus = s_plus / discount
        f_minus = s_minus / discount
        stdDev_plus = self.svi_iv_function(math.log(strike / f_plus, math.e)) * math.sqrt(self.ttm)
        stdDev_minus = self.svi_iv_function(math.log(strike / f_plus, math.e)) * math.sqrt(self.ttm)
        black_splus = blackcalculator(strike, f_plus, stdDev_plus, discount, iscall)
        black_sminus = blackcalculator(strike, f_minus, stdDev_minus, discount, iscall)
        delta_eff = (black_splus.value() - black_sminus.value()) / (s_plus - s_minus)
        return delta_eff