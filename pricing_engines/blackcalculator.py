import math
from scipy.stats import norm

class blackcalculator:

    def __init__(self,strike,forward,stdDev,discount,iscall):
        self.strike = strike
        self.forward = forward
        self.stdDev = stdDev
        self.discount = discount
        self.iscall = iscall
        if stdDev > 0.0:
            if strike == 0.0:
                n_d1 = 0.0
                n_d2 = 0.0
                cum_d1 = 1.0
                cum_d2 = 1.0
            else:
                D1 = math.log(forward/strike,math.e)/stdDev + 0.5*stdDev
                D2 = D1 - stdDev
                cum_d1 = norm.cdf(D1)
                cum_d2 = norm.cdf(D2)
                n_d1 = norm.pdf(D1)
                n_d2 = norm.pdf(D2)
        else:
            if forward > strike :
                cum_d1 = 1.0
                cum_d2 = 1.0
            else:
                cum_d1 = 0.0
                cum_d2 = 0.0
            n_d1 = 0.0
            n_d2 = 0.0

        if iscall:
            alpha = cum_d1 ## N(d1)
            dAlpha_dD1 = n_d1 ## n(d1)
            beta = -cum_d2 ## -N(d2)
            dBeta_dD2 = -n_d2 ## -n(d2)
        else:
            alpha = -1.0 + cum_d1 ## -N(-d1)
            dAlpha_dD1 = n_d1 ## n( d1)
            beta = 1.0 - cum_d2 ## N(-d2)
            dBeta_dD2 = -n_d2 ## -n( d2)
        self.alpha = alpha
        self.dAlpha_dD1 = dAlpha_dD1
        self.beta = beta
        self.dBeta_dD2 = dBeta_dD2
        self.x = strike
        self.dX_dS = 0.0

    def value(self):
        return self.discount * (self.forward * self.alpha + self.x * self.beta)

    def delta(self,spot):
        if spot <= 0.0: return
        else:
            DforwardDs = self.forward / spot
            temp = self.stdDev * spot
            DalphaDs = self.dAlpha_dD1 / temp
            DbetaDs = self.dBeta_dD2 / temp
            temp2 = DalphaDs * self.forward + self.alpha * DforwardDs + DbetaDs * self.x \
                    + self.beta * self.dX_dS
            return self.discount * temp2

    # 全Delta: dOption/dS = dOption/dS + dOption/dSigma * dSigma/dK
    # 根据SVI模型校准得到的隐含波动率的参数表达式，计算隐含波动率对行权价的一阶倒数（dSigma_dK）
    def delta_total(self,spot,dSigma_dK):
        delta = self.delta(spot)
        return delta + delta * dSigma_dK















