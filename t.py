import pandas as pd
import os
import QuantLib as ql
import pickle
import datetime
from Utilities import svi_prepare_vol_data as vol_data
import Utilities.svi_read_data as wind_data
import matplotlib.pyplot as plt
from Utilities.utilities import *
import Utilities.svi_prepare_vol_data as svi_data
import Utilities.svi_calibration_utility as svi_util
import math
import numpy as np
from WindPy import w
import datetime
import timeit
import os
import pickle

calendar = ql.China()

sr = pd.read_json('marketdata\sr_mkt_2017-7-14.json')
m = pd.read_json('marketdata\m_mkt_2017-7-14.json')
print(sr)
print(m)