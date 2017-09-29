# -*- coding: utf-8 -*-
from Utilities.svi_read_data import get_wind_data,get_curve_treasury_bond,get_contract_months,get_commodity_m_data,get_commodity_sr_data
import QuantLib as ql
import math
import pandas as pd
from WindPy import w

# prepare volatility data for commodities
def get_call_put_impliedVols_m(evalDate,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.05,show=True):
    results_call, results_put, underlying_prices = get_commodity_m_data(evalDate, calendar)
    call_vols, put_vols, expiration_dates_c, expiration_dates_p, curve = get_call_put_impliedVols_cmd(
        evalDate,daycounter,calendar,results_call, results_put, underlying_prices)
    return call_vols,put_vols,expiration_dates_c,expiration_dates_p,underlying_prices,curve

def get_call_put_impliedVols_sr(evalDate,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.05,show=True):
    results_call, results_put, underlying_prices = get_commodity_sr_data(evalDate, calendar)
    call_vols, put_vols, expiration_dates_c, expiration_dates_p, curve = get_call_put_impliedVols_cmd(
        evalDate,daycounter,calendar,results_call, results_put, underlying_prices)
    return call_vols,put_vols,expiration_dates_c,expiration_dates_p,underlying_prices,curve

def get_call_put_impliedVols_cmd(evalDate,daycounter,calendar,results_call, results_put, underlying_prices,maxVol=1.0,step=0.0001,precision=0.05,show=True):
    try:
        curve = get_curve_treasury_bond(evalDate, daycounter)
        ql.Settings.instance().evaluationDate = evalDate

        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
        call_vols = []
        put_vols = []
        expiration_dates_c = []
        for idx_m,mdate in enumerate(results_call):
            expiration_dates_c.append(mdate)
            call_volatilities = {}
            optiontype = ql.Option.Call
            dataset = results_call.get(mdate)
            #print(dataset)
            maxdate = curve.maxDate()
            if mdate > maxdate:
                rf = curve.zeroRate(maxdate, daycounter, ql.Continuous).rate()
            else:
                rf = curve.zeroRate(mdate, daycounter, ql.Continuous).rate()
            yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
            #print(rf)
            ttm = daycounter.yearFraction(evalDate, mdate)
            for data in dataset:
                spotid = data[-1]
                strike = data[0]
                close = data[1]
                if close < 0.0001 : continue
                spot = underlying_prices.get(spotid)
                if spot < 0.0001: continue
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                implied_vol, error = calculate_vol_BS(mdate, optiontype, strike, spot, dividend_ts, yield_ts,
                                                      close, evalDate, calendar, daycounter, precision, maxVol, step)
                call_volatilities.update({moneyness:[implied_vol,strike,close,spotid]})
            call_vols.append(call_volatilities)
        expiration_dates_p = []
        for idx_m, mdate in enumerate(results_put):
            expiration_dates_p.append(mdate)
            put_volatilities = {}
            optiontype = ql.Option.Put
            dataset = results_put.get(mdate)
            ttm = daycounter.yearFraction(evalDate, mdate)
            maxdate = curve.maxDate()
            if mdate > maxdate:
                rf = curve.zeroRate(maxdate, daycounter, ql.Continuous).rate()
            else:
                rf = curve.zeroRate(mdate, daycounter, ql.Continuous).rate()
            yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
            for data in dataset:
                spotid = data[-1]
                strike = data[0]
                close = data[1]
                if close < 0.0001 : continue
                spot = underlying_prices.get(spotid)
                if spot < 0.0001: continue
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                implied_vol, error = calculate_vol_BS(mdate, optiontype, strike, spot, dividend_ts, yield_ts,
                                                      close, evalDate, calendar, daycounter, precision, maxVol, step)
                put_volatilities.update({moneyness:[implied_vol,strike,close,spotid]})
            put_vols.append(put_volatilities)
    except Exception as e:
        print(e)
        return
    return call_vols,put_vols,expiration_dates_c,expiration_dates_p,curve

