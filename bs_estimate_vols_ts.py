import svi_read_data as wind_data
from hedging_utility import get_spot_price,calculate_cash_position,calculate_delta_bs,calculate_hedging_error
from utilities import convert_datelist_from_datetime_to_ql as to_ql_dates
from utilities import convert_datelist_from_ql_to_datetime as to_dt_dates
from utilities import convert_date_from_ql_to_datetime as to_dt_date
from utilities import convert_date_from_datetime_to_ql as to_ql_date
from bs_estimate_vol import estimiate_bs_constant_vol
import svi_prepare_vol_data as svi_data
import svi_calibration_utility as svi_util
import QuantLib as ql
import pandas as pd
import math
import numpy as np
from WindPy import w
import datetime
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


