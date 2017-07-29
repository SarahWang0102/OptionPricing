import QuantLib as ql
import math
import numpy as np
from svi_save_wind_data import *
import os
import datetime


# Load Data from json file
def get_wind_data(evalDate):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())

    try:
        # 50ETF contrats info
        optioncontractbasicinfo = pd.read_json(os.getcwd() + '\marketdata\optioncontractbasicinfo' + '.json')
        optionData = optioncontractbasicinfo.values.tolist()
        optionFlds = optioncontractbasicinfo.index.tolist()
        # 50ETF market price data
        optionmkt = pd.read_json(os.getcwd() + '\marketdata\optionmkt_' + datestr + '.json')
        mktFlds = optionmkt.index.tolist()
        mktData = optionmkt.values.tolist()
        # Uderlying market price
        underlyingdata = pd.read_json(os.getcwd() + '\marketdata\spotclose' + '.json')
        spot_ts = underlyingdata.values.tolist()
        dates_ts = underlyingdata.index.tolist()
        dt = datetime.datetime(evalDate.year(), evalDate.month(), evalDate.dayOfMonth(),
                               dates_ts[0].hour, dates_ts[0].minute, dates_ts[0].second, dates_ts[0].microsecond)
        spot = spot_ts[dates_ts.index(dt)][0]
        optionids = mktData[mktFlds.index('option_code')]
        optionids_SH = []
        for i, id in enumerate(optionids):
            id_sh = id + '.SH'
            optionids_SH.append(id_sh)
        vols = []
    except Exception as e:
        print(e)
        print('Error def -- get_wind_data in \'svi_read_data\' on date : ', evalDate)
        return
    return vols, spot, mktData, mktFlds, optionData, optionFlds, optionids


def get_curve_treasury_bond(evalDate, daycounter):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    try:
        curvedata = pd.read_json(os.getcwd() + '\marketdata\curvedata_tb_' + datestr + '.json')
        rates = curvedata.values[0]
        calendar = ql.China()
        dates = [calendar.advance(evalDate, ql.Period(1, ql.Days)),
                 calendar.advance(evalDate, ql.Period(1, ql.Months)),
                 calendar.advance(evalDate, ql.Period(3, ql.Months)),
                 calendar.advance(evalDate, ql.Period(6, ql.Months)),
                 calendar.advance(evalDate, ql.Period(9, ql.Months)),
                 calendar.advance(evalDate, ql.Period(1, ql.Years))]
        krates = np.divide(rates, 100)
        curve = ql.ForwardCurve(dates, krates, daycounter)
    except Exception as e:
        print(e)
        print('Error def -- get_curve_treasury_bond in \'svi_read_data\' on date : ', evalDate)
        return
    return curve

# w.start()
# vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data_pkl(ql.Date(14,7,2017))
# vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data(ql.Date(14,7,2017))
