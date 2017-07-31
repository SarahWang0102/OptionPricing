import svi_read_data as wind_data
import QuantLib as ql
from bs_estimate_vol import calulate_market_model_price_sse

evalDate = ql.Date(14,7,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
# estimate_vol,min_sse = estimiate_bs_constant_vol(evalDate, calendar, daycounter)
#print(estimate_vol,' ',min_sse) # 0.15410000000009316   0.011299317884210248

estimate_vol = 0.15410000000009316
vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = wind_data.get_wind_data(evalDate)
ql.Settings.instance().evaluationDate = evalDate
curve       = wind_data.get_curve_treasury_bond(evalDate, daycounter)
yield_ts    = ql.YieldTermStructureHandle(curve)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, estimate_vol, daycounter))
print("-" * 80)
print("BS In Sample Performance:")
print("=" * 80)
print(" %15s %25s %25s " % ("market price","model price", "square error(* e-4)"))
sse        = calulate_market_model_price_sse(
                spot, mktData, mktFlds, optionData, optionFlds, optionids, yield_ts, dividend_ts, flat_vol_ts)
print("-" * 80)
print(" %15s %25s %25s " % ("","SSE:", round(sse,6)))
print("-" * 80)