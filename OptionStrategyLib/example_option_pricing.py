import datetime
import QuantLib as ql
from OptionStrategyLib.OptionPricing.OptionMetrics import OptionMetrics
from OptionStrategyLib.OptionPricing.Options import OptionPlainEuropean
from OptionStrategyLib.OptionPricing.Evaluation import Evaluation


##################################################################################################
evalDate = datetime.date(2018,1,2)
ql_evalDate = ql.Date(evalDate.day,evalDate.month,evalDate.year)
rf = 0.03
calendar = ql.China()
daycounter = ql.ActualActual()
evaluation = Evaluation(ql_evalDate,daycounter,calendar)
engineType = 'AnalyticEuropeanEngine'
##################################################################################################
spot_price = 2.907
option_price = 0.08
strike = 2.9
ql_mdt = ql.Date(28,2,2018)
##################################################################################################
option = OptionPlainEuropean(strike,ql_mdt,ql.Option.Call)
option_metrics = OptionMetrics(option)
iv = option_metrics.implied_vol(evaluation,rf, spot_price, option_price)
delta = option_metrics.delta(evaluation,rf, spot_price, option_price,engineType)
theta = option_metrics.theta(evaluation,rf, spot_price, option_price,engineType)
vega = option_metrics.vega(evaluation,rf, spot_price, option_price,engineType)
# eff_delta = option_metrics.effective_delta(evaluation,rf ,spot_price, option_price, engineType)
print('implied vol : ', iv)
print('delta : ', delta)
print('theta : ', theta)
print('vega : ', vega)

