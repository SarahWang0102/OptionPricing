import pandas as pd
import QuantLib as ql
import math
import pickle
import os
from Utilities.utilities import *
from pricing_options.Options import OptionBarrierEuropean,OptionPlainEuropean
from pricing_options.Evaluation import Evaluation
from pricing_options.SviPricingModel import SviPricingModel
from pricing_options.SviVolSurface import SviVolSurface
import exotic_options.exotic_option_utilities as exotic_util

def get_vol_data(evalDate,daycounter,calendar,contractType):
    svidata = svi_dataset.get(to_dt_date(evalDate))
    paramset = calibrered_params_ts.get(to_dt_date(evalDate))
    volSurface = SviVolSurface(evalDate, paramset, daycounter, calendar)
    spot = svidata.spot
    maturity_dates = sorted(svidata.dataSet.keys())
    svi = SviPricingModel(volSurface, spot, daycounter, calendar,
                            to_ql_dates(maturity_dates), ql.Option.Call, contractType)
    black_var_surface = svi.black_var_surface()
    const_vol = estimated_vols.get(to_dt_date(evalDate))
    return spot, black_var_surface, const_vol


with open(os.path.abspath('..')+'/intermediate_data/svi_calibration_50etf_calls_noZeroVol.pickle','rb') as f:
    calibrered_params_ts = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/svi_dataset_50etf_calls_noZeroVol.pickle','rb') as f:
    svi_dataset = pickle.load(f)[0]
with open(os.path.abspath('..') +'/intermediate_data/total_hedging_bs_estimated_vols.pickle','rb') as f:
    estimated_vols = pickle.load(f)[0]



# Evaluation Settings
begDate = ql.Date(1,8,2017)
endDate1 = ql.Date(29,9,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
fee = 0.2/1000
dt = 1.0/365
rf = 0.03

################Barrier Option Info#####################





#########################################################
evalDate = begDate
datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
intraday_etf = pd.read_json(os.path.abspath('..') + '\marketdata\intraday_etf_'+datestr + '.json')
timestamps = list(intraday_etf.index)

















