import svi_prepare_vol_data as svi_data
import QuantLib as ql
import numpy as np
import math
# Evaluation Settings
evalDate = ql.Date(14,7,2017)
maturityDate = ql.Date(27,12,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
S0 = 2.5
strike = S0

rf_Ks_months = svi_data.calculate_PCParity_riskFreeRate(evalDate, daycounter, calendar)
print(rf_Ks_months.get(3).get(2.45))