# Use call options for IV data; use put options for put IV data; both use treasury bond curve
def get_call_put_impliedVols_tbcurve(
        evalDate,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.05,show=True):

    call_volatilities_0 = {}
    call_volatilities_1 = {}
    call_volatilities_2 = {}
    call_volatilities_3 = {}
    put_volatilites_0 = {}
    put_volatilites_1 = {}
    put_volatilites_2 = {}
    put_volatilites_3 = {}
    e_date0, e_date1, e_date2, e_date3 = 0,0,0,0
    try:
        curve = get_curve_treasury_bond(evalDate, daycounter)
        vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        yield_ts = ql.YieldTermStructureHandle(curve)
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
        month_indexs = get_contract_months(evalDate)
        for idx, optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt      = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex        = mktData[mktFlds.index('option_code')].index(optionid)
            strike          = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close           = mktData[mktFlds.index('close')][mktindex]
            ttm             = daycounter.yearFraction(evalDate, maturitydt)
            rf              = curve.zeroRate(maturitydt, daycounter, ql.Continuous).rate()
            nbr_month       = maturitydt.month()

            if nbr_month == month_indexs[0]:
                e_date0     = maturitydt
                Ft = spot * math.exp(rf * ttm)
                moneyness   = math.log(strike / Ft, math.e)
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_0.update({moneyness:[implied_vol,strike,close]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_0.update({moneyness: [implied_vol,strike,close]})
            elif nbr_month == month_indexs[1]:
                e_date1 = maturitydt
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_1.update({moneyness:[implied_vol,strike,close]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_1.update({moneyness: [implied_vol,strike,close]})
            elif nbr_month == month_indexs[2]:
                e_date2 = maturitydt
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_2.update({moneyness:[implied_vol,strike,close]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_2.update({moneyness: [implied_vol,strike,close]})
            else:
                e_date3 = maturitydt
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_3.update({moneyness:[implied_vol,strike,close]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_3.update({moneyness: [implied_vol,strike,close]})
        expiration_dates = [e_date0,e_date1,e_date2,e_date3]
        cal_vols = [call_volatilities_0,call_volatilities_1,call_volatilities_2,call_volatilities_3]
        put_vols = [put_volatilites_0,put_volatilites_1,put_volatilites_2,put_volatilites_3]
    except Exception as e:
        print('Error -- get_call_put_impliedVols failed')
        print(e)
        return
    return cal_vols,put_vols,expiration_dates,spot,curve

# Currently used for combine OTM calls and OTM puts for IV data
def get_call_put_impliedVols_moneyness_PCPrate_pcvt(
        evalDate,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.05,show=True):
    close_call = []
    close_put = []
    call_volatilities_0 = {}
    call_volatilities_1 = {}
    call_volatilities_2 = {}
    call_volatilities_3 = {}
    put_volatilites_0 = {}
    put_volatilites_1 = {}
    put_volatilites_2 = {}
    put_volatilites_3 = {}
    e_date0, e_date1, e_date2, e_date3 = 0,0,0,0
    try:
        # Get PC parity implied risk free rates
        rf_Ks_months = calculate_PCParity_ATM_implied_rfs(evalDate, daycounter, calendar)
        #rf_Ks_months = calculate_PCParity_riskFreeRate(evalDate, daycounter, calendar)
        #print(rf_Ks_months)
        # Get Wind Market Data
        vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
        month_indexs = get_contract_months(evalDate)
        for idx, optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt      = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex        = mktData[mktFlds.index('option_code')].index(optionid)
            strike          = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close           = mktData[mktFlds.index('close')][mktindex]
            ttm             = daycounter.yearFraction(evalDate, maturitydt)
            nbr_month       = maturitydt.month()
            optiontype = ql.Option.Call
            if nbr_month == month_indexs[0]:
                e_date0     = maturitydt
                #rf = rf_Ks_months.get(0).get(strike)
                rf = rf_Ks_months.get(0)
                Ft = spot * math.exp(rf * ttm)
                moneyness   = math.log(strike / Ft, math.e)
                yield_ts    = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,rf,daycounter))

                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_0.update({moneyness:[implied_vol,strike,close]})
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_0.update({moneyness: [implied_vol,strike,close]})
            elif nbr_month == month_indexs[1]:
                e_date1 = maturitydt
                #rf = rf_Ks_months.get(1).get(strike)
                rf = rf_Ks_months.get(1)
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_1.update({moneyness:[implied_vol,strike,close]})
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_1.update({moneyness: [implied_vol,strike,close]})
            elif nbr_month == month_indexs[2]:
                e_date2 = maturitydt
                #rf = rf_Ks_months.get(2).get(strike)
                rf = rf_Ks_months.get(2)
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_2.update({moneyness:[implied_vol,strike,close]})
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_2.update({moneyness: [implied_vol,strike,close]})
            else:
                e_date3 = maturitydt
                #rf = rf_Ks_months.get(3).get(strike)
                rf = rf_Ks_months.get(3)
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_3.update({moneyness:[implied_vol,strike,close]})
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_3.update({moneyness: [implied_vol,strike,close]})
        expiration_dates = [e_date0,e_date1,e_date2,e_date3]
        cal_vols = [call_volatilities_0,call_volatilities_1,call_volatilities_2,call_volatilities_3]
        put_vols = [put_volatilites_0,put_volatilites_1,put_volatilites_2,put_volatilites_3]
    except:
        print('Error -- get_call_put_impliedVols failed')
        return
    return cal_vols,put_vols,expiration_dates,spot,rf_Ks_months

# Use treasury bond curve and put option conversion for IV data
def get_impliedvolmat_BS_put_cnvt(
        evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False):
    try:
        # Get Wind Market Data
        vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        yield_ts = ql.YieldTermStructureHandle(curve)
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
        month_indexs = get_contract_months(evalDate)
        call_volatilities_0 = {}
        call_volatilities_1 = {}
        call_volatilities_2 = {}
        call_volatilities_3 = {}
        put_volatilites_0 = {}
        put_volatilites_1 = {}
        put_volatilites_2 = {}
        put_volatilites_3 = {}
        e_date0, e_date1, e_date2, e_date3 = 0, 0, 0, 0
        if show:
            print("="*110)
            print("%10s %10s %10s %10s %25s %25s %20s" % ("Type","Spot", "Strike", "close","moneyness", "impliedVol", "Error (%)"))
            print("-"*110)
        for idx,optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt      = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex        = mktData[mktFlds.index('option_code')].index(optionid)
            strike          = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close           = mktData[mktFlds.index('close')][mktindex]
            ttm             = daycounter.yearFraction(evalDate, maturitydt)
            rf              = curve.zeroRate(maturitydt, daycounter, ql.Continuous).rate()
            Ft              = spot * math.exp(rf * ttm)
            nbr_month       = maturitydt.month()
            moneyness       = math.log(strike / Ft, math.e)
            optiontype      = ql.Option.Call
            if nbr_month == month_indexs[0]:
                e_date0     = maturitydt
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    eqvlt_close = close
                    implied_vol,error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts, eqvlt_close, evalDate,
                                     calendar, daycounter, precision, maxVol, step)
                    call_volatilities_0.update({moneyness: [implied_vol, strike]})
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_0.update({moneyness: [implied_vol, strike]})
            elif nbr_month == month_indexs[1]:
                e_date1 = maturitydt
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    eqvlt_close = close
                    implied_vol,error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts, eqvlt_close, evalDate,
                                     calendar, daycounter, precision, maxVol, step)
                    call_volatilities_1.update({moneyness: [implied_vol, strike]})
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_1.update({moneyness: [implied_vol, strike]})
            elif nbr_month == month_indexs[2]:
                e_date2 = maturitydt
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    eqvlt_close = close
                    implied_vol,error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts, eqvlt_close, evalDate,
                                     calendar, daycounter, precision, maxVol, step)
                    call_volatilities_2.update({moneyness: [implied_vol, strike]})
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_2.update({moneyness: [implied_vol, strike]})
            else:
                e_date3 = maturitydt
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    eqvlt_close = close
                    implied_vol,error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts, eqvlt_close, evalDate,
                                     calendar, daycounter, precision, maxVol, step)
                    call_volatilities_3.update({moneyness: [implied_vol, strike]})
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    put_volatilites_3.update({moneyness: [implied_vol, strike]})
        expiration_dates = [e_date0, e_date1, e_date2, e_date3]
        cal_vols = [call_volatilities_0, call_volatilities_1, call_volatilities_2, call_volatilities_3]
        put_vols = [put_volatilites_0, put_volatilites_1, put_volatilites_2, put_volatilites_3]
        if show : print("-"*110)
        #print('vols:', vol_data)
        #print('close prices: ', close_prices)
    except:
        print('VolatilityData -- get_impliedvolmat_BS_put_cnvt failed')
        return
    return cal_vols,put_vols,expiration_dates,spot,curve


def get_call_put_impliedVols_strikes(
        evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=True):
    close_call = []
    close_put = []
    call_volatilities_0 = {}
    call_volatilities_1 = {}
    call_volatilities_2 = {}
    call_volatilities_3 = {}
    put_volatilites_0 = {}
    put_volatilites_1 = {}
    put_volatilites_2 = {}
    put_volatilites_3 = {}
    try:
        # Get Wind Market Data
        vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        yield_ts = ql.YieldTermStructureHandle(curve)
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
        month_indexs = get_contract_months(evalDate)
        for idx,optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])

            maturitydt  = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
            strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close       = mktData[mktFlds.index('close')][mktindex]
            amount      = mktData[mktFlds.index('amount')][mktindex]
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                optiontype  = ql.Option.Call
                implied_vol,error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                         close, evalDate,calendar, daycounter, precision, maxVol, step)
                if mdate.month == month_indexs[0]:
                    call_volatilities_0.update({strike:[implied_vol,amount]})
                elif mdate.month == month_indexs[1]:
                    call_volatilities_1.update({strike:[implied_vol,amount]})
                elif mdate.month == month_indexs[2]:
                    call_volatilities_2.update({strike:[implied_vol,amount]})
                else:
                    call_volatilities_3.update({strike:[implied_vol,amount]})
                close_call.append(close)
            else:
                optiontype = ql.Option.Put
                implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,calendar, daycounter, precision, maxVol, step)
                if mdate.month   == month_indexs[0]:
                    put_volatilites_0.update({strike:[implied_vol,amount]})
                elif mdate.month == month_indexs[1]:
                    put_volatilites_1.update({strike:[implied_vol,amount]})
                elif mdate.month == month_indexs[2]:
                    put_volatilites_2.update({strike:[implied_vol,amount]})
                else:
                    put_volatilites_3.update({strike:[implied_vol,amount]})
                close_put.append(close)
        cal_vols = [call_volatilities_0,call_volatilities_1,call_volatilities_2,call_volatilities_3]
        put_vols = [put_volatilites_0,put_volatilites_1,put_volatilites_2,put_volatilites_3]
    except:
        print('VolatilityData -- get_call_put_impliedVols failed')
        return
    return cal_vols,put_vols

