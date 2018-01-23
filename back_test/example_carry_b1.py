import pandas as pd
import QuantLib as ql
import datetime
from WindPy import w
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from back_test.bkt_option import BktUtil
from back_test.bkt_option_set import OptionSet
from back_test.bkt_account import BktAccount

# start_date = datetime.date(2015, 3, 31)
start_date = datetime.date(2017, 9, 1)
end_date = datetime.date(2017, 12, 1)
# end_date = datetime.date(2017, 12, 31)
# evalDate = datetime.date(2017, 6, 21)
hp = 20

w.start()
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
query_mkt = sess.query(Option_mkt.dt_date,Option_mkt.id_instrument,Option_mkt.code_instrument,
                        Option_mkt.amt_close,Option_mkt.amt_settlement,Option_mkt.amt_last_settlement,
                        Option_mkt.amt_trading_volume
                          ) \
    .filter(Option_mkt.dt_date >= start_date) \
    .filter(Option_mkt.dt_date <= end_date) \
    .filter(Option_mkt.datasource == 'wind')

query_option = sess.query(options.id_instrument,options.cd_option_type,options.amt_strike,
                          options.dt_maturity,options.nbr_multiplier) \
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

# last_trading_date = bkt_optionset.dt_list[-1]
money_utilization = 0.2
buy_ratio = 0.5
sell_ratio = 0.5
while bkt_optionset.index < len(bkt_optionset.dt_list):
    if bkt_optionset.index == 0 :
        bkt_optionset.next()
        continue

    evalDate = bkt_optionset.eval_date
    hp_enddate = w.tdaysoffset(hp, evalDate).Data[0][0].date()

    call_list = bkt_optionset.bktoption_list_call

    df_call_ranked = bkt_optionset.rank_by_carry(call_list)
    df_call_ranked = df_call_ranked[df_call_ranked['amt_carry'] != -999.0]

    df_buy = df_call_ranked.loc[0:4]
    df_sell = df_call_ranked.loc[len(df_call_ranked) - 5:]
    df_metrics_today = df_option[(df_option['dt_date']==evalDate)]

    # 到期全部清仓
    if evalDate == bkt_optionset.end_date:
        print(' Liquidate all possitions !!! ')
        bkt.liquidate_all(evalDate)
        break

    for bktoption in  bkt.holdings:
        if bktoption.maturitydt <= evalDate:
            print('Liquidate position at maturity : ',evalDate,' , ',bktoption.maturitydt)
            bkt.close_position(evalDate, bktoption)

    if (bkt_optionset.index-1) % hp == 0:
        print('调仓 : ',evalDate)

        # 平仓
        for bktoption in  bkt.holdings:
            if bktoption.maturitydt <= hp_enddate:
                bkt.close_position(evalDate, bktoption)
            else:
                if bktoption.trade_long_short == 1 and bktoption in df_buy['bktoption']: continue
                if bktoption.trade_long_short == -1 and bktoption in df_sell['bktoption']: continue
                bkt.close_position(evalDate,bktoption)

        # 开仓
        fund_buy = bkt.cash*money_utilization*buy_ratio
        fund_sell = bkt.cash*money_utilization*sell_ratio
        if hp_enddate < bkt_optionset.end_date:
            n1 = len(df_buy)
            n2 = len(df_sell)

            for (idx,row) in df_buy.iterrows():
                bktoption = row['bktoption']
                if bktoption in bkt.holdings and bktoption.trade_flag_open:
                    bkt.rebalance_position(evalDate,bktoption,fund_buy/n1)
                else:
                    bkt.open_long(evalDate,bktoption,fund_buy/n1)

            for (idx,row) in df_sell.iterrows():
                bktoption = row['bktoption']
                if bktoption in bkt.holdings and bktoption.trade_flag_open:
                    bkt.rebalance_position(evalDate, bktoption, fund_sell/n2)
                else:
                    bkt.open_short(evalDate, bktoption, fund_sell/n2)

    bkt.mkm_update(evalDate,df_metrics_today,'amt_close')

    print(evalDate , ' : ',bkt.npv,' , ',bkt.cash)

    bkt_optionset.next()
    print(bkt.df_account)

print(evalDate , ' : ',bkt.npv,' , ',bkt.cash)
# print(bkt.df_account)
print(bkt.holdings)








































