import pandas as pd
import QuantLib as ql
import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from back_test.bkt_option import BktUtil
from back_test.bkt_option_set import OptionSet
from back_test.bkt_account import BktAccount

# start_date = datetime.date(2015, 3, 31)
start_date = datetime.date(2017, 9, 1)
end_date = datetime.date(2017, 11, 10)
# end_date = datetime.date(2017, 12, 31)
# evalDate = datetime.date(2017, 6, 21)
hp = 20


engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
engine2 = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/metrics', echo=False)
conn2 = engine2.connect()
metadata2 = MetaData(engine2)
Session2 = sessionmaker(bind=engine2)
sess2 = Session2()
Index_mkt = dbt.IndexMkt
Option_mkt = dbt.OptionMkt
option_intd = dbt.OptionMktIntraday
carry1 = Table('carry1', metadata2, autoload=True)
options = dbt.Options
calendar = ql.China()
daycounter = ql.ActualActual()
util = BktUtil()
open_trades = []
query_mkt = sess.query(Option_mkt.dt_date,
                        Option_mkt.id_instrument,
                        Option_mkt.code_instrument,
                        Option_mkt.amt_close,
                        Option_mkt.amt_settlement,
                        Option_mkt.amt_last_settlement,
                        Option_mkt.amt_trading_volume
                          ) \
    .filter(Option_mkt.dt_date >= start_date) \
    .filter(Option_mkt.dt_date <= end_date) \
    .filter(Option_mkt.datasource == 'wind')

query_option = sess.query(options.id_instrument,
                          options.cd_option_type,
                          options.amt_strike,
                          options.dt_maturity,
                          options.nbr_multiplier) \
    .filter(and_(options.dt_listed <= end_date,options.dt_maturity >= start_date))


query_etf = sess.query(Index_mkt.dt_date,Index_mkt.amt_close) \
    .filter(Index_mkt.dt_date >= start_date) \
    .filter(Index_mkt.dt_date <= end_date) \
    .filter(Index_mkt.id_instrument == 'index_50etf')

df_mkt = pd.read_sql(query_mkt.statement, query_mkt.session.bind)
df_contract = pd.read_sql(query_option.statement, query_option.session.bind)
df_50etf = pd.read_sql(query_etf.statement, query_etf.session.bind).rename(columns={'amt_close':util.col_underlying_price})
df_option = df_mkt.join(df_contract.set_index('id_instrument'),how='left',on='id_instrument')
df_option = df_option.join(df_50etf.set_index('dt_date'),how='left',on='dt_date')

bkt = BktAccount()
bkt_optionset = OptionSet('daily',df_option,hp)
bktoption_list = bkt_optionset.bktoption_list

print('start_date : ',bkt_optionset.start_date)
print('end_date : ',bkt_optionset.end_date)


while bkt_optionset.index < len(bkt_optionset.dt_list):
    print(bkt_optionset.eval_date)
    option_list = bkt_optionset.bktoption_list
    if len(option_list) == 0:
        bkt_optionset.next()
        continue
    df_carry,res = bkt_optionset.collect_carry(option_list)
    df_carry = df_carry[df_carry['amt_carry'] != -999.0]
    df_call = df_carry[df_carry['cd_option_type'] == 'call'] \
        .sort_values(by='amt_carry', ascending=False).reset_index()
    mdt_next = w.tdaysoffset(hp, evalDate).Data[0][0].date()

    df_call_t5 = df_call.loc[0:4]



    bkt_optionset.next()











































