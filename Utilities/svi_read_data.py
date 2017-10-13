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

def get_commodity_sr_data(evalDate,calendar):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())

    try:
        # 白糖
        optionmkt = pd.read_json(os.path.abspath('..')+'\marketdata\sr_mkt_' + datestr + '.json')
        mktFlds = optionmkt.index.tolist()
        mktData = optionmkt.values.tolist()
        optionids = mktData[mktFlds.index('品种代码')]
        underlyingIds = []
        for i, id in enumerate(optionids):
            id_sh = id[0:5]
            if id_sh not in underlyingIds:
                underlyingIds.append(id_sh)
        spotmkt = pd.read_json(os.path.abspath('..')+'\marketdata\sr_future_mkt_' + datestr + '.json')
        spotFlds = spotmkt.index.tolist()
        spotData = spotmkt.values.tolist()
        spot_ids = spotData[spotFlds.index('品种月份')]
        spot_ids2 = []
        for s in spot_ids:
            spot_ids2.extend(s.split())
        close_prices = spotData[spotFlds.index('今收盘')]
        underlying_prices = {}
        for spotId in underlyingIds:
            p = close_prices[spot_ids2.index(spotId)]
            p = float(p.replace(',', ''))
            underlying_prices.update({spotId: int(p)})
        contract_months = underlying_prices.keys()
        maturity_dates = []
        for c in contract_months:
            year = '201' + c[2]
            month = c[3:5]
            date = ql.Date(1, int(month), int(year))
            maturity_date = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(-5, ql.Days))
            maturity_dates.append(maturity_date)

        orgnised_data = {}
        for idx in range(len(mktData[0])):
            data = []
            id = mktData[mktFlds.index('品种代码')][idx]
            close = mktData[mktFlds.index('今收盘')][idx]
            volume = mktData[mktFlds.index('成交额(万元)')][idx]
            strike = id[-4:len(id)]
            data.append(int(strike.replace(',', '')))
            data.append(float(close.replace(',', '')))
            data.append(float(volume.replace(',', '')))
            data.append(id[5])  # C or P
            data.append(id[0:5])  # spot id
            orgnised_data.update({id: data})

        results_call = {}
        results_put = {}
        for idx, key in enumerate(orgnised_data):
            data = orgnised_data.get(key)
            year = '201' + key[2]
            month = key[3:5]
            date = ql.Date(1, int(month), int(year))
            mdate = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(-5, ql.Days))
            if data[3] == 'C':
                if mdate not in results_call:
                    results_call.update({mdate: [data]})
                else:
                    results_call.get(mdate).append(data)
            else:
                if mdate not in results_put:
                    results_put.update({mdate: [data]})
                else:
                    results_put.get(mdate).append(data)

    except Exception as e:
        print(e)
        print('Error def -- get_wind_data in \'svi_read_data\' on date : ', evalDate)
        return
    return results_call,results_put,underlying_prices


def get_commodity_m_data(evalDate,calendar):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())

    try:
        # 豆粕
        optionmkt = pd.read_json(os.path.abspath('..')+'\marketdata\m_mkt_' + datestr + '.json')
        mktFlds = optionmkt.index.tolist()
        mktData = optionmkt.values.tolist()

        optionids = mktData[mktFlds.index('合约名称')]
        underlyingIds = []
        for i, id in enumerate(optionids):
            index = id.index('-')
            id_sh = id[1:index]
            if id_sh not in underlyingIds:
                underlyingIds.append(id_sh)
        spotmkt = pd.read_json(os.path.abspath('..')+'\marketdata\m_future_mkt_' + datestr + '.json')
        spotFlds = spotmkt.index.tolist()
        spotData = spotmkt.values.tolist()
        spot_ids = spotData[spotFlds.index('交割月份')]
        close_prices = spotData[spotFlds.index('收盘价')]
        underlying_prices = {}
        for spotId in underlyingIds:
            p = close_prices[spot_ids.index(spotId)]
            p = float(p.replace(',', ''))
            underlying_prices.update({spotId: int(p)})
        contract_months = underlying_prices.keys()
        maturity_dates = []
        for c in contract_months:
            year = '20' + c[0: 2]
            month = c[2:4]
            date = ql.Date(1, int(month), int(year))
            maturity_date = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(4, ql.Days))
            maturity_dates.append(maturity_date)

        orgnised_data = {}
        for idx in range(len(mktData[0])):
            data = []
            id = mktData[mktFlds.index('合约名称')][idx]
            close = mktData[mktFlds.index('收盘价')][idx]
            volume = mktData[mktFlds.index('成交额')][idx]
            strike = id[-4:len(id)]
            index = id.index('-')
            spotid = id[1:index]
            data.append(int(strike))
            data.append(float(close))
            data.append(float(volume))
            data.append(id[id.index('-') + 1]) # C or P
            data.append(spotid) # spot id
            orgnised_data.update({id: data})

        results_call = {}
        results_put = {}
        for idx, key in enumerate(orgnised_data):
            data = orgnised_data.get(key)
            c = key[1:key.index('-')]
            year = '20' + c[0: 2]
            month = c[2:4]
            date = ql.Date(1, int(month), int(year))
            mdate = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(4, ql.Days))
            if data[3] == 'C':
                if mdate not in results_call:
                    results_call.update({mdate: [data]})
                else:
                    results_call.get(mdate).append(data)
            else:
                if mdate not in results_put:
                    results_put.update({mdate: [data]})
                else:
                    results_put.get(mdate).append(data)

    except Exception as e:
        print(e)
        print('Error def -- get_wind_data in \'svi_read_data\' on date : ', evalDate)
        return
    return results_call,results_put,underlying_prices


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
        dates = [evalDate,
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
    month = evalDate.month()
    if evalDate == ql.China().endOfMonth(evalDate):
        month += 1
    if month == 12:
        m2 = 1
    else:
        m2 = month + 1
    if month in [11,12,1]:
        m3 = 3
        m4 = 6
    elif month in [2,3,4]:
        m3 = 6
        m4 = 9
    elif month in [5,6,7]:
        m3 = 9
        m4 = 12
    else:
        m3 = 12
        m4 = 3
    month_indexs = [month, m2, m3, m4]
    return month_indexs

# w.start()
# vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data_pkl(ql.Date(14,7,2017))
# vols,spot,mktData,mktFlds,optionData,optionFlds,optionids = get_wind_data(ql.Date(14,7,2017))