def get_call_put_impliedVols_moneyness(
        evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=True):
    close_call = []
    close_put = []
    call_volatilities_0 = {}
    call_volatilities_1 = {}
    call_volatilities_2 = {}
    call_volatilities_3 = {}
    put_volatilites_0 = {}
    put_volatilites_1 = {}
    put_volatilites_2 = {}
    put_volatilites_3 = {}
    try:
        # Get Wind Market Data
        vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        yield_ts = ql.YieldTermStructureHandle(curve)
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
        month_indexs = get_contract_months(evalDate)
        for idx,optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])

            maturitydt  = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
            strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close       = mktData[mktFlds.index('close')][mktindex]
            ttm         = daycounter.yearFraction(evalDate, maturitydt)
            rf          = curve.zeroRate(maturitydt, daycounter, ql.Continuous).rate()
            Ft          = spot * math.exp(rf * ttm)
            moneyness   = math.log(strike / Ft, math.e)
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                optiontype  = ql.Option.Call
                implied_vol,error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                         close, evalDate,calendar, daycounter, precision, maxVol, step)
                if mdate.month == month_indexs[0]:
                    call_volatilities_0.update({moneyness:implied_vol})
                elif mdate.month == month_indexs[1]:
                    call_volatilities_1.update({moneyness:implied_vol})
                elif mdate.month == month_indexs[2]:
                    call_volatilities_2.update({moneyness:implied_vol})
                else:
                    call_volatilities_3.update({moneyness:implied_vol})
                close_call.append(close)
            else:
                optiontype = ql.Option.Put
                implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate,calendar, daycounter, precision, maxVol, step)
                if mdate.month   == month_indexs[0]:
                    put_volatilites_0.update({moneyness:implied_vol})
                elif mdate.month == month_indexs[1]:
                    put_volatilites_1.update({moneyness:implied_vol})
                elif mdate.month == month_indexs[2]:
                    put_volatilites_2.update({moneyness:implied_vol})
                else:
                    put_volatilites_3.update({moneyness:implied_vol})
                close_put.append(close)
        cal_vols = [call_volatilities_0,call_volatilities_1,call_volatilities_2,call_volatilities_3]
        put_vols = [put_volatilites_0,put_volatilites_1,put_volatilites_2,put_volatilites_3]
    except:
        print('Error -- get_call_put_impliedVols failed')
        return
    return cal_vols,put_vols

