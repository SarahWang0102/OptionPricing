from Utilities.utilities import *
from bs_model.bs_estimate_vol import estimiate_bs_constant_vol
import QuantLib as ql
import timeit
import os
import pickle


start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()


begDate = ql.Date(1, 9, 2015)
#begDate = ql.Date(18, 7, 2017)
endDate = ql.Date(20, 7, 2017)
evalDate = begDate

estimatied_vols = {}
while evalDate < endDate:
    print('Start : ', evalDate)

    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    ql.Settings.instance().evaluationDate = evalDate
    try:
        print(evalDate)

        estimate_vol, min_sse = estimiate_bs_constant_vol(evalDate, calendar, daycounter)
        estimatied_vols.update({to_dt_date(evalDate):estimate_vol})
        print(estimate_vol)
    except Exception as e:
        print(e)
        continue

print('estimatied_vols = ',estimatied_vols)
stop = timeit.default_timer()
print('calibration time : ',stop-start)

with open(os.getcwd()+'/intermediate_data/total_hedging_bs_estimated_vols.pickle','wb') as f:
    pickle.dump([estimatied_vols],f)


