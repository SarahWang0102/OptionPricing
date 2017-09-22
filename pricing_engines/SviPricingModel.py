from Utilities import utilities as util
from pricing_engines.SviVolSurface import SviVolSurface
from Utilities.svi_read_data import get_curve_treasury_bond
import QuantLib as ql
import numpy as np
import math


class SviPricingModel:

    def __init__(self, evalDate, sviVolSurface,underlyingset, daycounter, calendar ,maturity_dates,
                 optiontype,contractType):
        ql.Settings.instance().evaluationDate = evalDate
        self.evalDate = evalDate
        self.daycounter = daycounter
        self.calendar = calendar
        self.maturity_dates = maturity_dates
        self.contractType = contractType
        self.sviVolSurface = sviVolSurface
        self.underlyingset = underlyingset
        self.black_var_surface = sviVolSurface.get_black_var_surface(underlyingset,contractType,
                                                                     maturity_dates)
        self.yield_ts = ql.YieldTermStructureHandle(get_curve_treasury_bond(evalDate, daycounter))
        self.dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, 0.0, self.daycounter))
        self.vol_ts = ql.BlackVolTermStructureHandle(self.black_var_surface)


    def get_option(self,spot,strike,maturitydt,optiontype):
        exercise = ql.EuropeanExercise(maturitydt)
        payoff = ql.PlainVanillaPayoff(optiontype, strike)
        option = ql.EuropeanOption(payoff, exercise)
        underlying = ql.SimpleQuote(spot)
        bsmprocess = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying), self.dividend_ts,
                                               self.yield_ts, self.vol_ts)
        option.setPricingEngine(ql.AnalyticEuropeanEngine(bsmprocess))
        return option


    # 计算全Delta
    def calculate_total_delta(self,spot,strike,maturitydt,optiontype,dS):
        option = self.get_option(spot,strike,maturitydt,optiontype)
        delta_tot = option.delta() + option.vega()*self.calculate_dSigma_dS(dS, strike,maturitydt)
        return delta_tot


    # 计算Effective Delta
    def calculate_effective_delta(self,spot, strike, maturitydt,optiontype, dS):
        black_vol_surface1 = self.sviVolSurface.get_black_var_surface(
            self.underlyingset,self.contractType,self.maturity_dates,dS)
        black_vol_surface2 = self.sviVolSurface.get_black_var_surface(
            self.underlyingset, self.contractType,self.maturity_dates, -dS)
        process1 = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot+dS)),self.dividend_ts,self.yield_ts,
                                                ql.BlackVolTermStructureHandle(black_vol_surface1))
        process2 = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot-dS)),self.dividend_ts,self.yield_ts,
                                                ql.BlackVolTermStructureHandle(black_vol_surface2))
        option1 = self.get_option(spot+dS,strike,maturitydt,optiontype)
        option1.setPricingEngine(ql.AnalyticEuropeanEngine(process1))
        option2 = self.get_option(spot-dS,strike,maturitydt,optiontype)
        option2.setPricingEngine(ql.AnalyticEuropeanEngine(process2))
        delta_eff = (option1.NPV()-option2.NPV())/(2*dS)
        return delta_eff


    def calculate_dSigma_dS(self, dS, strike,maturitydt):
        black_vol_surface1 = self.sviVolSurface.get_black_var_surface(
            self.underlyingset,self.contractType,self.maturity_dates,dS)
        black_vol_surface2 = self.sviVolSurface.get_black_var_surface(
            self.underlyingset, self.contractType,self.maturity_dates, -dS)
        ttm = self.daycounter.yearFraction(self.evalDate,maturitydt)
        vol1 = black_vol_surface1.blackVol(ttm,strike)
        vol2 = black_vol_surface2.blackVol(ttm,strike)
        dSigma_dS = (vol2-vol1)/(2*dS)
        return dSigma_dS





