def get_call_put_impliedVols_moneyness_PCPrate(
        evalDate,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.05,show=True):
    close_call = []
    close_put = []
    call_volatilities_0 = {}
    call_volatilities_1 = {}
    call_volatilities_2 = {}
    call_volatilities_3 = {}
    put_volatilites_0 = {}
    put_volatilites_1 = {}
    put_volatilites_2 = {}
    put_volatilites_3 = {}
    e_date0, e_date1, e_date2, e_date3 = 0,0,0,0
    try:
        # Get PC parity implied risk free rates
        rf_Ks_months = calculate_PCParity_ATM_implied_rfs(evalDate, daycounter, calendar)
        #rf_Ks_months = calculate_PCParity_riskFreeRate(evalDate, daycounter, calendar)
        print(rf_Ks_months)
        # Get Wind Market Data
        vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
        month_indexs = get_contract_months(evalDate)
        for idx, optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt      = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex        = mktData[mktFlds.index('option_code')].index(optionid)
            strike          = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close           = mktData[mktFlds.index('close')][mktindex]
            ttm             = daycounter.yearFraction(evalDate, maturitydt)
            nbr_month       = maturitydt.month()
            if nbr_month == month_indexs[0]:
                e_date0     = maturitydt
                #rf = rf_Ks_months.get(0).get(strike)
                rf = rf_Ks_months.get(0)
                Ft = spot * math.exp(rf * ttm)
                moneyness   = math.log(strike / Ft, math.e)
                yield_ts    = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,rf,daycounter))
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_0.update({moneyness:[implied_vol,strike]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    put_volatilites_0.update({moneyness: [implied_vol,strike]})
            elif nbr_month == month_indexs[1]:
                e_date1 = maturitydt
                #rf = rf_Ks_months.get(1).get(strike)
                rf = rf_Ks_months.get(1)
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_1.update({moneyness:[implied_vol,strike]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    put_volatilites_1.update({moneyness: [implied_vol,strike]})
            elif nbr_month == month_indexs[2]:
                e_date2 = maturitydt
                #rf = rf_Ks_months.get(2).get(strike)
                rf = rf_Ks_months.get(2)
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_2.update({moneyness:[implied_vol,strike]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    put_volatilites_2.update({moneyness: [implied_vol,strike]})
            else:
                e_date3 = maturitydt
                #rf = rf_Ks_months.get(3).get(strike)
                rf = rf_Ks_months.get(3)
                Ft = spot * math.exp(rf * ttm)
                moneyness = math.log(strike / Ft, math.e)
                yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    optiontype = ql.Option.Call
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts,yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    call_volatilities_3.update({moneyness:[implied_vol,strike]})
                else:
                    optiontype = ql.Option.Put
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          close, evalDate, calendar, daycounter, precision, maxVol,step)
                    put_volatilites_3.update({moneyness: [implied_vol,strike]})
        expiration_dates = [e_date0,e_date1,e_date2,e_date3]
        cal_vols = [call_volatilities_0,call_volatilities_1,call_volatilities_2,call_volatilities_3]
        put_vols = [put_volatilites_0,put_volatilites_1,put_volatilites_2,put_volatilites_3]
    except:
        print('Error -- get_call_put_impliedVols failed')
        return
    return cal_vols,put_vols,expiration_dates,spot,rf_Ks_months

## Utilities
# Utility function for calculating BS implied vols
def calculate_vol_BS(
        maturitydt,optiontype,strike,spot,dividend_ts,yield_ts,
        eqvlt_close,evalDate,calendar,daycounter,precision=0.001,maxVol=1.0,step=0.0001):
    exercise = ql.EuropeanExercise(maturitydt)
    payoff = ql.PlainVanillaPayoff(optiontype, strike)
    option = ql.EuropeanOption(payoff, exercise)
    flat_vol_ts = ql.BlackVolTermStructureHandle(
                ql.BlackConstantVol(evalDate, calendar, 0.0, daycounter))
    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts, yield_ts,
                                           flat_vol_ts)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
    error = 0.0
    try:
        implied_vol = option.impliedVolatility(eqvlt_close, process, 1.0e-4, 300, 0.0, 4.0)
    except RuntimeError:
        implied_vol = 0.0
    if implied_vol == 0.0:
        error = 'NaN'
        sigma = maxVol
        implied_vol = 0.0
        # candidate_prices = []
        while sigma >= step:
            flat_vol_ts_it = ql.BlackVolTermStructureHandle(
                ql.BlackConstantVol(evalDate, calendar, sigma, daycounter))
            process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts,
                                                   yield_ts, flat_vol_ts_it)
            option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
            price = option.NPV()
            # candidate_prices.append(price)
            if abs(price - eqvlt_close) < precision:
                # print('error : ', price - close)
                error = price - eqvlt_close
                break
            sigma -= step
        implied_vol = sigma
    return implied_vol,error

def calculate_PCParity_ATM_implied_rfs(evalDate,daycounter,calendar):
    vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
    rf_atm_months = {}
    call_month0 = {}
    call_month1 = {}
    call_month2 = {}
    call_month3 = {}
    put_month0 = {}
    put_month1 = {}
    put_month2 = {}
    put_month3 = {}
    ttm = 0.0
    month_indexs = get_contract_months(evalDate)
    for idx,optionid in enumerate(optionids):
        optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
        mdate = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
        mktindex = mktData[mktFlds.index('option_code')].index(optionid)
        close = mktData[mktFlds.index('close')][mktindex]
        strike = optionData[optionFlds.index('exercise_price')][optionDataIdx]
        maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
        ttm = daycounter.yearFraction(evalDate, maturitydt)
        if mdate.month == month_indexs[0]:
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call_month0.update({strike:close})
            else:
                put_month0.update({strike:close})
        elif mdate.month == month_indexs[1]:
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call_month1.update({strike:close})
            else:
                put_month1.update({strike:close})
        elif mdate.month == month_indexs[2]:
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call_month2.update({strike:close})
            else:
                put_month2.update({strike:close})
        else:
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call_month3.update({strike:close})
            else:
                put_month3.update({strike:close})
    call_months = [call_month0,call_month1,call_month2,call_month3]
    put_months = [put_month0, put_month1, put_month2, put_month3]
    for idx_month,call in enumerate(call_months):
        put = put_months[idx_month]
        min_diff = 10
        r_f = 0.0002
        for idx_k, strike in enumerate(call.keys()):
            diff = strike - spot
            if diff < min_diff and diff >= 0:
                min_diff = diff
                r_f = max(0.0002,(1/ttm)*math.log((spot+put.get(strike)-call.get(strike))/strike,math.e))
        rf_atm_months.update({idx_month:r_f})
    return rf_atm_months

def calculate_PCParity_implied_rfs(evalDate,daycounter,calendar):
    vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
    rf_Ks_months = {}
    call_month0 = {}
    call_month1 = {}
    call_month2 = {}
    call_month3 = {}
    put_month0 = {}
    put_month1 = {}
    put_month2 = {}
    put_month3 = {}
    ttm = 0.0
    month_indexs = get_contract_months(evalDate)
    for idx,optionid in enumerate(optionids):
        optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
        mdate = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
        mktindex = mktData[mktFlds.index('option_code')].index(optionid)
        close = mktData[mktFlds.index('close')][mktindex]
        strike = optionData[optionFlds.index('exercise_price')][optionDataIdx]
        maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
        ttm = daycounter.yearFraction(evalDate, maturitydt)
        if mdate.month == month_indexs[0]:
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call_month0.update({strike:close})
            else:
                put_month0.update({strike:close})
        elif mdate.month == month_indexs[1]:
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call_month1.update({strike:close})
            else:
                put_month1.update({strike:close})
        elif mdate.month == month_indexs[2]:
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call_month2.update({strike:close})
            else:
                put_month2.update({strike:close})
        else:
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call_month3.update({strike:close})
            else:
                put_month3.update({strike:close})
    call_months = [call_month0,call_month1,call_month2,call_month3]
    put_months = [put_month0, put_month1, put_month2, put_month3]
    for idx_month,call in enumerate(call_months):
        r_f = {}
        count = len(call.keys())
        put = put_months[idx_month]
        for idx_k, strike in enumerate(call.keys()):
            r = max(0.0002,(1/ttm)*math.log((spot+put.get(strike)-call.get(strike))/strike,math.e))
            r_f.update({strike:r})
        rf_Ks_months.update({idx_month:r_f})
    return rf_Ks_months

## IV Surface
# Used for black volatiluty curve
def get_impliedvolmat_call_givenKs(evalDate,daycounter,calendar,curve):
    # Get Wind Market Data
    vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
    ql.Settings.instance().evaluationDate = evalDate
    yield_ts = ql.YieldTermStructureHandle(curve)
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
    vol1 = []
    vol2 = []
    vol3 = []
    vol4 = []
    close1 = []
    close2 = []
    close3 = []
    close4 = []
    #strikes = [2.4, 2.45, 2.5, 2.55, 2.6, 2.65, 2.7, 2.75]
    strikes = [2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6, 2.65]
    tempcontainer = [2.299, 2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6]
    months = get_contract_months(evalDate)
    for idx,optionid in enumerate(optionids):
        optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
        if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认沽':
            optiontype  = ql.Option.Put
            strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            mdate       = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt  = ql.Date(mdate.day,mdate.month,mdate.year)
            mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
            close       = mktData[mktFlds.index('close')][mktindex]
            voldata     = w.wss(optionid + '.SH', "us_impliedvol", "tradeDate=20170703")
            implied_vol = voldata.Data[0][0]
            #implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,                                     close, evalDate, calendar, daycounter)
            #implied_vol = vols[idx]
            if strike in strikes:
                if mdate.month == months[0]:
                    vol1.append(implied_vol)
                    close1.append(close)
                    dt1 = maturitydt
                elif mdate.month == months[1]:
                    vol2.append(implied_vol)
                    close2.append(close)
                    dt2 = maturitydt
                elif mdate.month == months[2]:
                    vol3.append(implied_vol)
                    close3.append(close)
                    dt3 = maturitydt
                elif mdate.month == months[3]:
                    vol4.append(implied_vol)
                    close4.append(close)
                    dt4 = maturitydt
    # Matrix data to construct BlackVarianceSurface
    data = [vol1,vol2,vol3,vol4]
    expiration_dates = [dt1,dt2,dt3,dt4]
    #expiration_dates = [dt2, dt3, dt4]
    #data = [vol2, vol3, vol4]
    matrix = ql.Matrix(len(strikes), len(expiration_dates))
    close_prices = [close1,close2,close3,close4]
    #print('vols:', data)
    #print('close prices: ', close_prices)
    return data,matrix,expiration_dates,strikes,spot

def get_impliedvolmat_call_BS_givenKs(evalDate,daycounter,calendar):
    # Get Wind Market Data
    vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
    # Evaluation Settings
    ql.Settings.instance().evaluationDate = evalDate
    curve       = get_curve_treasury_bond(evalDate, daycounter)
    yield_ts    = ql.YieldTermStructureHandle(curve)
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, 0.0, daycounter))
    # Prepare strikes,maturity dates for BlackVarianceSurface
    optionids   = mktData[mktFlds.index('option_code')]
    vol1 = []
    vol2 = []
    vol3 = []
    vol4 = []
    close1 = []
    close2 = []
    close3 = []
    close4 = []
    month_indexs = get_contract_months(evalDate)
    strikes = [2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6]
    #strikes = [2.45, 2.5, 2.55, 2.6]
    tempcontainer = [2.299, 2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6]
    for idx,optionid in enumerate(optionids):
        optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
        if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认沽':
            optiontype  = ql.Option.Call
            strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            mdate       = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            maturitydt  = ql.Date(mdate.day,mdate.month,mdate.year)
            mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
            close       = mktData[mktFlds.index('close')][mktindex]
            exercise    = ql.EuropeanExercise(maturitydt)
            payoff      = ql.PlainVanillaPayoff(optiontype,strike)
            option      = ql.EuropeanOption(payoff,exercise)
            process     = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)),dividend_ts,yield_ts,flat_vol_ts)
            option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
            try:
                implied_vol = option.impliedVolatility(close,process,1.0e-1,300,0.0,4.0)
            except RuntimeError:
                implied_vol = 0.00
            if strike in strikes:
                if mdate.month == month_indexs[0]:
                    vol1.append(implied_vol)
                    close1.append(close)
                    dt1 = maturitydt
                elif mdate.month == month_indexs[1]:
                    vol2.append(implied_vol)
                    close2.append(close)
                    dt2 = maturitydt
                elif mdate.month == month_indexs[2]:
                    vol3.append(implied_vol)
                    close3.append(close)
                    dt3 = maturitydt
                elif mdate.month == month_indexs[3]:
                    vol4.append(implied_vol)
                    close4.append(close)
                    dt4 = maturitydt
    # Matrix data to construct BlackVarianceSurface
    data = [vol1,vol2,vol3,vol4]
    expiration_dates = [dt1,dt2,dt3,dt4]
    matrix = ql.Matrix(len(strikes), len(expiration_dates))
    close_prices = [close1,close2,close3,close4]
    #print('vols:', data)
    #print('close prices: ', close_prices)
    return data,matrix,expiration_dates,strikes,spot

