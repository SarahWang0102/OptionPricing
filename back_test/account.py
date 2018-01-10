import pandas as pd
import numpy as np
import hashlib
import datetime

class TradeUtil():

    def __init__(self):
        self.long = 1
        self.short = -1
        self.hb_columns = ['id_instrument',
                           'dt_trade',
                           'long_short',
                           'trade_price',
                           'trading_cost',
                           'unit',
                           'mkt_price',
                           'margin_capital',
                           'pnl',
                           'mktvalue',
                           'flag_open']

        self.record_columns = ['dt_trade',
                               'id_instrument',
                               'trading_type',
                               'trade_price',
                               'trading_cost',
                               'unit']

        self.tb_columns = ['id_position',
                           'id_instrument',
                           'dt_open',
                           'long_short',
                           'open_price',
                           'open_trading_cost',
                           'unit',
                           'margin_capital',
                           'dt_close',
                           'days_holding',
                           'close_price',
                           'close_trading_cost',
                           'pnl_amt',
                           'yield']

        self.account_columns = ['dt_date',
                                'nbr_trade',
                                'margin_capital',
                                'mkm_pnl',
                                'realized_pnl',
                                'mkm_portfolio_value',
                                'cash',
                                'money_utilization']


class Account(object):

    def __init__(self,leverage=0.5,margin_rate=0.1,init_fund=1000000,tick_size=0.0001,
                 contract_multiplier=10000,fee_rate=1.0/1000, nbr_slippage=0):

        self.util = TradeUtil()
        self.leverage = leverage
        self.margin = margin_rate
        self.init_fund = init_fund
        self.multiplier = contract_multiplier
        self.tick = tick_size
        self.fee = fee_rate
        self.slippage = nbr_slippage

        self.cash = init_fund
        self.mtm_value = 0.0
        self.realized_value = 0.0
        self.df_trading_book = pd.DataFrame(columns=self.util.tb_columns)  # 持仓信息
        self.df_holdings = pd.DataFrame(columns=self.util.hb_columns)  # 持仓信息
        self.df_account = pd.DataFrame(columns=self.util.account_columns)  # 交易账户
        self.df_trading_records = pd.DataFrame()  # 交易记录

    def get_sha(self):

        sha = hashlib.sha256()
        now = str(datetime.datetime.now()).encode('utf-8')
        sha.update(now)
        id_position = sha.hexdigest()
        return id_position

    def open_position(self,dt,id_instrument,mkt_price,trade_fund,long_short):# 多空开仓

        id_position = self.get_sha()
        position = pd.Series()
        unit = np.floor(trade_fund*self.leverage/(self.margin*mkt_price*self.multiplier))
        position['id_instrument'] = id_instrument
        position['dt_open'] = dt
        position['long_short'] = long_short
        position['open_price'] = mkt_price
        position['open_trading_cost'] = unit*mkt_price*self.fee*self.multiplier
        position['unit'] = unit
        position['margin_capital'] = unit*mkt_price*self.multiplier*self.margin
        if long_short == self.util.long : trade_type = '多开'
        else: trade_type = '空开'
        record = pd.DataFrame(data={'id_instrument':[id_instrument],
                                    'dt_trade':[dt],
                                    'trading_type':[trade_type],
                                    'trade_price':[mkt_price],
                                    'trading_cost':[position['open_trading_cost']],
                                    'unit':[unit]})
        holding = pd.DataFrame(data={'id_instrument':[id_instrument],
                                     'dt_trade':[dt],
                                     'long_short':[long_short],
                                     'trade_price':[mkt_price],
                                     'trading_cost':[position['open_trading_cost']],
                                     'unit':[unit],
                                     'mkt_price':[mkt_price],
                                     'margin_capital':[position['margin_capital']],
                                     'flag_open':[True]})
        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        self.df_holdings = self.df_holdings.append(holding,ignore_index=True)
        self.cash = self.cash-position['margin_capital']-position['open_trading_cost']
        return position


    def liquidite_position(self,dt,id_instrument,mkt_price,position): # 多空平仓

        position['dt_close'] = dt
        position['days_holding'] = (dt-position['dt_open']).days
        position['close_price'] = mkt_price
        position['close_trading_cost'] = position['unit']*mkt_price*self.fee*self.multiplier
        position['pnl_amt'] = position['unit']*position['long_short']*(mkt_price-position['open_price'])\
                            *self.multiplier-position['open_trading_cost']-position['close_trading_cost']
        position['yield'] = position['pnl_amt']/position['margin_capital']
        if position['long_short'] == self.util.long : trade_type = '多平'
        else: trade_type = '空平'
        record = pd.DataFrame(data={'id_instrument':[id_instrument],
                                    'dt_trade':[dt],
                                    'trading_type':[trade_type],
                                    'trade_price':[mkt_price],
                                    'trading_cost':[position['close_trading_cost']],
                                    'unit':[position['unit']]})

        self.df_holdings.loc[self.df_holdings['id_instrument']==position['id_instrument'],'flag_open'] = False
        self.df_holdings.loc[self.df_holdings['id_instrument']==position['id_instrument'],'trading_cost'] = \
            position['open_trading_cost']+position['close_trading_cost']

        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        self.df_trading_book = self.df_trading_book.append(position,ignore_index=True)
        self.cash = self.cash+position['margin_capital']-position['close_trading_cost']
        return position


    def mkm_update(self,dt,dict_closes_by_ids): # 每日更新

        self.df_holdings['pnl'] = (self.df_holdings['mkt_price']-self.df_holdings['trade_price']
                                   - self.df_holdings['trading_cost'])*self.df_holdings['unit']
        self.df_holdings['mktvalue'] = self.df_holdings['mkt_price']*self.df_holdings['unit']
        df_open_trades = self.df_holdings[self.df_holdings['flag_open']]
        df_closed = self.df_holdings[self.df_holdings['flag_open'] == False]
        for (idx,row) in df_open_trades.iterrows():
            id_instrument = row['id_instrument']
            mkt_price = dict_closes_by_ids[id_instrument]
            margin = mkt_price*row['unit']*self.multiplier*self.margin
            margin_call = margin-row['margin_capital']
            self.cash -= margin_call
            df_open_trades.loc[idx,'margin_capital'] = margin
            df_open_trades.loc[idx,'mkt_price'] = mkt_price

        mtm_pnl = df_open_trades['pnl'].sum()
        mtm_portfolio_value = df_open_trades['mktvalue'].sum()
        total_margin = df_open_trades['margin_capital'].sum()
        realized_pnl = df_closed['pnl'].sum()
        # realized_yield = realized_pnl/df_closed['margin_capital'].sum()
        money_utilization = total_margin/(total_margin+self.cash)
        account = pd.DataFrame(data={'dt_date':[dt],
                                     'nbr_trade':[len(df_open_trades)],
                                     'margin_capital':[total_margin],
                                     'mtm_pnl':[mtm_pnl],
                                     'realized_pnl':[realized_pnl],
                                     'mkm_portfolio_value':[mtm_portfolio_value],
                                     'cash':[self.cash],
                                     'money_utilization':[money_utilization]})
        self.df_account.append(account,ignore_index=True)
        self.df_holdings = self.df_holdings[self.df_holdings['flag_open']]






















































