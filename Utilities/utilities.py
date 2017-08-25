import datetime
import QuantLib as ql
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