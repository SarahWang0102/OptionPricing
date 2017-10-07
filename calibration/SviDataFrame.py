from Utilities.svi_read_data import get_wind_data, get_curve_treasury_bond, get_contract_months, get_commodity_m_data, \
    get_commodity_sr_data
from Utilities.svi_prepare_vol_data import calculate_vol_BS
import QuantLib as ql
import math
import pandas as pd
import datetime
from WindPy import w


class SviDataFrame:


    def __init__(self, evalDate,data_mdates = []):
        self.evalDate = evalDate
        self.dataSet = {}
        if len(data_mdates)>0:
            self.add_data(data_mdates) # {mdate1 : SviOneMaturityData 1, mdate2 : SviOneMaturityData 2...}


    def add_data(self,data_mdates):
        for data in data_mdates:
            self.dataSet.update({data.mdate:data})
        #sorted(self.dataSet)


    def get_nst_maturity_data(self,n):
        mdates = list(self.dataSet.keys())
        mdates.sort()
        mdate = mdates[n]
        return self.dataSet.get(mdate)

class SviOneMaturityData:


    def __init__(self, mdate):
        self.mdate = mdate
        self.strikes = []
        self.moneynesses = []
        self.volatilities = []
        self.closes = []
        self.opens = []


    def add_data(self, k, m, vol, close, open):
        self.strikes.append(k)
        self.moneynesses.append(m)
        self.volatilities.append(vol)
        self.closes.append(close)
        self.opens.append(open)


w.start()
evalDate = ql.Date(24, 3, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()
ql.Settings.instance().evaluationDate = evalDate
curve = get_curve_treasury_bond(evalDate, daycounter)
yield_ts = ql.YieldTermStructureHandle(curve)
dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))

vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = get_wind_data(evalDate)

mdates = []
data_mdates = []
for optionid in optionids:
    optionDataIdx = optionData[optionFlds.index('wind_code')].index(optionid)
    if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
        mktindex = mktData[mktFlds.index('option_code')].index(optionid)
        tmp = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
        mdate = datetime.date(tmp.year, tmp.month, tmp.day)
        maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
        strike = optionData[optionFlds.index('exercise_price')][optionDataIdx]
        close = mktData[mktFlds.index('close')][mktindex]
        open = mktData[mktFlds.index('open')][mktindex]
        ttm = daycounter.yearFraction(evalDate, maturitydt)
        rf = curve.zeroRate(maturitydt, daycounter, ql.Continuous).rate()
        Ft = spot * math.exp(rf * ttm)
        moneyness = math.log(strike / Ft, math.e)
        optiontype = ql.Option.Call
        implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                              close, evalDate, calendar, daycounter, precision=0.05, maxVol=0.5,
                                              step=0.0001)

        data_m = SviOneMaturityData(mdate)

        if mdate not in mdates:
            mdates.append(mdate)
            data_m = SviOneMaturityData(mdate)
            data_m.add_data(strike,moneyness,implied_vol,close,open)
            data_mdates.append(data_m)
        else:
            idx_data = mdates.index(mdate)
            data_mdates[idx_data].add_data(strike,moneyness,implied_vol,close,open)

data_set = SviDataFrame(evalDate,data_mdates)
print(data_mdates)
print(data_set)
t = data_set.get_nst_maturity_data(0)
print(t)
# print(mdates)
#mdates.sort()


# print(mdates)






# Use call options for IV data; use put options for put IV data; both use treasury bond curve
def get_call_put_impliedVols_tbcurve(
        evalDate, daycounter, calendar, maxVol=1.0, step=0.0001, precision=0.05, show=True):
    call_volatilities_0 = {}
    call_volatilities_1 = {}
    call_volatilities_2 = {}
    call_volatilities_3 = {}
    put_volatilites_0 = {}
    put_volatilites_1 = {}
    put_volatilites_2 = {}
    put_volatilites_3 = {}
    e_date0, e_date1, e_date2, e_date3 = 0, 0, 0, 0
    try:
        curve = get_curve_treasury_bond(evalDate, daycounter)
        vols, spot, mktData, mktFlds, optionData, optionFlds, optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        yield_ts = ql.YieldTermStructureHandle(curve)
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
        month_indexs = get_contract_months(evalDate)
        for idx, optionid in enumerate(optionids):
            optionDataIdx = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex = mktData[mktFlds.index('option_code')].index(optionid)
            strike = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close = mktData[mktFlds.index('close')][mktindex]
            ttm = daycounter.yearFraction(evalDate, maturitydt)
            rf = curve.zeroRate(maturitydt, daycounter, ql.Continuous).rate()
            nbr_month = maturitydt.month()

            if nbr_month == month_indexs[0]:
                e_date0 = maturitydt
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,
                                                          step)
                    call_volatilities_0.update({moneyness: [implied_vol, strike, close]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_0.update({moneyness: [implied_vol, strike, close]})
            elif nbr_month == month_indexs[1]:
                e_date1 = maturitydt
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,
                                                          step)
                    call_volatilities_1.update({moneyness: [implied_vol, strike, close]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_1.update({moneyness: [implied_vol, strike, close]})
            elif nbr_month == month_indexs[2]:
                e_date2 = maturitydt
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,
                                                          step)
                    call_volatilities_2.update({moneyness: [implied_vol, strike, close]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_2.update({moneyness: [implied_vol, strike, close]})
            else:
                e_date3 = maturitydt
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,
                                                          step)
                    call_volatilities_3.update({moneyness: [implied_vol, strike, close]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_3.update({moneyness: [implied_vol, strike, close]})
        expiration_dates = [e_date0, e_date1, e_date2, e_date3]
        cal_vols = [call_volatilities_0, call_volatilities_1, call_volatilities_2, call_volatilities_3]
        put_vols = [put_volatilites_0, put_volatilites_1, put_volatilites_2, put_volatilites_3]
    except Exception as e:
        print('Error -- get_call_put_impliedVols failed')
        print(e)
        return
    return cal_vols, put_vols, expiration_dates, spot, curve
