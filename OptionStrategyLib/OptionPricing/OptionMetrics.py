import QuantLib as ql
from OptionStrategyLib.OptionPricing import OptionPricingUtil as util

class OptionMetrics:

    def __init__(self, option):
        self.Option = option

    def implied_vol(self,evaluation,rf, spot_price, option_price,engineType):

        ql_evalDate = evaluation.evalDate
        ql.Settings.instance().evaluationDate = ql_evalDate
        calendar = evaluation.calendar
        daycounter = evaluation.daycounter
        option = self.Option.option_ql
        flat_vol_ts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(ql_evalDate, calendar, 0.0, daycounter))
        dividend_ts = ql.YieldTermStructureHandle(
            ql.FlatForward(ql_evalDate, 0.0, daycounter))
        yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(ql_evalDate, rf, daycounter))
        process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot_price)), dividend_ts, yield_ts,
                                               flat_vol_ts)
        engine = util.get_engine(process, engineType)
        option.setPricingEngine(engine)
        try:
            implied_vol = option.impliedVolatility(option_price, process, 1.0e-4, 300, 0.0, 10.0)
        except RuntimeError as e:
            print('calculate iv failed : ', e)
            implied_vol = 0.0
        return implied_vol

    def delta(self,evaluation,rf, spot_price, option_price,engineType,implied_vol):
        option = self.Option.option_ql
        # if implied_vol == None :
        #     implied_vol = self.implied_vol(evaluation,rf, spot_price, option_price, engineType)
        process = evaluation.get_bsmprocess_cnstvol(rf,spot_price, implied_vol)
        engine = util.get_engine(process,engineType)
        option.setPricingEngine(engine)
        delta = option.delta()
        return delta

    def effective_delta(self,evaluation,rf ,spot_price, option_price, engineType,
                        implied_vol, dS=0.001):
        option_ql = self.Option.option_ql
        # if implied_vol == None :
        #     implied_vol = self.implied_vol(evaluation,rf, spot_price, option_price, engineType)
        process1 = evaluation.get_bsmprocess_cnstvol(rf,spot_price+dS, implied_vol)
        process2 = evaluation.get_bsmprocess_cnstvol(rf,spot_price-dS, implied_vol)
        engine1 = util.get_engine(process1,engineType)
        engine2 = util.get_engine(process2,engineType)
        option_ql.setPricingEngine(engine1)
        option_price1 = option_ql.NPV()
        option_ql.setPricingEngine(engine2)
        option_price2 = option_ql.NPV()
        delta_eff = (option_price1-option_price2)/(2*dS)
        return delta_eff

    def theta(self,evaluation,rf ,spot_price, option_price, engineType,
              implied_vol):
        option = self.Option.option_ql
        # if implied_vol == None:
        #     implied_vol = self.implied_vol(evaluation, rf, spot_price, option_price, engineType)
        # print(implied_vol)
        process = evaluation.get_bsmprocess_cnstvol(rf, spot_price, implied_vol)
        engine = util.get_engine(process, engineType)
        option.setPricingEngine(engine)
        theta = option.theta()
        return theta

    def vega(self,evaluation,rf ,spot_price, option_price, engineType,
              implied_vol):
        option = self.Option.option_ql
        # if implied_vol == None:
        #     implied_vol = self.implied_vol(evaluation, rf, spot_price, option_price, engineType)
        process = evaluation.get_bsmprocess_cnstvol(rf, spot_price, implied_vol)
        engine = util.get_engine(process, engineType)
        option.setPricingEngine(engine)
        vega = option.vega()
        return vega
