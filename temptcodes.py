import matplotlib.pyplot as plt
import operator
import plot_util as pu
from SVI_Calibration_Util import *

w.start()
# Evaluation Settings
calendar   = ql.China()
daycounter = ql.ActualActual()

#endDate = ql.Date(4,8,2016)
endDate  = ql.Date(20,7,2017)
#evalDate = endDate
evalDate = ql.Date(7,1,2015)
#evalDate = ql.Date(7,6,2017)
#evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
#begDate  = calendar.advance(evalDate, ql.Period(1, ql.Weeks))


while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Weeks))
    ql.Settings.instance().evaluationDate = evalDate
    try:
        curve = get_curve_treasuryBond(evalDate, daycounter)

    except:
        print('Warning:',evalDate,' get Spread failed')
        continue
