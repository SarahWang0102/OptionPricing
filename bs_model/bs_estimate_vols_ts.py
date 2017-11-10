from Utilities.utilities import *
from bs_model.bs_estimate_vol import estimiate_bs_constant_vol
import QuantLib as ql
import timeit
import os
import pickle

with open(os.path.abspath('..') +'/intermediate_data/total_hedging_bs_estimated_vols.pickle','rb') as f:
    estimated_vols = pickle.load(f)[0]


start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()


evalDate = ql.Date(1, 1, 2016)
#evalDate = ql.Date(28, 9, 2017)
endDate = ql.Date(29, 9, 2017)

#estimatied_vols = {}
while evalDate < endDate:
    print('Start : ', evalDate)

    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    if to_dt_date(evalDate) in estimated_vols.keys(): continue
    ql.Settings.instance().evaluationDate = evalDate
    try:
        print(evalDate)

        estimate_vol, min_sse = estimiate_bs_constant_vol(evalDate, calendar, daycounter)
        estimated_vols.update({to_dt_date(evalDate):estimate_vol})
        print(estimate_vol)
    except Exception as e:
        print(e)
        continue

print('estimatied_vols = ',estimated_vols)
stop = timeit.default_timer()
print('calibration time : ',stop-start)

with open(os.path.abspath('..') +'/intermediate_data/total_hedging_bs_estimated_vols.pickle','wb') as f:
    pickle.dump([estimated_vols],f)


