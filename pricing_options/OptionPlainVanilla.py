import QuantLib as ql
from Utilities.svi_read_data import get_curve_treasury_bond

class OptionPlainVanilla:

    def __init__(self, strike, maturitydt, optionType):
        self.strike = strike
        self.maturitydt = maturitydt
        self.optionType = optionType

    def get_european_option(self):
        exercise = ql.EuropeanExercise(self.maturitydt)
        payoff = ql.PlainVanillaPayoff(self.optionType, self.strike)
        option = ql.EuropeanOption(payoff, exercise)
        return option