## One Maturity
# Use only put option impied vols for SVI calibrated IV curve (one maturity)
def get_impliedvolmat_BS_put_cnvt_oneMaturity(
        evalDate,curve,daycounter,calendar,month,maxVol=1.0,step=0.0001,precision=0.001,show=True):
    try:
        # Get Wind Market Data
        vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        yield_ts = ql.YieldTermStructureHandle(curve)
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
        vol_data = []
        close_call = []
        close_put = []
        logMoneyness_call = []
        logMoneyness_put = []
        strikes_call = []
        strikes_put = []
        call_volatilities = []
        put_converted_volatilites = []
        call_pair = []
        put_pair =[]
        maturitydt = 0.0
        if show:
            print("="*110)
            print("%10s %10s %10s %10s %25s %25s %20s" % ("Type","Spot", "Strike", "close","moneyness", "impliedVol", "Error (%)"))
            print("-"*110)
        for idx,optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            if mdate.month == month:
                maturitydt  = ql.Date(mdate.day, mdate.month, mdate.year)
                mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
                strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
                close       = mktData[mktFlds.index('close')][mktindex]
                ttm         = daycounter.yearFraction(evalDate, maturitydt)
                rf          = curve.zeroRate(maturitydt,daycounter,ql.Continuous).rate()
                Ft          = spot* math.exp(rf*ttm)
                optiontype  = ql.Option.Call
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    eqvlt_close = close
                    implied_vol,error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts, eqvlt_close, evalDate,
                                     calendar, daycounter, precision, maxVol, step)
                    logMoneyness = math.log(strike / Ft, math.e)
                    logMoneyness_call.append(logMoneyness)
                    strikes_call.append(strike)
                    call_volatilities.append(implied_vol)
                    close_call.append(close)
                    if show: print(
                        "%10s %10s %10s %10s %25s %25s %20s" % ('Call',spot, strike, close, logMoneyness, implied_vol, error))
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    logMoneyness = math.log(strike / Ft, math.e)
                    logMoneyness_put.append(logMoneyness)
                    strikes_put.append(strike)
                    put_converted_volatilites.append(implied_vol)
                    close_put.append(close)
                    if show: print(
                        "%10s %10s %10s %10s %25s %25s %20s" % ('Put', spot, strike, close, logMoneyness, implied_vol, error))
        if show : print("-"*110)
        #print('vols:', vol_data)
        #print('close prices: ', close_prices)
    except:
        print('VolatilityData -- get_impliedvolmat_BS_put_cnvt_oneMaturity failed')
        return
    return call_volatilities,put_converted_volatilites,strikes_call,strikes_put,\
           close_call,close_put,logMoneyness_call,logMoneyness_put,maturitydt,spot

