import QuantLib as ql


def get_engine(bsmprocess, engineType):
    if engineType == 'AnalyticEuropeanEngine':
        engine = ql.AnalyticEuropeanEngine(bsmprocess)
    elif engineType == 'BinomialVanillaEngine':
        engine = ql.BinomialVanillaEngine(bsmprocess, 'crr', 801)
    elif engineType == 'AnalyticBarrierEngine':
        engine = ql.AnalyticBarrierEngine(bsmprocess)
    elif engineType == 'BinomialBarrierEngine':
        engine = ql.BinomialBarrierEngine(bsmprocess, 'crr', 801)
    else:
        engine = None
    return engine
