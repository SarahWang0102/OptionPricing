import Utilities.svi_read_data as wind_data
import matplotlib.pyplot as plt
from Utilities.utilities import *
import Utilities.svi_prepare_vol_data as svi_data
import Utilities.svi_calibration_utility as svi_util
import numpy as np
from WindPy import w
import datetime
import pickle
import os


with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_params_calls_noZeroVol.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_dates_calls_noZeroVol.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/m_hedging_daily_svi_dataset_calls_noZeroVol.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

#print(daily_params)

print(daily_svi_dataset.get(datetime.date(2017, 3, 31)))