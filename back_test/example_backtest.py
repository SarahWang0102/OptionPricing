import pandas as pd
import datetime
from back_test.account import TradeUtil,Account

d1 = {'id1':[2],'id2':[3],'id3':[4]}
df = pd.DataFrame(d1)
print('df')
print(df)
print(df['id1'])

print(df.id1)
d1_mktprices = {'id1':2,
                'id2':3,
                'id3':4}
d2_mktprices = {'id1':3,
                'id2':2,
                'id3':5}

d3_mktprices = {'id1':4,
                'id2':1,
                'id3':6}
init_fund = 1000000
backtest = Account() # 一笔资金投资于期权

trade_fund = init_fund/3
long_short = TradeUtil().long
# 买入期权1：id1,用1/3的资金
position1 = backtest.open_position(datetime.date(2017,12,8),'id1',
                                   d1_mktprices['id1'],trade_fund,long_short)
# 买入期权2：id2
position2 = backtest.open_position(datetime.date(2017,12,8),'id2',d1_mktprices['id2'],trade_fund,long_short)

id_instrument = 'id1'
backtest.liquidite_position(datetime.date(2017,12,9),'id1',d2_mktprices['id1'],position1)
backtest.mkm_update(datetime.date(2017,12,9),d3_mktprices)
backtest.mkm_update(datetime.date(2017,12,10),d3_mktprices)
print('df_holdings')
print(backtest.df_holdings)
print(' ')
print('df_trading_records')
print(backtest.df_trading_records)
print(' ')
print('df_trading_book')
print(backtest.df_trading_book)