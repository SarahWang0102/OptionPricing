import QuantLib as ql
from Utilities.svi_read_data import get_curve_treasury_bond

class Evaluation:

    def __init__(self,evalDate,daycounter,calendar):
        self.evalDate = evalDate
        self.daycounter = daycounter
        self.calendar = calendar
        ql.Settings.instance().evaluationDate = evalDate

    def get_bsmprocess(self,daycounter,underlying,vol_surface):
        yield_ts = ql.YieldTermStructureHandle(get_curve_treasury_bond(self.evalDate, daycounter))
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, 0.0, daycounter))
        vol_ts = ql.BlackVolTermStructureHandle(vol_surface)
        process = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying), dividend_ts,yield_ts, vol_ts)
        return process

    def get_bsmprocess_cnstvol(self,daycounter,calendar,underlying,vol):
        yield_ts = ql.YieldTermStructureHandle(get_curve_treasury_bond(self.evalDate, daycounter))
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, 0.0, daycounter))
        vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(self.evalDate, calendar,vol, daycounter))
        process = ql.BlackScholesMertonProcess(ql.QuoteHandle(underlying), dividend_ts,yield_ts, vol_ts)
        return process

    def get_bsmprocess_rf(self,daycounter,underlying,vol_surface,rf):
        yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, rf, daycounter))
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, 0.0, daycounter))
        vol_ts = ql.BlackVolTermStructureHandle(vol_surface)
        process = ql.BlackScholesMertonProcess(underlying, dividend_ts,yield_ts, vol_ts)
        return process