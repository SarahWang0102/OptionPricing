import QuantLib as ql
from Utilities.svi_read_data import get_curve_treasury_bond


class OptionPlainEuropean:
    def __init__(self, strike, maturitydt, optionType):
        self.strike = strike
        self.maturitydt = maturitydt
        self.optionType = optionType
        exercise = ql.EuropeanExercise(self.maturitydt)
        payoff = ql.PlainVanillaPayoff(self.optionType, self.strike)
        option = ql.EuropeanOption(payoff, exercise)
        self.option_ql = option


class OptionBarrierEuropean:
    def __init__(self, strike, maturitydt, optionType, barrier, barrierType):
        self.strike = strike
        self.maturitydt = maturitydt
        self.optionType = optionType
        self.barrier = barrier
        self.barrierType = barrierType
        exercise = ql.EuropeanExercise(maturitydt)
        self.exercise = exercise
        payoff = ql.PlainVanillaPayoff(optionType, strike)
        self.payoff = payoff
        barrieroption = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
        self.option_ql = barrieroption