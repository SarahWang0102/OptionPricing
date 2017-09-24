from Utilities import utilities as util
from pricing_options.SviVolSurface import SviVolSurface
from pricing_options.OptionPlainVanilla import OptionPlainVanilla
from pricing_options.OptionEngine import OptionEngine
from pricing_options.Evaluation import Evaluation
from Utilities.svi_read_data import get_curve_treasury_bond
import QuantLib as ql
import numpy as np
import math


class SviPricingModel:

    def __init__(self, sviVolSurface,underlyingset, daycounter, calendar ,maturity_dates,
                 optiontype,contractType):
        self.daycounter = daycounter
        self.calendar = calendar
        self.contractType = contractType
        self.sviVolSurface = sviVolSurface
        self.underlyingset = underlyingset
        self.maturity_dates = maturity_dates

    def black_var_surface(self):
        black_var_surface = self.sviVolSurface.get_black_var_surface(self.underlyingset, self.contractType,
                                                                     self.maturity_dates)
        return black_var_surface
    # 计算全Delta
    def calculate_total_delta(self,evaluation,option,engineType,spot,strike,maturitydt,dS):

        process = evaluation.get_bsmprocess(self.daycounter,ql.SimpleQuote(spot),self.black_var_surface())
        engine = OptionEngine(process,engineType).engine
        option.setPricingEngine(engine)
        dSigma_dS = self.calculate_dSigma_dS(evaluation.evalDate,strike,maturitydt,dS)
        vega = option.vega()
        delta_tot = option.delta() + vega*dSigma_dS
        return delta_tot


    # 计算Effective Delta
    def calculate_effective_delta(self,evaltion,option,engineType,spot, dS=0.001):
        vol_surface1 = self.sviVolSurface.get_black_var_surface(
            self.underlyingset,self.contractType,self.maturity_dates,dS)
        vol_surface2 = self.sviVolSurface.get_black_var_surface(
            self.underlyingset,self.contractType,self.maturity_dates,-dS)
        process1 = evaltion.get_bsmprocess(self.daycounter,ql.SimpleQuote(spot+dS),vol_surface1)
        process2 = evaltion.get_bsmprocess(self.daycounter,ql.SimpleQuote(spot-dS),vol_surface2)
        engine1 = OptionEngine(process1,engineType).engine
        engine2 = OptionEngine(process2,engineType).engine
        option.setPricingEngine(engine1)
        price1 = option.NPV()
        option.setPricingEngine(engine2)
        price2 = option.NPV()
        engine1 = ''
        engine2 = ''
        delta_eff = (price1-price2)/(2*dS)
        return delta_eff


    def calculate_dSigma_dS(self,evalDate, strike,maturitydt, dS=0.001):
        vol_surface1 = self.sviVolSurface.get_black_var_surface(
            self.underlyingset,self.contractType,self.maturity_dates,dS)
        vol_surface2 = self.sviVolSurface.get_black_var_surface(
            self.underlyingset,self.contractType,self.maturity_dates,-dS)
        ttm = self.daycounter.yearFraction(evalDate,maturitydt)
        vol1 = vol_surface1.blackVol(ttm,strike)
        vol2 = vol_surface2.blackVol(ttm,strike)
        dSigma_dS = (vol1-vol2)/(2*dS)
        return dSigma_dS





































