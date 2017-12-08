from sqlalchemy import orm, create_engine, MetaData, Table, inspect, join, select
from sqlalchemy.engine import reflection
import datetime
import pandas as pd
from WindPy import w

w.start()
engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
options_mkt = Table('options_mktdata', metadata, autoload=True)
futures_mkt = Table('futures_mktdata', metadata, autoload=True)

# res = options_mkt.select(sql).execute()
# result = res.fetchall()


start_date = datetime.date(2017, 3, 31).strftime("%Y-%m-%d")
# end_date = datetime.date(2017, 12, 7)
end_date = datetime.date(2017, 4, 7).strftime("%Y-%m-%d")

evalDate = start_date
while evalDate < end_date:
    evalDate = w.tdaysoffset(1, evalDate, "Period=W").Data[0][0].date()
    print(evalDate)
    sql = (options_mkt.c.dt_date  == evalDate) & \
          (futures_mkt.c.dt_date == evalDate) & \
          (options_mkt.c.flag_night  == 0) & \
          (futures_mkt.c.flag_night == 0) & \
          (options_mkt.c.datasource == 'dce') & \
          (options_mkt.c.id_underlying == futures_mkt.c.id_instrument)
    result = select([options_mkt.c.id_instrument,options_mkt.c.amt_strike, futures_mkt], sql).execute()
    for r in result:
        print(r)
    # dataset = result.fetchall()
    # print(dataset)
    # print(dataset[0].keys())
    # for k in dataset[0].keys():
    #     print(k,dataset[0][k])
    # dataset = []
    # for r in result:
    #     dataset.append(dict(r.items()))
    # print(dataset)
    evalDate = evalDate.strftime("%Y-%m-%d")