def get_impliedvolmat_BS_oneMaturity(type, evalDate,daycounter,calendar,i,maxVol=1.0,step=0.0001,precision=0.001,show=True):
    # Get Wind Market Data
    vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
    ql.Settings.instance().evaluationDate = evalDate
    curve = get_curve_treasury_bond(evalDate, daycounter)
    yield_ts = ql.YieldTermStructureHandle(curve)
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, 0.0, daycounter))
    vol_data = []
    close_prices = []
    logMoneynesses = []
    #strikes = [2.3, 2.35, 2.4, 2.45, 2.5, 2.55, 2.6]
    #strikes = [2.45, 2.5, 2.55, 2.6]
    strikes = []
    if show:
        print("="*110)
        print("%10s %10s %10s %25s %25s %20s" % ("Spot", "Strike", "close","moneyness", "impliedVol", "Error (%)"))
        print("-"*110)
    for idx,optionid in enumerate(optionids):
        optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
        mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
        if mdate.month == i:
            maturitydt  = ql.Date(mdate.day, mdate.month, mdate.year)
            mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
            strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            close       = mktData[mktFlds.index('close')][mktindex]
            ttm         = daycounter.yearFraction(evalDate, maturitydt)
            rf          = curve.zeroRate(maturitydt,daycounter,ql.Continuous).rate()
            Ft          = spot* math.exp(rf*ttm)
            if type == '认购': optiontype  = ql.Option.Call
            else:optiontype  = ql.Option.Put
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == type:
                exercise    = ql.EuropeanExercise(maturitydt)
                payoff      = ql.PlainVanillaPayoff(optiontype,strike)
                option      = ql.EuropeanOption(payoff,exercise)
                process     = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)),dividend_ts,yield_ts,flat_vol_ts)
                option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
                error       = 0.0
                try:
                    implied_vol = option.impliedVolatility(close,process,1.0e-4,300,0.0,4.0)
                except RuntimeError:
                    implied_vol = 0.0
                if implied_vol == 0.0:
                    error = 'NaN'
                    sigma = maxVol
                    implied_vol = 0.0
                    #candidate_prices = []
                    while sigma >= 0.0:
                        flat_vol_ts_it = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(evalDate, calendar, sigma, daycounter))
                        process = ql.BlackScholesMertonProcess(ql.QuoteHandle(ql.SimpleQuote(spot)), dividend_ts,
                                                               yield_ts, flat_vol_ts_it)
                        option.setPricingEngine(ql.AnalyticEuropeanEngine(process))
                        price = option.NPV()
                        #candidate_prices.append(price)
                        if abs(price - close) < precision:
                            #print('error : ', price - close)
                            error = price - close
                            break
                        sigma -= step
                    implied_vol = sigma
                #print('implied vol : ', implied_vol)
                logMoneyness = math.log(strike / Ft, math.e)
                logMoneynesses.append(logMoneyness)
                strikes.append(strike)
                vol_data.append(implied_vol)
                close_prices.append(close)
                if show : print("%10s %10s %10s %25s %25s %20s" % (spot, strike, close,logMoneyness, implied_vol, error))
    if show : print("-"*110)
    #print('vols:', vol_data)
    #print('close prices: ', close_prices)
    return vol_data,maturitydt,strikes,spot,close_prices,logMoneynesses

