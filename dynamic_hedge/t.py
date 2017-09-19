import pandas as pd
import os
import QuantLib as ql
import datetime
from Utilities import svi_prepare_vol_data as vol_data

calendar = ql.China()
evalDate = ql.Date(19,7,2017)
daycounter = ql.ActualActual()
call_vols,put_vols,expiration_dates,underlying_prices,curve = vol_data.get_call_put_impliedVols_m(evalDate,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.05,show=True)
print(call_vols)
print(put_vols)