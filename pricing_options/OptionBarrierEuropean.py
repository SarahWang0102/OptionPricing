import QuantLib as ql
from Utilities.svi_read_data import get_curve_treasury_bond

class OptionBarrierEuropean:

    def __init__(self, strike, maturitydt, optionType,barrier,barrierType):
        self.strike = strike
        self.maturitydt = maturitydt
        self.optionType = optionType
        self.barrier = barrier
        self.barrierType = barrierType
        exercise = ql.EuropeanExercise(maturitydt)
        payoff = ql.PlainVanillaPayoff(optionType, strike)
        barrieroption = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
        self.option = barrieroption


'''
    def get_european_option(self):
        exercise = ql.EuropeanExercise(self.maturitydt)
        payoff = ql.PlainVanillaPayoff(self.optionType, self.strike)
        option = ql.EuropeanOption(payoff, exercise)
        return option

'''