def get_impliedvolmat_BS_OTM_oneMaturity(
        evalDate,curve,daycounter,calendar,month,maxVol=1.0,step=0.0001,precision=0.001,show=True):
    try:
        # Get Wind Market Data
        vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
        ql.Settings.instance().evaluationDate = evalDate
        yield_ts = ql.YieldTermStructureHandle(curve)
        dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate,0.0,daycounter))
        vol_data = []
        close_call = []
        close_put = []
        logMoneyness_call = []
        logMoneyness_put = []
        strikes_call = []
        strikes_put = []
        call_volatilities = []
        put_converted_volatilites = []
        call_pair = []
        put_pair =[]
        maturitydt = 0.0
        for idx,optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            if mdate.month == month:
                mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
                strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
                close       = mktData[mktFlds.index('close')][mktindex]
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    call_pair.append((strike,close))
                else:
                    put_pair.append((strike,close))
        call_pair.sort()
        put_pair.sort()
        error_pair = []
        for i in range(len(call_pair)):
            e = abs(call_pair[i][1] - put_pair[i][1])
            error_pair.append((e,call_pair[i][0]))
        error_pair.sort()
        Ft = error_pair[0][1]
        print('error_pair : ',error_pair)
        print('forward price : ',Ft)
        if show:
            print("="*110)
            print("%10s %10s %10s %10s %25s %25s %20s" % ("Type","Spot", "Strike", "close","moneyness", "impliedVol", "Error (%)"))
            print("-"*110)
        for idx,optionid in enumerate(optionids):
            optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
            mdate           = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
            if mdate.month == month:
                maturitydt  = ql.Date(mdate.day, mdate.month, mdate.year)
                mktindex    = mktData[mktFlds.index('option_code')].index(optionid)
                strike      = optionData[optionFlds.index('exercise_price')][optionDataIdx]
                close       = mktData[mktFlds.index('close')][mktindex]
                ttm         = daycounter.yearFraction(evalDate, maturitydt)
                rf          = curve.zeroRate(maturitydt,daycounter,ql.Continuous).rate()
                #Ft          = spot* math.exp(rf*ttm)
                optiontype  = ql.Option.Call
                if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                    eqvlt_close = close
                    implied_vol,error = calculate_vol_BS(
                        maturitydt, optiontype, strike, spot, dividend_ts, yield_ts, eqvlt_close, evalDate,
                        calendar, daycounter, precision, maxVol, step)
                    logMoneyness = math.log(strike / Ft, math.e)
                    logMoneyness_call.append(logMoneyness)
                    strikes_call.append(strike)
                    call_volatilities.append(implied_vol)
                    close_call.append(close)
                    if show: print(
                        "%10s %10s %10s %10s %25s %25s %20s" % ('Call',spot, strike, close, logMoneyness, implied_vol, error))
                else:
                    eqvlt_close = close + spot - math.exp(-rf*ttm) * strike
                    implied_vol, error = calculate_vol_BS(maturitydt, optiontype, strike, spot, dividend_ts, yield_ts,
                                                          eqvlt_close, evalDate,
                                                          calendar, daycounter, precision, maxVol, step)
                    logMoneyness = math.log(strike / Ft, math.e)
                    logMoneyness_put.append(logMoneyness)
                    strikes_put.append(strike)
                    put_converted_volatilites.append(implied_vol)
                    close_put.append(close)
                    if show: print(
                        "%10s %10s %10s %10s %25s %25s %20s" % ('Put', spot, strike, close, logMoneyness, implied_vol, error))
        if show : print("-"*110)
        #print('vols:', vol_data)
        #print('close prices: ', close_prices)
    except:
        print('VolatilityData -- get_impliedvolmat_BS_OTM_oneMaturity failed')
        return
    return call_volatilities,put_converted_volatilites,strikes_call,strikes_put,\
           close_call,close_put,logMoneyness_call,logMoneyness_put,maturitydt,spot

