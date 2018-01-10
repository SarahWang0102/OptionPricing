import QuantLib as ql

class Evaluation:

    def __init__(self,evalDate,daycounter,calendar):
        self.evalDate = evalDate
        self.daycounter = daycounter
        self.calendar = calendar
        ql.Settings.instance().evaluationDate = evalDate

    def get_bsmprocess(self,rf, spot_price,vol_surface):
        yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, rf, self.daycounter))
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, 0.0, self.daycounter))
        vol_ts = ql.BlackVolTermStructureHandle(vol_surface)
        process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot_price)), dividend_ts,yield_ts, vol_ts)
        return process

    def get_bsmprocess_cnstvol(self,rf,spot_price,vol):
        yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, rf, self.daycounter))
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(self.evalDate, 0.0, self.daycounter))
        vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(self.evalDate, self.calendar, vol, self.daycounter))
        process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot_price)), dividend_ts,yield_ts, vol_ts)
        return process
