from scipy.optimize import minimize
import numpy as np
import math


class SVI_NelderMeadOptimization:


    def __init__(self,data):
        #self.init_msigma = init_msigma
        #self.init_adc = init_adc
        #self._a_star = 0.0
        #self._d_star = 0.0
        #self._c_star = 0.0
        self.data = data
        # data[0]:log-moneyness:x ; data[1]:variance:v

    def outter_fun(self,params):
        m,sigma = params
        sigma = max(0,sigma)
        adc_0 = np.random.random([1,3]) * np.array([max(self.data[1]),4*sigma,4*sigma])
        def inner_fun(params):
            a,d,c = params
            sum = 0.0
            for i,xi in enumerate(self.data[0]):
                yi = (xi - m)/sigma
                f_msigma = (a + d*yi + c * math.sqrt((yi**2 + 1)) - self.data[1][i])**2
                sum += f_msigma
            return sum
        #print(m,sigma)
        # Constraints: 0 <= c <=4sigma; |d| <= c and |d| <= 4sigma - c; 0 <= a <= max{vi}
        #print("m",m,";\tsigma",sigma)
        bnds = ((1e-10,max(self.data[1])),(-4*sigma,4*sigma),(0, 4*sigma))
        #bnds = ((None, max(self.data[1])), (-4 * sigma, 4 * sigma), (0, 4 * sigma))
        b = np.array(bnds,float)
        cons = (
            {'type':'ineq','fun': lambda x: x[2] - abs(x[1])},
            {'type':'ineq','fun': lambda x: 4*sigma - x[2] - abs(x[1])}
        )
        inner_res = minimize(inner_fun,adc_0,method='SLSQP',bounds = bnds,constraints=cons, tol=1e-6)
        a_star,d_star,c_star = inner_res.x
        #global _a_star,_d_star,_c_star
        self._a_star, self._d_star, self._c_star = inner_res.x
        #print(a_star,d_star,c_star)
        sum = 0.0
        for i,xi in enumerate(self.data[0]):
            yi = (xi - m)/sigma
            f_msigma = (a_star + d_star*yi + c_star * math.sqrt((yi**2 + 1)) - self.data[1][i])**2
            sum += f_msigma
        return sum

    def optimization(self):
        outter_res = minimize(self.outter_fun, np.random.random([1,2]), method='Nelder-Mead', tol=1e-6)
        m_star,sigma_star = outter_res.x
        #print(outter_res.x)
        #print(outter_res)
        obj = outter_res.fun
        #print(_a_star,_d_star,_c_star,m_star,sigma_star)
        # SVI parameters: a, b, sigma, rho, m
        calibrated_params = [self._a_star, self._d_star, self._c_star,m_star,sigma_star]
        return calibrated_params,obj


    def one_fuction(self,params):
        a,d,c,m,sigma = params
        sum = 0.0
        for i,xi in enumerate(self.data[0]):
            yi = (xi - m)/sigma
            f_msigma = (a + d*yi + c * math.sqrt((yi**2 + 1)) - self.data[1][i])**2
            sum += f_msigma
        return sum

    def optimization_SLSQP(self):
        [a0,d0,c0,m0,sigma0] = [1,1,1,1,1]
        bnds = ((0,max(self.data[1])),(None,None),(0,None),(None,None),(0,None))
        cons = (
            {'type': 'ineq', 'fun': lambda x: 4*x[4] - x[2]}, # 4sigma - c >= 0
            {'type': 'ineq', 'fun': lambda x: x[2] - abs(x[1])}, # |d| <= c
            {'type': 'ineq', 'fun': lambda x: 4*x[4] - x[2] - abs(x[1])} # |d| <= 4sigma -c
        )
        res = minimize(self.one_fuction, np.array([a0,d0,c0,m0,sigma0]),
                       method='SLSQP',bounds = bnds,constraints=cons, tol=1e-6)
        a_star,d_star,c_star, m_star, sigma_star = res.x
        print('a_star,d_star,c_star, m_star, sigma_star: ', a_star,d_star,c_star, m_star, sigma_star)
        return a_star,d_star,c_star, m_star, sigma_star
