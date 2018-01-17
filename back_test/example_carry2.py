import pandas as pd
import QuantLib as ql
from WindPy import w
import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from back_test.account import Account


# start_date = datetime.date(2015, 12, 31)
start_date = datetime.date(2017, 9, 30)
# end_date = datetime.date(2016, 5, 31)
end_date = datetime.date(2017, 12, 31)
# evalDate = datetime.date(2017, 6, 21)

w.start()
calendar = ql.China()
daycounter = ql.ActualActual()
rf = 0.03
engineType = 'AnalyticEuropeanEngine'
dt = 1.0 / 12
init_fund = 10000
hp = 10 # days

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
Option_mkt = dbt.OptionMkt
carry = Table('carry', metadata2, autoload=True)
options = dbt.Options

query = sess2.query(carry)
df_carry = pd.read_sql(query.statement,query.session.bind)
query_optioninfo = sess.query(options)
df_optioninfo = pd.read_sql(query_optioninfo.statement,query_optioninfo.session.bind)
query_metric = sess.query(Option_mkt.dt_date,Option_mkt.id_instrument,Option_mkt.amt_close)
df_metric = pd.read_sql(query_metric.statement,query_metric.session.bind)

##############################################################################################
bkt = Account()
print('=' * 50)
print("%20s %20s %20s" % ("eval date", 'NPV','cash'))
date_range = w.tdays(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d")).Data[0]
i = 0
last_trading_date = date_range[-1].date()
while i < len(date_range):
    evalDate = date_range[i].date()
    mdt_next = w.tdaysoffset(hp, evalDate).Data[0][0].date()
    df_carry_today = df_carry[(df_carry['dt_date']==evalDate)&(df_carry['dt_maturity']>mdt_next)]
    df_carry_today = df_carry_today[df_carry_today['amt_carry'] != -999.0]

    df_call = df_carry_today[df_carry_today['cd_option_type']=='call']\
                .sort_values(by='amt_carry',ascending=False).reset_index()
    df_call_t5 = df_call.loc[0:4]
    df_call_b5 = df_call.loc[len(df_call)-5:]
    df_put = df_carry_today[df_carry_today['cd_option_type']=='put'] \
                .sort_values(by='amt_carry', ascending=False).reset_index()
    df_put_t5 = df_put.loc[0:4]
    df_put_b5 = df_put.loc[len(df_put) - 5:]
    df_metric_today = df_metric[df_metric['dt_date'] == evalDate]
    df_buy = pd.DataFrame()
    df_sell = pd.DataFrame()
    df_buy = df_buy.append(df_call_t5,ignore_index=True)
    df_buy = df_buy.append(df_put_t5,ignore_index=True)
    df_sell = df_sell.append(df_call_b5,ignore_index=True)
    df_sell = df_sell.append(df_put_b5,ignore_index=True)
    cash = bkt.cash
    if cash <= bkt.init_fund / 1000: break
    if i%hp == 0:
        # 平仓
        if len(bkt.df_holdings) != 0:
            for (idx,row) in bkt.df_holdings.iterrows():
                id_instrument = row['id_instrument']
                long_short = row['long_short']
                try:
                    mkt_price = df_metric_today[df_metric_today['id_instrument']==id_instrument]['amt_close'].values[0]
                    mdt = df_optioninfo[df_optioninfo['id_instrument']==id_instrument]['dt_maturity'].values[0]
                except Exception as e:
                    print(id_instrument,evalDate)
                    print(e)

                if mdt<=mdt_next or mdt>=last_trading_date or mdt_next>=last_trading_date:
                    bkt.liquidite_position(evalDate, id_instrument,mkt_price)
                else:
                    if long_short==1 and id_instrument in df_buy['id_instrument']:continue
                    if long_short==-1 and id_instrument in df_sell['id_instrument']: continue
                    try:
                        bkt.liquidite_position(evalDate,id_instrument,mkt_price)
                    except Exception as e:
                        print(evalDate,id_instrument)
                        print(e)

        # 开仓/调仓：
        if mdt_next < last_trading_date:
            for (idx,row) in df_buy.iterrows():
                id_instrument = row['id_instrument']
                # mkt_price = row['amt_option_price']
                mkt_price = df_metric_today[df_metric_today['id_instrument'] == id_instrument]['amt_close'].values[0]
                multiplier = df_optioninfo[df_optioninfo['id_instrument']==id_instrument]['nbr_multiplier'].values[0]
                trading_fund = cash*(1/20)
                if id_instrument in bkt.df_holdings['id_instrument']:
                    bkt.adjust_unit(evalDate,id_instrument,mkt_price,trading_fund)
                else:
                    bkt.open_long(evalDate,id_instrument,mkt_price,trading_fund,multiplier)

            for (idx,row) in df_sell.iterrows():
                id_instrument = row['id_instrument']
                # mkt_price = row['amt_option_price']
                mkt_price = df_metric_today[df_metric_today['id_instrument'] == id_instrument]['amt_close'].values[0]
                multiplier = df_optioninfo[df_optioninfo['id_instrument']==id_instrument]['nbr_multiplier'].values[0]
                trading_fund = cash*(1/20)
                if id_instrument in bkt.df_holdings['id_instrument']:
                    bkt.adjust_unit(evalDate,id_instrument,mkt_price,trading_fund)
                else:
                    bkt.open_short(evalDate,id_instrument,mkt_price,trading_fund,multiplier)

    bkt.mkm_update(evalDate,df_metric_today,'amt_close')
    print("%20s %20s %20s" % (evalDate, bkt.npv,cash))
    i += 1


print(evalDate)
print(mdt_next)
print(bkt.df_holdings)




























































