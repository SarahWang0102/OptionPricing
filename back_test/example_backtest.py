import pandas as pd
import datetime
from back_test.backtest import TradeUtil,BackTestOption

d1_mktprices = {'id1':2,
                'id2':3,
                'id3':4,
      }

d2_mktprices = {'id1':3,
                'id2':2,
                'id3':5,
      }

d3_mktprices = {'id1':4,
                'id2':1,
                'id3':6,
      }
init_fund = 10000000

backtest = BackTestOption()
# dt = datetime.date(2017,12,8)

trade_fund = init_fund/3
long_short = TradeUtil().long
position1 = backtest.open_position(datetime.date(2017,12,8),'id1',d1_mktprices['id1'],trade_fund,long_short)
position2 = backtest.open_position(datetime.date(2017,12,8),'id2',d1_mktprices['id2'],trade_fund,long_short)

id_instrument = 'id1'
backtest.liquidite_position(datetime.date(2017,12,9),'id1',d2_mktprices['id1'],position1)
backtest.mkm_update(datetime.date(2017,12,10),d3_mktprices)
print('df_holdings')
print(backtest.df_holdings)
print(' ')
print('df_trading_records')
print(backtest.df_trading_records)
print(' ')
print('df_trading_book')
print(backtest.df_trading_book)