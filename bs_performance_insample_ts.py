import svi_read_data as wind_data
import QuantLib as ql
from bs_estimate_vol import calulate_market_model_price_sse, estimiate_bs_constant_vol

begDate = ql.Date(1, 12, 2016)
endDate = ql.Date(20, 7, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()
sse_container = {}
evalDate = begDate
while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    ql.Settings.instance().evaluationDate = evalDate
    try:
        vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = wind_data.get_wind_data(evalDate)
        curve = wind_data.get_curve_treasury_bond(evalDate, daycounter)
        estimate_vol, min_sse = estimiate_bs_constant_vol(evalDate, calendar, daycounter)
    except:
        continue
    #print(estimate_vol, ' ', min_sse)  # 0.15410000000009316   0.011299317884210248
    yield_ts = ql.YieldTermStructureHandle(curve)
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, estimate_vol, daycounter))
    try:
        sse = calulate_market_model_price_sse(
            spot, mktData, mktFlds, optionData, optionFlds, optionids, yield_ts, dividend_ts, flat_vol_ts)
    except:
        sse = 'NAN'
    sse_container.update({evalDate: sse})
    print('SSE : ', sse)
print("=" * 80)
print(" %15s %25s " % ("EvalDate", "SSE"))
for date in sse_container.keys():
    e = sse_container.get(date)
    if e == 'NAN': continue
    print(" %15s %25s " % (str(date), round(e, 6)))
print("-" * 80)

print('sse_container = ',sse_container)