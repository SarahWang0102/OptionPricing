import datetime
import QuantLib as ql
def convert_datelist_from_ql_to_datetime(ql_dates):
    datetime_dates = []
    for d in ql_dates:
        dt = datetime.date(d.year(),d.month(),d.dayOfMonth())
        datetime_dates.append(dt)
    return datetime_dates

def convert_datelist_from_datetime_to_ql(datetime_dates):
    ql_dates = []
    for d in datetime_dates:
        dt = ql.Date(d.day,d.month,d.year)
        ql_dates.append(dt)
    return ql_dates

def convert_date_from_datetime_to_ql(datetime_date):
    dt = ql.Date(datetime_date.day,datetime_date.month,datetime_date.year)
    return dt

def convert_date_from_ql_to_datetime(ql_date):
    dt = datetime.date(ql_date.year(), ql_date.month(), ql_date.dayOfMonth())
    return dt