def calculate_PCParity_riskFreeRate_oneMaturity(evalDate,daycounter,calendar,i):
    vols, spot, mktData, mktFlds, optionData, optionFlds,optionids = get_wind_data(evalDate)
    call = {}
    put = {}
    ttm = 0.0
    for idx,optionid in enumerate(optionids):
        optionDataIdx   = optionData[optionFlds.index('wind_code')].index(optionid)
        mdate = pd.to_datetime(optionData[optionFlds.index('exercise_date')][optionDataIdx])
        if mdate.month == evalDate.month() + i:
            mktindex = mktData[mktFlds.index('option_code')].index(optionid)
            close = mktData[mktFlds.index('close')][mktindex]
            strike = optionData[optionFlds.index('exercise_price')][optionDataIdx]
            if optionData[optionFlds.index('call_or_put')][optionDataIdx] == '认购':
                call.update({strike:close})
            else:
                put.update({strike:close})
            maturitydt = ql.Date(mdate.day, mdate.month, mdate.year)
            ttm = daycounter.yearFraction(evalDate, maturitydt)
    count = len(call.keys())
    r_avg = 0.0
    for k, strike in enumerate(call.keys()):
        r = (1/ttm)*math.log((spot+put.get(strike)-call.get(strike))/strike,math.e)
        #print('strike is : ',strike,'rate is : ',r)
        r_avg +=r
    r_avg = r_avg/count
    return r_avg

'''

def get_curve_depo(evalDate,daycounter):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    data   = w.wsd("DR001.IB,DR007.IB,DR014.IB,DR021.IB,DR1M.IB,DR2M.IB,DR3M.IB,DR4M.IB,DR6M.IB,DR9M.IB,DR1Y.IB",
        "ytm_b", datestr, datestr, "returnType=1")
    calendar = ql.China()
    dates  = [
              calendar.advance(evalDate , ql.Period(1,ql.Days)),
              calendar.advance(evalDate , ql.Period(7,ql.Days)),
              calendar.advance(evalDate , ql.Period(14,ql.Days)),
              calendar.advance(evalDate , ql.Period(21,ql.Days)),
              calendar.advance(evalDate , ql.Period(1,ql.Months)),
              calendar.advance(evalDate , ql.Period(2,ql.Months)),
              calendar.advance(evalDate , ql.Period(3,ql.Months)),
              calendar.advance(evalDate , ql.Period(4,ql.Months)),
              calendar.advance(evalDate , ql.Period(6,ql.Months)),
              calendar.advance(evalDate , ql.Period(9,ql.Months)),
              calendar.advance(evalDate , ql.Period(1,ql.Years))]
    try:
        krates = np.divide( data.Data[0], 100)
        #print(dates)
        #print(krates)
        curve  = ql.ForwardCurve(dates,krates,daycounter)
    except:
        print(evalDate,' get curve failed')
        return
    #print(curve.referenceDate(),' , ',curve.maxDate())
    return curve

'''

