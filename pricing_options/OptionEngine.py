import QuantLib as ql
from Utilities.svi_read_data import get_curve_treasury_bond
class OptionEngine:

    def __init__(self,bsmprocess,engineType):
        self.engine = self.get_engine(bsmprocess,engineType)

    def get_engine(self,bsmprocess,engineType):
        if engineType == 'AnalyticEuropeanEngine':
            engine = ql.AnalyticEuropeanEngine(bsmprocess)
        elif engineType == 'AnalyticBarrierEngine':
            engine = ql.AnalyticBarrierEngine(bsmprocess)
        elif engineType == 'BinomialBarrierEngine':
            engine = ql.BinomialBarrierEngine(bsmprocess,'crr',801)
        elif engineType == 'BinomialEuropeanEngine':
            engine = ql.BinomialVanillaEngine(bsmprocess,'crr',801)
        else:
            engine = ''
        return engine
