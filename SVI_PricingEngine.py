from VolatilityData import *

calendar    = ql.China()
daycounter  = ql.ActualActual()
evalDate    = ql.Date(12,6,2017)
curve       = get_curve_depo(evalDate, daycounter)
yield_ts    = ql.YieldTermStructureHandle(curve)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
vol         = 0.0
a_star,b_star,sigma_star,rho_star,m_star = 0.0,0.0958120642083,0.000473009803263,1.0,-0.0766962382514
# Calculate SVI model volatility
flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, vol, daycounter))