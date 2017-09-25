from Utilities import utilities as util
import QuantLib as ql
import numpy as np


class StaticHedgePortfolio:

    def __init__(self,exotic_option):
        self.exoticOption = exotic_option
        #self.staticPortfolio = portfolio # portfolio = ql.CompositeInstrument()
        #self.instrumentRatio = instrument_ratio # {instrumentId:shareNo}


    def get_portfolio_mtm(self,instrument_prices):
        # port_dic = {instrumentId:shareNo}
        portfolio_mtm = 0.0
        for instrumentId in instrument_prices.keys():
            ratio = self.instrumentRatio.get(instrumentId)
            price = instrument_prices.get(instrumentId)
            portfolio_mtm += ratio*price
        return portfolio_mtm


    def set_static_portfolio(self,evaluation,spot,vol_ts,call_strikes,put_strikes):
        portfolio = ql.CompositeInstrument()
        instrument_ratio = {}
        optionType = self.exoticOption.optionType
        barrierType = self.exoticOption.barrierType
        if optionType == ql.Option.Call:
            if barrierType == ql.Barrier.DownOut:
                portfolio, instrument_ratio = self.knock_out_call(
                    portfolio,instrument_ratio,evaluation,spot,vol_ts,call_strikes,put_strikes)
        self.staticPortfolio = portfolio
        self.instrumentRatio = instrument_ratio


    def knock_out_call(self,portfolio,instrument_ratio,evaluation,spot,vol_ts,call_strikes=[],put_strikes=[]):
        barrier = self.exoticOption.barrier
        strike = self.exoticOption.strike
        maturitydt = self.exoticOption.maturitydt
        evalDate = evaluation.evalDate
        daycounter = evaluation.daycounter
        rf = util.get_rf_tbcurve(evalDate, daycounter, maturitydt)
        ttm = daycounter.yearFraction(evalDate, maturitydt)
        underlying = ql.SimpleQuote(spot)
        process = evaluation.get_bsmprocess(daycounter, underlying, vol_ts)
        european_engine = ql.AnalyticEuropeanEngine(process)
        exercise = ql.EuropeanExercise(maturitydt)
        if len(call_strikes) == 0:
            k_call = strike
        else:
            k_call = util.get_closest_strike(call_strikes, strike)
        payoff = ql.PlainVanillaPayoff(ql.Option.Call, k_call)
        call = ql.EuropeanOption(payoff, exercise)
        call.setPricingEngine(european_engine)
        instrument_ratio.update({'call-' + str(k_call): 1.0})
        portfolio.add(call)
        b_forward = ((barrier * np.exp(rf * ttm)) ** 2) / k_call
        if len(put_strikes) == 0:
            k_put = b_forward
        else:
            k_put = util.get_closest_strike(put_strikes, b_forward)
        put_payoff = ql.PlainVanillaPayoff(ql.Option.Put, k_put)
        put = ql.EuropeanOption(put_payoff, exercise)
        put.setPricingEngine(european_engine)
        underlying.setValue(barrier)
        callprice_at_barrier = call.NPV()
        putprice_at_barrier = put.NPV()
        put_ratio = callprice_at_barrier / putprice_at_barrier
        portfolio.subtract(put, put_ratio)
        instrument_ratio.update({'put-' + str(k_put): -put_ratio})
        return portfolio,instrument_ratio
