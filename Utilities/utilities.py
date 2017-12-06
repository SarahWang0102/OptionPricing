import datetime
import QuantLib as ql
from Utilities.svi_read_data import get_curve_treasury_bond

def to_dt_dates(ql_dates):
    datetime_dates = []
    for d in ql_dates:
        dt = datetime.date(d.year(),d.month(),d.dayOfMonth())
        datetime_dates.append(dt)
    return datetime_dates

def to_ql_dates(datetime_dates):
    ql_dates = []
    for d in datetime_dates:
        dt = ql.Date(d.day,d.month,d.year)
        ql_dates.append(dt)
    return ql_dates

def to_ql_date(datetime_date):
    dt = ql.Date(datetime_date.day,datetime_date.month,datetime_date.year)
    return dt

def to_dt_date(ql_date):
    dt = datetime.date(ql_date.year(), ql_date.month(), ql_date.dayOfMonth())
    return dt


def get_mdate_by_contractid(commodityType,contractId,calendar):
    maturity_date = 0
    if commodityType == 'm':
        year = '20' + contractId[0: 2]
        month = contractId[-2:]
        date = ql.Date(1, int(month), int(year))
        maturity_date = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(4, ql.Days))
    elif commodityType == 'sr':
        year = '201' + contractId[2]
        month = contractId[-2:]
        date = ql.Date(1, int(month), int(year))
        maturity_date = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(-5, ql.Days))
    return maturity_date

def get_rf_tbcurve(evalDate,daycounter,maturitydate):
    curve = get_curve_treasury_bond(evalDate, daycounter)
    maxdate = curve.maxDate()
    #print(maxdate,maturitydate)
    if maturitydate > maxdate:
        rf = curve.zeroRate(maxdate, daycounter, ql.Continuous).rate()
    else:
        rf = curve.zeroRate(maturitydate, daycounter, ql.Continuous).rate()
    return rf

def get_yield_ts(evalDate,curve,mdate,daycounter):
    maxdate = curve.maxDate()
    if mdate > maxdate:
        rf = curve.zeroRate(maxdate, daycounter, ql.Continuous).rate()
    else:
        rf = curve.zeroRate(mdate, daycounter, ql.Continuous).rate()
    yield_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, rf, daycounter))
    return yield_ts

def get_dividend_ts(evalDate,daycounter):
    dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
    return dividend_ts

def get_closest_strike(strikes,target):
    res = strikes[0]
    emin = 100.0
    for strike in strikes:
        e = strike-target
        if e < emin : res = strike
    return res