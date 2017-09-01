# -*- coding: utf-8 -*-

from Utilities.svi_save_wind_data import *
import os
import datetime


# Load Data from json file
def get_spot_price(evalDate):
    # Uderlying market price
    underlyingdata = pd.read_json(os.path.abspath('..') + '\marketdata\spotclose' + '.json')
    spot_ts = underlyingdata.values.tolist()
    dates_ts = underlyingdata.index.tolist()
    dt = datetime.datetime(evalDate.year(), evalDate.month(), evalDate.dayOfMonth(),
                           dates_ts[0].hour, dates_ts[0].minute, dates_ts[0].second, dates_ts[0].microsecond)
    spot = spot_ts[dates_ts.index(dt)][0]
    return spot

def get_underlying_ts():
    underlyingdata = pd.read_pickle(os.path.abspath('..')+'\marketdata\spotclose' +'.pkl')
    dates_ts  = underlyingdata.index.tolist()
    spot_ts   = underlyingdata.values.tolist()
    spot_dic  = {}
    for idx_dt,dt in enumerate(dates_ts):
        date_tmp = pd.to_datetime(dt)
        date_ql = ql.Date(date_tmp.day, date_tmp.month, date_tmp.year)
        spot_dic.update({date_ql:spot_ts[idx_dt][0]})
    return spot_dic

def get_commodity_option_data(evalDate):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())

    try:
        # 50ETF contrats info
        optioncontractbasicinfo = pd.read_json(os.path.abspath('..') + '\marketdata\optioncontractbasicinfo' + '.json')
        optionData = optioncontractbasicinfo.values.tolist()
        optionFlds = optioncontractbasicinfo.index.tolist()
        # 50ETF market price data
        optionmkt = pd.read_json(os.path.abspath('..') + '\marketdata\optionmkt_' + datestr + '.json')
        mktFlds = optionmkt.index.tolist()
        mktData = optionmkt.values.tolist()
        # Uderlying market price
        underlyingdata = pd.read_json(os.path.abspath('..') + '\marketdata\spotclose' + '.json')
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


def get_wind_data(evalDate):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())

    try:
        # 50ETF contrats info
        optioncontractbasicinfo = pd.read_json(os.path.abspath('..') + '\marketdata\optioncontractbasicinfo' + '.json')
        optionData = optioncontractbasicinfo.values.tolist()
        optionFlds = optioncontractbasicinfo.index.tolist()
        # 50ETF market price data
        optionmkt = pd.read_json(os.path.abspath('..') + '\marketdata\optionmkt_' + datestr + '.json')
        mktFlds = optionmkt.index.tolist()
        mktData = optionmkt.values.tolist()
        # Uderlying market price
        underlyingdata = pd.read_json(os.path.abspath('..') + '\marketdata\spotclose' + '.json')
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
        curvedata = pd.read_json(os.path.abspath('..') + '\marketdata\curvedata_tb_' + datestr + '.json')
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


def get_contract_months(evalDate):
    if evalDate.month() == 12:
        m2 = 1
    else:
        m2 = evalDate.month() + 1
    if evalDate.month() in [11,12,1]:
        m3 = 3
        m4 = 6
    elif evalDate.month() in [2,3,4]:
        m3 = 6
        m4 = 9
    elif evalDate.month() in [5,6,7]:
        m3 = 9
        m4 = 12
    else:
        m3 = 12
        m4 = 3
    month_indexs = [evalDate.month(), m2, m3, m4]
    return month_indexs

# w.start()
# vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data_pkl(ql.Date(14,7,2017))
# vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data(ql.Date(14,7,2017))
