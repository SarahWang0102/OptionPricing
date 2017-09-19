import Utilities.hedging_utility as hedge_util
from Utilities.utilities import *
import Utilities.svi_prepare_vol_data as svi_data
import Utilities.svi_calibration_utility as svi_util
import Utilities.hedging_performance_utility as hp_util
import QuantLib as ql
import pandas as pd
import math
import numpy as np
import datetime
import timeit
import os
import pickle


start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()

def Date(d,m,y):
    return ql.Date(d,m,y)

with open(os.path.abspath('..') +'/intermediate_data/total_hedging_daily_params_puts.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
#with open(os.getcwd()+'/intermediate_data/total_hedging_dates_puts.pickle','rb') as f:
#    dates = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_bs_estimated_vols.pickle','rb') as f:
    estimated_vols = pickle.load(f)[0]

# Hedge option using underlying 50ETF
daily_hedge_errors = {}
daily_pct_hedge_errors = {}
option_last_close_Ms = {}
#print(len(estimated_vols))
# 3-Day smoothing
#dates = [datetime.date(2015, 9, 15), datetime.date(2015, 9, 16), datetime.date(2015, 9, 17), datetime.date(2015, 9, 18), datetime.date(2015, 9, 21), datetime.date(2015, 9, 22), datetime.date(2015, 10, 8), datetime.date(2015, 10, 9), datetime.date(2015, 10, 12), datetime.date(2015, 10, 13), datetime.date(2015, 10, 14), datetime.date(2015, 10, 15), datetime.date(2015, 10, 16), datetime.date(2015, 10, 19), datetime.date(2015, 10, 20), datetime.date(2015, 10, 21), datetime.date(2015, 10, 23), datetime.date(2015, 10, 26), datetime.date(2015, 10, 27), datetime.date(2015, 11, 2), datetime.date(2015, 11, 3), datetime.date(2015, 11, 4), datetime.date(2015, 11, 6), datetime.date(2015, 11, 9), datetime.date(2015, 11, 10), datetime.date(2015, 11, 11), datetime.date(2015, 11, 12), datetime.date(2015, 11, 13), datetime.date(2015, 11, 16), datetime.date(2015, 11, 17), datetime.date(2015, 11, 18), datetime.date(2015, 11, 19), datetime.date(2015, 11, 20), datetime.date(2015, 11, 23), datetime.date(2015, 11, 24), datetime.date(2015, 12, 1), datetime.date(2015, 12, 2), datetime.date(2015, 12, 3), datetime.date(2015, 12, 4), datetime.date(2015, 12, 7), datetime.date(2015, 12, 8), datetime.date(2015, 12, 9), datetime.date(2015, 12, 10), datetime.date(2015, 12, 11), datetime.date(2015, 12, 14), datetime.date(2015, 12, 15), datetime.date(2015, 12, 16), datetime.date(2015, 12, 17), datetime.date(2015, 12, 18), datetime.date(2015, 12, 21), datetime.date(2015, 12, 22), datetime.date(2016, 1, 4), datetime.date(2016, 1, 5), datetime.date(2016, 1, 6), datetime.date(2016, 1, 7), datetime.date(2016, 1, 8), datetime.date(2016, 1, 11), datetime.date(2016, 1, 12), datetime.date(2016, 1, 13), datetime.date(2016, 1, 14), datetime.date(2016, 1, 15), datetime.date(2016, 1, 18), datetime.date(2016, 1, 19), datetime.date(2016, 1, 20), datetime.date(2016, 1, 21), datetime.date(2016, 1, 22), datetime.date(2016, 1, 25), datetime.date(2016, 2, 1), datetime.date(2016, 2, 2), datetime.date(2016, 2, 3), datetime.date(2016, 2, 5), datetime.date(2016, 2, 15), datetime.date(2016, 2, 16), datetime.date(2016, 2, 17), datetime.date(2016, 2, 18), datetime.date(2016, 2, 19), datetime.date(2016, 2, 22), datetime.date(2016, 2, 23), datetime.date(2016, 3, 1), datetime.date(2016, 3, 2), datetime.date(2016, 3, 3), datetime.date(2016, 3, 4), datetime.date(2016, 3, 7), datetime.date(2016, 3, 11), datetime.date(2016, 3, 14), datetime.date(2016, 3, 15), datetime.date(2016, 3, 16), datetime.date(2016, 3, 17), datetime.date(2016, 3, 18), datetime.date(2016, 3, 21), datetime.date(2016, 3, 22), datetime.date(2016, 4, 1), datetime.date(2016, 4, 5), datetime.date(2016, 4, 6), datetime.date(2016, 4, 7), datetime.date(2016, 4, 8), datetime.date(2016, 4, 11), datetime.date(2016, 4, 12), datetime.date(2016, 4, 13), datetime.date(2016, 4, 14), datetime.date(2016, 4, 15), datetime.date(2016, 4, 18), datetime.date(2016, 4, 19), datetime.date(2016, 4, 20), datetime.date(2016, 4, 21), datetime.date(2016, 4, 22), datetime.date(2016, 4, 25), datetime.date(2016, 4, 26), datetime.date(2016, 5, 9), datetime.date(2016, 5, 10), datetime.date(2016, 5, 11), datetime.date(2016, 5, 12), datetime.date(2016, 5, 13), datetime.date(2016, 5, 16), datetime.date(2016, 5, 17), datetime.date(2016, 5, 18), datetime.date(2016, 5, 19), datetime.date(2016, 5, 20), datetime.date(2016, 5, 23), datetime.date(2016, 5, 24), datetime.date(2016, 6, 1), datetime.date(2016, 6, 2), datetime.date(2016, 6, 3), datetime.date(2016, 6, 6), datetime.date(2016, 6, 7), datetime.date(2016, 6, 8), datetime.date(2016, 6, 13), datetime.date(2016, 6, 14), datetime.date(2016, 6, 15), datetime.date(2016, 6, 16), datetime.date(2016, 6, 17), datetime.date(2016, 6, 20), datetime.date(2016, 6, 21), datetime.date(2016, 7, 1), datetime.date(2016, 7, 4), datetime.date(2016, 7, 5), datetime.date(2016, 7, 6), datetime.date(2016, 7, 7), datetime.date(2016, 7, 8), datetime.date(2016, 7, 11), datetime.date(2016, 7, 12), datetime.date(2016, 7, 13), datetime.date(2016, 7, 14), datetime.date(2016, 7, 15), datetime.date(2016, 7, 18), datetime.date(2016, 7, 19), datetime.date(2016, 7, 20), datetime.date(2016, 7, 21), datetime.date(2016, 7, 22), datetime.date(2016, 7, 25), datetime.date(2016, 7, 26), datetime.date(2016, 8, 1), datetime.date(2016, 8, 2), datetime.date(2016, 8, 3), datetime.date(2016, 8, 5), datetime.date(2016, 8, 8), datetime.date(2016, 8, 9), datetime.date(2016, 8, 10), datetime.date(2016, 8, 11), datetime.date(2016, 8, 12), datetime.date(2016, 8, 15), datetime.date(2016, 8, 16), datetime.date(2016, 8, 17), datetime.date(2016, 8, 18), datetime.date(2016, 8, 19), datetime.date(2016, 8, 22), datetime.date(2016, 8, 23), datetime.date(2016, 9, 1), datetime.date(2016, 9, 2), datetime.date(2016, 9, 5), datetime.date(2016, 9, 6), datetime.date(2016, 9, 7), datetime.date(2016, 9, 8), datetime.date(2016, 9, 9), datetime.date(2016, 9, 12), datetime.date(2016, 9, 13), datetime.date(2016, 9, 14), datetime.date(2016, 9, 19), datetime.date(2016, 9, 20), datetime.date(2016, 9, 21), datetime.date(2016, 9, 22), datetime.date(2016, 9, 23), datetime.date(2016, 9, 26), datetime.date(2016, 9, 27), datetime.date(2016, 10, 10), datetime.date(2016, 10, 11), datetime.date(2016, 10, 12), datetime.date(2016, 10, 13), datetime.date(2016, 10, 14), datetime.date(2016, 10, 17), datetime.date(2016, 10, 18), datetime.date(2016, 10, 19), datetime.date(2016, 10, 20), datetime.date(2016, 10, 21), datetime.date(2016, 10, 24), datetime.date(2016, 10, 25), datetime.date(2016, 11, 1), datetime.date(2016, 11, 2), datetime.date(2016, 11, 3), datetime.date(2016, 11, 7), datetime.date(2016, 11, 8), datetime.date(2016, 11, 9), datetime.date(2016, 11, 10), datetime.date(2016, 11, 11), datetime.date(2016, 11, 14), datetime.date(2016, 11, 15), datetime.date(2016, 11, 16), datetime.date(2016, 11, 17), datetime.date(2016, 11, 18), datetime.date(2016, 11, 21), datetime.date(2016, 11, 22), datetime.date(2016, 12, 1), datetime.date(2016, 12, 2), datetime.date(2016, 12, 5), datetime.date(2016, 12, 6), datetime.date(2016, 12, 7), datetime.date(2016, 12, 8), datetime.date(2016, 12, 9), datetime.date(2016, 12, 12), datetime.date(2016, 12, 13), datetime.date(2016, 12, 14), datetime.date(2016, 12, 15), datetime.date(2016, 12, 16), datetime.date(2016, 12, 19), datetime.date(2016, 12, 20), datetime.date(2016, 12, 21), datetime.date(2016, 12, 22), datetime.date(2016, 12, 23), datetime.date(2016, 12, 26), datetime.date(2016, 12, 27), datetime.date(2017, 1, 3), datetime.date(2017, 1, 4), datetime.date(2017, 1, 5), datetime.date(2017, 1, 6), datetime.date(2017, 1, 9), datetime.date(2017, 1, 10), datetime.date(2017, 1, 11), datetime.date(2017, 1, 12), datetime.date(2017, 1, 13), datetime.date(2017, 1, 16), datetime.date(2017, 1, 17), datetime.date(2017, 1, 18), datetime.date(2017, 1, 19), datetime.date(2017, 1, 20), datetime.date(2017, 1, 23), datetime.date(2017, 1, 24), datetime.date(2017, 2, 3), datetime.date(2017, 2, 6), datetime.date(2017, 2, 7), datetime.date(2017, 2, 9), datetime.date(2017, 2, 10), datetime.date(2017, 2, 13), datetime.date(2017, 2, 14), datetime.date(2017, 2, 15), datetime.date(2017, 2, 16), datetime.date(2017, 2, 17), datetime.date(2017, 2, 20), datetime.date(2017, 2, 21), datetime.date(2017, 3, 1), datetime.date(2017, 3, 2), datetime.date(2017, 3, 3), datetime.date(2017, 3, 6), datetime.date(2017, 3, 7), datetime.date(2017, 3, 8), datetime.date(2017, 3, 9), datetime.date(2017, 3, 10), datetime.date(2017, 3, 13), datetime.date(2017, 3, 14), datetime.date(2017, 3, 15), datetime.date(2017, 3, 16), datetime.date(2017, 3, 17), datetime.date(2017, 3, 20), datetime.date(2017, 3, 21), datetime.date(2017, 4, 5), datetime.date(2017, 4, 6), datetime.date(2017, 4, 7), datetime.date(2017, 4, 10), datetime.date(2017, 4, 11), datetime.date(2017, 4, 12), datetime.date(2017, 4, 13), datetime.date(2017, 4, 14), datetime.date(2017, 4, 17), datetime.date(2017, 4, 18), datetime.date(2017, 4, 19), datetime.date(2017, 4, 20), datetime.date(2017, 4, 21), datetime.date(2017, 4, 24), datetime.date(2017, 4, 25), datetime.date(2017, 5, 2), datetime.date(2017, 5, 3), datetime.date(2017, 5, 4), datetime.date(2017, 5, 8), datetime.date(2017, 5, 9), datetime.date(2017, 5, 10), datetime.date(2017, 5, 11), datetime.date(2017, 5, 12), datetime.date(2017, 5, 15), datetime.date(2017, 5, 16), datetime.date(2017, 5, 17), datetime.date(2017, 5, 18), datetime.date(2017, 5, 19), datetime.date(2017, 5, 22), datetime.date(2017, 5, 23), datetime.date(2017, 6, 1), datetime.date(2017, 6, 2), datetime.date(2017, 6, 5), datetime.date(2017, 6, 6), datetime.date(2017, 6, 7), datetime.date(2017, 6, 8), datetime.date(2017, 6, 9), datetime.date(2017, 6, 12), datetime.date(2017, 6, 13), datetime.date(2017, 6, 14), datetime.date(2017, 6, 15), datetime.date(2017, 6, 16), datetime.date(2017, 6, 19), datetime.date(2017, 6, 20), datetime.date(2017, 6, 21), datetime.date(2017, 6, 22), datetime.date(2017, 6, 23), datetime.date(2017, 6, 26), datetime.date(2017, 6, 27), datetime.date(2017, 7, 3), datetime.date(2017, 7, 4), datetime.date(2017, 7, 5), datetime.date(2017, 7, 6), datetime.date(2017, 7, 7), datetime.date(2017, 7, 10), datetime.date(2017, 7, 11), datetime.date(2017, 7, 12), datetime.date(2017, 7, 13), datetime.date(2017, 7, 14)]

dates = [datetime.date(2015, 9, 9), datetime.date(2015, 9, 10), datetime.date(2015, 9, 11), datetime.date(2015, 9, 14), datetime.date(2015, 9, 15), datetime.date(2015, 9, 16), datetime.date(2015, 9, 17), datetime.date(2015, 9, 18), datetime.date(2015, 9, 21), datetime.date(2015, 9, 22), datetime.date(2015, 10, 8), datetime.date(2015, 10, 9), datetime.date(2015, 10, 12), datetime.date(2015, 10, 13), datetime.date(2015, 10, 14), datetime.date(2015, 10, 15), datetime.date(2015, 10, 16), datetime.date(2015, 10, 19), datetime.date(2015, 10, 20), datetime.date(2015, 10, 21), datetime.date(2015, 10, 23), datetime.date(2015, 10, 26), datetime.date(2015, 10, 27), datetime.date(2015, 11, 2), datetime.date(2015, 11, 4), datetime.date(2015, 11, 5), datetime.date(2015, 11, 6), datetime.date(2015, 11, 9), datetime.date(2015, 11, 10), datetime.date(2015, 11, 11), datetime.date(2015, 11, 12), datetime.date(2015, 11, 13), datetime.date(2015, 11, 16), datetime.date(2015, 11, 17), datetime.date(2015, 11, 18), datetime.date(2015, 11, 19), datetime.date(2015, 11, 20), datetime.date(2015, 11, 23), datetime.date(2015, 11, 24), datetime.date(2015, 12, 1), datetime.date(2015, 12, 2), datetime.date(2015, 12, 3), datetime.date(2015, 12, 4), datetime.date(2015, 12, 7), datetime.date(2015, 12, 8), datetime.date(2015, 12, 9), datetime.date(2015, 12, 10), datetime.date(2015, 12, 11), datetime.date(2015, 12, 14), datetime.date(2015, 12, 15), datetime.date(2015, 12, 16), datetime.date(2015, 12, 17), datetime.date(2015, 12, 18), datetime.date(2015, 12, 21), datetime.date(2015, 12, 22), datetime.date(2016, 1, 4), datetime.date(2016, 1, 5), datetime.date(2016, 1, 6), datetime.date(2016, 1, 7), datetime.date(2016, 1, 8), datetime.date(2016, 1, 11), datetime.date(2016, 1, 12), datetime.date(2016, 1, 13), datetime.date(2016, 1, 14), datetime.date(2016, 1, 15), datetime.date(2016, 1, 18), datetime.date(2016, 1, 19), datetime.date(2016, 1, 20), datetime.date(2016, 1, 21), datetime.date(2016, 1, 22), datetime.date(2016, 1, 25), datetime.date(2016, 2, 1), datetime.date(2016, 2, 3), datetime.date(2016, 2, 4), datetime.date(2016, 2, 5), datetime.date(2016, 2, 15), datetime.date(2016, 2, 16), datetime.date(2016, 2, 17), datetime.date(2016, 2, 18), datetime.date(2016, 2, 19), datetime.date(2016, 2, 22), datetime.date(2016, 2, 23), datetime.date(2016, 3, 1), datetime.date(2016, 3, 2), datetime.date(2016, 3, 3), datetime.date(2016, 3, 7), datetime.date(2016, 3, 8), datetime.date(2016, 3, 9), datetime.date(2016, 3, 10), datetime.date(2016, 3, 11), datetime.date(2016, 3, 14), datetime.date(2016, 3, 15), datetime.date(2016, 3, 16), datetime.date(2016, 3, 17), datetime.date(2016, 3, 18), datetime.date(2016, 3, 21), datetime.date(2016, 3, 22), datetime.date(2016, 4, 1), datetime.date(2016, 4, 5), datetime.date(2016, 4, 6), datetime.date(2016, 4, 7), datetime.date(2016, 4, 8), datetime.date(2016, 4, 11), datetime.date(2016, 4, 12), datetime.date(2016, 4, 13), datetime.date(2016, 4, 14), datetime.date(2016, 4, 15), datetime.date(2016, 4, 18), datetime.date(2016, 4, 19), datetime.date(2016, 4, 20), datetime.date(2016, 4, 21), datetime.date(2016, 4, 22), datetime.date(2016, 4, 25), datetime.date(2016, 4, 26), datetime.date(2016, 5, 3), datetime.date(2016, 5, 5), datetime.date(2016, 5, 6), datetime.date(2016, 5, 9), datetime.date(2016, 5, 10), datetime.date(2016, 5, 11), datetime.date(2016, 5, 12), datetime.date(2016, 5, 13), datetime.date(2016, 5, 16), datetime.date(2016, 5, 17), datetime.date(2016, 5, 18), datetime.date(2016, 5, 19), datetime.date(2016, 5, 20), datetime.date(2016, 5, 23), datetime.date(2016, 5, 24), datetime.date(2016, 6, 1), datetime.date(2016, 6, 2), datetime.date(2016, 6, 3), datetime.date(2016, 6, 6), datetime.date(2016, 6, 7), datetime.date(2016, 6, 8), datetime.date(2016, 6, 13), datetime.date(2016, 6, 14), datetime.date(2016, 6, 15), datetime.date(2016, 6, 16), datetime.date(2016, 6, 17), datetime.date(2016, 6, 20), datetime.date(2016, 6, 21), datetime.date(2016, 7, 1), datetime.date(2016, 7, 4), datetime.date(2016, 7, 5), datetime.date(2016, 7, 6), datetime.date(2016, 7, 7), datetime.date(2016, 7, 8), datetime.date(2016, 7, 11), datetime.date(2016, 7, 12), datetime.date(2016, 7, 13), datetime.date(2016, 7, 14), datetime.date(2016, 7, 15), datetime.date(2016, 7, 18), datetime.date(2016, 7, 19), datetime.date(2016, 7, 20), datetime.date(2016, 7, 21), datetime.date(2016, 7, 22), datetime.date(2016, 7, 25), datetime.date(2016, 7, 26), datetime.date(2016, 8, 1), datetime.date(2016, 8, 3), datetime.date(2016, 8, 4), datetime.date(2016, 8, 5), datetime.date(2016, 8, 8), datetime.date(2016, 8, 9), datetime.date(2016, 8, 10), datetime.date(2016, 8, 11), datetime.date(2016, 8, 12), datetime.date(2016, 8, 15), datetime.date(2016, 8, 16), datetime.date(2016, 8, 17), datetime.date(2016, 8, 18), datetime.date(2016, 8, 19), datetime.date(2016, 8, 22), datetime.date(2016, 8, 23), datetime.date(2016, 9, 1), datetime.date(2016, 9, 2), datetime.date(2016, 9, 5), datetime.date(2016, 9, 6), datetime.date(2016, 9, 7), datetime.date(2016, 9, 8), datetime.date(2016, 9, 9), datetime.date(2016, 9, 12), datetime.date(2016, 9, 13), datetime.date(2016, 9, 14), datetime.date(2016, 9, 19), datetime.date(2016, 9, 20), datetime.date(2016, 9, 21), datetime.date(2016, 9, 22), datetime.date(2016, 9, 23), datetime.date(2016, 9, 26), datetime.date(2016, 9, 27), datetime.date(2016, 10, 10), datetime.date(2016, 10, 11), datetime.date(2016, 10, 12), datetime.date(2016, 10, 13), datetime.date(2016, 10, 14), datetime.date(2016, 10, 17), datetime.date(2016, 10, 18), datetime.date(2016, 10, 19), datetime.date(2016, 10, 20), datetime.date(2016, 10, 21), datetime.date(2016, 10, 24), datetime.date(2016, 10, 25), datetime.date(2016, 11, 1), datetime.date(2016, 11, 3), datetime.date(2016, 11, 4), datetime.date(2016, 11, 7), datetime.date(2016, 11, 8), datetime.date(2016, 11, 9), datetime.date(2016, 11, 10), datetime.date(2016, 11, 11), datetime.date(2016, 11, 14), datetime.date(2016, 11, 15), datetime.date(2016, 11, 16), datetime.date(2016, 11, 17), datetime.date(2016, 11, 18), datetime.date(2016, 11, 21), datetime.date(2016, 11, 22), datetime.date(2016, 12, 1), datetime.date(2016, 12, 2), datetime.date(2016, 12, 5), datetime.date(2016, 12, 6), datetime.date(2016, 12, 7), datetime.date(2016, 12, 8), datetime.date(2016, 12, 9), datetime.date(2016, 12, 12), datetime.date(2016, 12, 13), datetime.date(2016, 12, 14), datetime.date(2016, 12, 15), datetime.date(2016, 12, 16), datetime.date(2016, 12, 19), datetime.date(2016, 12, 20), datetime.date(2016, 12, 21), datetime.date(2016, 12, 22), datetime.date(2016, 12, 23), datetime.date(2016, 12, 26), datetime.date(2016, 12, 27), datetime.date(2017, 1, 3), datetime.date(2017, 1, 4), datetime.date(2017, 1, 5), datetime.date(2017, 1, 6), datetime.date(2017, 1, 9), datetime.date(2017, 1, 10), datetime.date(2017, 1, 11), datetime.date(2017, 1, 12), datetime.date(2017, 1, 13), datetime.date(2017, 1, 16), datetime.date(2017, 1, 17), datetime.date(2017, 1, 18), datetime.date(2017, 1, 19), datetime.date(2017, 1, 20), datetime.date(2017, 1, 23), datetime.date(2017, 1, 24), datetime.date(2017, 2, 3), datetime.date(2017, 2, 7), datetime.date(2017, 2, 8), datetime.date(2017, 2, 9), datetime.date(2017, 2, 10), datetime.date(2017, 2, 13), datetime.date(2017, 2, 14), datetime.date(2017, 2, 15), datetime.date(2017, 2, 16), datetime.date(2017, 2, 17), datetime.date(2017, 2, 20), datetime.date(2017, 2, 21), datetime.date(2017, 3, 1), datetime.date(2017, 3, 2), datetime.date(2017, 3, 3), datetime.date(2017, 3, 6), datetime.date(2017, 3, 7), datetime.date(2017, 3, 8), datetime.date(2017, 3, 9), datetime.date(2017, 3, 10), datetime.date(2017, 3, 13), datetime.date(2017, 3, 14), datetime.date(2017, 3, 15), datetime.date(2017, 3, 16), datetime.date(2017, 3, 17), datetime.date(2017, 3, 20), datetime.date(2017, 3, 21), datetime.date(2017, 4, 5), datetime.date(2017, 4, 6), datetime.date(2017, 4, 7), datetime.date(2017, 4, 10), datetime.date(2017, 4, 11), datetime.date(2017, 4, 12), datetime.date(2017, 4, 13), datetime.date(2017, 4, 14), datetime.date(2017, 4, 17), datetime.date(2017, 4, 18), datetime.date(2017, 4, 19), datetime.date(2017, 4, 20), datetime.date(2017, 4, 21), datetime.date(2017, 4, 24), datetime.date(2017, 4, 25), datetime.date(2017, 5, 2), datetime.date(2017, 5, 4), datetime.date(2017, 5, 5), datetime.date(2017, 5, 8), datetime.date(2017, 5, 9), datetime.date(2017, 5, 10), datetime.date(2017, 5, 11), datetime.date(2017, 5, 12), datetime.date(2017, 5, 15), datetime.date(2017, 5, 16), datetime.date(2017, 5, 17), datetime.date(2017, 5, 18), datetime.date(2017, 5, 19), datetime.date(2017, 5, 22), datetime.date(2017, 5, 23), datetime.date(2017, 6, 1), datetime.date(2017, 6, 2), datetime.date(2017, 6, 5), datetime.date(2017, 6, 6), datetime.date(2017, 6, 7), datetime.date(2017, 6, 8), datetime.date(2017, 6, 9), datetime.date(2017, 6, 12), datetime.date(2017, 6, 13), datetime.date(2017, 6, 14), datetime.date(2017, 6, 15), datetime.date(2017, 6, 16), datetime.date(2017, 6, 19), datetime.date(2017, 6, 20), datetime.date(2017, 6, 21), datetime.date(2017, 6, 22), datetime.date(2017, 6, 23), datetime.date(2017, 6, 26), datetime.date(2017, 6, 27), datetime.date(2017, 7, 3), datetime.date(2017, 7, 4), datetime.date(2017, 7, 5), datetime.date(2017, 7, 6), datetime.date(2017, 7, 7), datetime.date(2017, 7, 10), datetime.date(2017, 7, 11), datetime.date(2017, 7, 12), datetime.date(2017, 7, 13), datetime.date(2017, 7, 14), datetime.date(2017, 7, 17), datetime.date(2017, 7, 18), datetime.date(2017, 7, 19), datetime.date(2017, 7, 20)]
#print(len(dates))
for idx_date,date in enumerate(dates[0:len(dates)-5]):
    try:
        #print(idx_date)
        calibrate_date = to_ql_date(dates[idx_date])
        hedge_date = to_ql_date(dates[idx_date+1])
        liquidition_date = to_ql_date(dates[idx_date+4])

        # Calibration Date Dataset
        dataset_on_calibrate_date = daily_svi_dataset.get(to_dt_date(calibrate_date))
        cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_pcprs_c = dataset_on_calibrate_date

        # Liquidition Date Dataset
        dataset_on_liquidition_date = daily_svi_dataset.get(to_dt_date(liquidition_date))
        cal_vols, put_vols, maturity_dates, spot, rf_pcprs = dataset_on_liquidition_date

        # SELECT PUT OPTION DATA!!
        expiration_dates = to_ql_dates(maturity_dates)
        orgnized_data_liquidition_date = svi_util.orgnize_data_for_hedging(
            liquidition_date , daycounter, put_vols, expiration_dates, spot)
        optiontype = ql.Option.Put

        # Hedge Date Data Set
        dataset_on_hedge_date = daily_svi_dataset.get(to_dt_date(hedge_date))
        cal_vols_h, put_vols_h, maturity_dates_h, spot_on_hedge_date, pcprs_on_hedge_date = dataset_on_hedge_date
        expiration_dates_h = to_ql_dates(maturity_dates_h)
        orgnized_data_hedge_date = svi_util.orgnize_data_for_hedging(
            hedge_date, daycounter, put_vols_h, expiration_dates_h, spot_on_hedge_date)

        curve_on_hedge_date = svi_data.get_curve_treasury_bond(hedge_date,daycounter)

        #estimate_vol, min_sse = estimiate_bs_constant_vol_single_optiontype(calibrate_date, calendar, daycounter,ql.Option.Put)
        #estimate_vol, min_sse = estimiate_bs_constant_vol(calibrate_date, calendar, daycounter)
        estimate_vol = estimated_vols.get(to_dt_date(calibrate_date))
        hedge_error_Ms = {}
        hedge_error_pct_Ms = {}
        for nbr_month in range(4):
            moneyness_l, strikes_l, close_prices_l, expiration_date_l = orgnized_data_liquidition_date.get(nbr_month)
            moneyness_h, strikes_h, close_prices_h, expiration_date_h = orgnized_data_hedge_date.get(nbr_month)
            evalDate = calendar.advance(liquidition_date, ql.Period(5, ql.Days))
            if expiration_date_l <= evalDate: continue
            rf = curve_on_hedge_date.zeroRate(expiration_date_h, daycounter, ql.Continuous).rate()
            hedge_errors = []
            hedge_errors_pct = []
            moneyness = []
            #print('liquidition date : ', liquidition_date, ',', nbr_month)
            for idx_k,k in enumerate(strikes_h):
                if k in close_prices_l.keys():
                    close_l = close_prices_l.get(k)
                else:
                    #print('strike not found in L date')
                    continue
                close_h = close_prices_h.get(k)
                # No arbitrage condition
                ttm = daycounter.yearFraction(hedge_date, expiration_date_h)
                if close_h < k*math.exp(-rf*ttm) - spot_on_hedge_date:
                    continue
                if close_h < 0.0001: continue
                delta = hedge_util.calculate_delta_bs(hedge_date, daycounter, calendar,
                                           estimate_vol, spot_c, rf, k, expiration_date_h, optiontype)

                t = daycounter.yearFraction(hedge_date, liquidition_date)
                cash_h = close_h - delta * spot_on_hedge_date
                pnl = delta * spot + cash_h * math.exp(rf * t) - close_l
                pnl_pct = pnl / close_h
                if abs(pnl_pct) > 10 :
                    # print(liquidition_date, ',', nbr_month, ',', k, 'too large error', pnl_pct)
                    continue
                hedge_error = round(pnl, 4)
                pnl_pct = round(pnl_pct, 4)
                hedge_errors.append(hedge_error)
                hedge_errors_pct.append(pnl_pct)
                moneyness.append(round(spot_on_hedge_date/k,4))
            #print('moneyness : ', moneyness)
            #print('hedge errors pct : ', hedge_errors_pct)
            hedge_error_Ms.update({nbr_month:[moneyness,hedge_errors]})
            hedge_error_pct_Ms.update({nbr_month:[moneyness,hedge_errors_pct]})
        if idx_date != 0:
            #print('liquidition date : ',liquidition_date)
            #print('hedge errors : ',hedge_error_Ms)
            key_date1 = datetime.date(liquidition_date.year(),liquidition_date.month(),liquidition_date.dayOfMonth())
            daily_hedge_errors.update({key_date1: hedge_error_Ms})
            daily_pct_hedge_errors.update({key_date1: hedge_error_pct_Ms})
    except Exception as e:
        print(e)
        continue

stop = timeit.default_timer()


print("=" * 110)
print("BS Model Average Hedging Percent Error, PUT (NO SMOOTHING) : ")
print("=" * 110)
print("%20s %15s %15s %25s" % ("sample dates", "month", "moneyness", "PnL(%)"))
samples = ['2015.9-2016.1', '2016.2-2016.7', '2016.8-2017.1', '2017.2-2017.7']

p1_ed = hedge_util.get_1st_percentile_dates(daily_pct_hedge_errors)
p2_ed = hedge_util.get_2nd_percentile_dates(daily_pct_hedge_errors)
p3_ed = hedge_util.get_3rd_percentile_dates(daily_pct_hedge_errors)
p4_ed = hedge_util.get_4th_percentile_dates(daily_pct_hedge_errors)
container = [p1_ed, p2_ed, p3_ed, p4_ed]
results = {}
index = ["sample dates", "contract month", "moneyness", "PnL(%)"]
count = 0
for idx_c, r_ed in enumerate(container):
    mny_ed = hedge_util.hedging_performance_atm(r_ed, r_ed.keys())
    print("-" * 110)
    for i in range(4):
        results.update(
            {count: [samples[idx_c], i, ' ATM',
                     round(sum(mny_ed.get(i)) / len(mny_ed.get(i)), 4)]})
        print("%20s %15s %15s %25s" % (
            samples[idx_c], i, 'ATM',
            round(sum(mny_ed.get(i)) / len(mny_ed.get(i)), 4)))
        count += 1
    results.update({'total sample' + str(idx_c): ['Total Sample', len(r_ed.keys()), 0, 0]})
    #print('total date : ', len(r_ed.keys()))
print("=" * 110)



df = pd.DataFrame(data=results, index=index)
print(df)
df.to_csv('heging_bs_put_atm.csv')