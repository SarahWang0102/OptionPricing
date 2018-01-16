import pandas as pd
import numpy as np
import hashlib
import datetime

class TradeUtil():

    def __init__(self):
        self.long = 1
        self.short = -1
        self.id_position='id_position'
        self.id_instrument='id_instrument'
        self.multiplier='multiplier'
        self.mkt_price = 'mkt_price'
        self.dt_open='dt_open'
        self.long_short='long_short'
        self.open_price='open_price'
        self.cost='cost'
        # self.open_trading_cost='open_trading_cost'
        self.unit='unit'
        self.margin_capital='margin_capital'
        self.dt_close='dt_close'
        self.days_holding='days_holding'
        self.close_price='close_price'
        # self.close_trading_cost='close_trading_cost'
        self.realized_pnl='realized_pnl'
        self.unrealized_pnl='unrealized_pnl'
        self.flag_open = 'flag_open'

        self.dt_date='dt_date'
        self.nbr_trade='nbr_trade'
        self.margin_capital='margin_capital'
        self.mkm_pnl='mkm_pnl'
        self.realized_pnl='realized_pnl'
        self.mkm_portfolio_value='mkm_portfolio_value'
        self.cash='cash'
        self.money_utilization='money_utilization'

        self.dt_trade = 'dt_trade'
        self.trading_type='trading_type'
        self.trade_price='trade_price'
        self.trading_cost='trading_cost'


        self.tb_columns = [
                           self.id_instrument,
                           self.multiplier,
                           self.mkt_price,
                           self.dt_open,
                           self.long_short,
                           self.open_price,
                           self.cost,
                           # self.open_trading_cost,
                           self.unit,
                           self.margin_capital,
                           self.dt_close,
                           self.days_holding,
                           self.close_price,
                           # self.close_trading_cost,
                           self.realized_pnl,
                           self.unrealized_pnl,
                           self.flag_open]

        self.account_columns = [self.dt_date,
                                self.nbr_trade,
                                self.margin_capital,
                                self.realized_pnl,
                                self.unrealized_pnl,
                                self.mkm_portfolio_value,
                                self.cash,
                                self.money_utilization]

        self.record_columns = [self.dt_trade,
                               self.id_instrument,
                               self.trading_type,
                               self.trade_price,
                               self.trading_cost,
                               self.unit]



class Account(object):

    def __init__(self,leverage=0.5,margin_rate=0.1,init_fund=1000000.0,tick_size=0.0001,
                 contract_multiplier=10000,fee_rate=2.0/10000, nbr_slippage=0):

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
        self.nbr_trade = 0
        self.realized_pnl = 0.0
        self.df_trading_book = pd.DataFrame(columns=self.util.tb_columns)  # 持仓信息
        self.df_holdings = pd.DataFrame(columns=self.util.tb_columns)  # 持仓信息
        self.df_account = pd.DataFrame(columns=self.util.account_columns)  # 交易账户
        self.df_trading_records = pd.DataFrame(columns=self.util.record_columns)  # 交易记录

    def get_sha(self):

        sha = hashlib.sha256()
        now = str(datetime.datetime.now()).encode('utf-8')
        sha.update(now)
        id_position = sha.hexdigest()
        return id_position


    def open_long(self,dt,id_instrument,mkt_price,trade_fund,multiplier=None):# 多空开仓
        long_short = self.util.long
        trade_type = '多开'
        position = pd.Series()
        if multiplier==None:
            multiplier = self.multiplier
        unit = np.floor(trade_fund*self.leverage/(self.margin*mkt_price*multiplier))
        fee = unit*mkt_price*self.fee*multiplier
        cost = unit*mkt_price*(1+self.fee)*multiplier
        position[self.util.id_instrument] = id_instrument
        position[self.util.dt_open] = dt
        position[self.util.long_short] = long_short
        position[self.util.cost] = cost
        position[self.util.open_price] = mkt_price
        position[self.util.unit] = unit
        position[self.util.margin_capital] = unit*mkt_price*multiplier*self.margin
        position[self.util.flag_open] = True
        position[self.util.multiplier] = multiplier

        record = pd.DataFrame(data={self.util.id_instrument:[id_instrument],
                                    self.util.dt_trade:[dt],
                                    self.util.trading_type:[trade_type],
                                    self.util.trade_price:[mkt_price],
                                    self.util.trading_cost:[fee],
                                    self.util.unit:[unit]})
        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        self.df_holdings = self.df_holdings.append(position,ignore_index=True)
        self.cash = self.cash-position[self.util.margin_capital]-fee
        self.nbr_trade += 1

    def open_short(self,dt,id_instrument,mkt_price,trade_fund,multiplier=None):
        long_short = self.util.short
        trade_type = '空开'
        position = pd.Series()
        if multiplier==None:
            multiplier = self.multiplier
        unit = np.floor(trade_fund * self.leverage / (self.margin * mkt_price * multiplier))
        fee = unit * mkt_price * self.fee * multiplier
        cost = unit * mkt_price * (1 + self.fee) * multiplier
        position[self.util.id_instrument] = id_instrument
        position[self.util.dt_open] = dt
        position[self.util.long_short] = long_short
        position[self.util.cost] = cost
        position[self.util.open_price] = mkt_price
        position[self.util.unit] = unit
        position[self.util.margin_capital] = unit * mkt_price * multiplier * self.margin
        position[self.util.flag_open] = True
        position[self.util.multiplier] = multiplier

        record = pd.DataFrame(data={self.util.id_instrument:[id_instrument],
                                    self.util.dt_trade:[dt],
                                    self.util.trading_type:[trade_type],
                                    self.util.trade_price:[mkt_price],
                                    self.util.trading_cost:[fee],
                                    self.util.unit:[unit]})
        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        self.df_holdings = self.df_holdings.append(position,ignore_index=True)
        self.cash = self.cash-position[self.util.margin_capital]-fee
        self.nbr_trade += 1


    def liquidate_long(self,dt,id_instrument,mkt_price):
        position = self.df_holdings[self.df_holdings[self.util.id_instrument]==id_instrument]
        unit = position[self.util.unit].values[0]
        long_short = position[self.util.long_short].values[0]
        open_trading_cost = position[self.util.open_trading_cost].values[0]
        margin_capital = position[self.util.margin_capital].values[0]
        open_price = position[self.util.open_price].values[0]
        dt_open = position[self.util.dt_open].values[0]
        multiplier = position[self.util.multiplier].values[0]
        if long_short != self.util.long :
            print(id_instrument,' liquidate long position function encounter short holding!')
            return
        trade_type = '多平'
        close_trading_cost = unit*mkt_price*self.fee*multiplier
        pnl_amt = unit*long_short*(mkt_price-open_price)*multiplier-open_trading_cost-close_trading_cost
        position[self.util.dt_close] = dt
        position[self.util.days_holding] = (dt-dt_open).days
        position[self.util.close_price] = mkt_price
        position[self.util.close_trading_cost] = close_trading_cost
        position[self.util.realized_pnl] = pnl_amt
        position[self.util.flag_open] = False
        position[self.util.unrealized_pnl] = 0.0

        record = pd.DataFrame(data={self.util.id_instrument:[id_instrument],
                                    self.util.dt_trade:[dt],
                                    self.util.trading_type:[trade_type],
                                    self.util.trade_price:[mkt_price],
                                    self.util.trading_cost:[close_trading_cost],
                                    self.util.unit:[unit]})

        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        self.df_trading_book = self.df_trading_book.append(position,ignore_index=True)
        self.cash = self.cash+margin_capital-close_trading_cost
        self.df_holdings = self.df_holdings[self.df_holdings[self.util.id_instrument]!=id_instrument].reset_index()
        self.nbr_trade += 1
        self.realized_pnl += pnl_amt


    def liquidate_short(self,dt,id_instrument,mkt_price):
        position = self.df_holdings[self.df_holdings[self.util.id_instrument] == id_instrument]
        unit = position[self.util.unit].values[0]
        long_short = position[self.util.long_short].values[0]
        open_trading_cost = position[self.util.open_trading_cost].values[0]
        margin_capital = position[self.util.margin_capital].values[0]
        open_price = position[self.util.open_price].values[0]
        dt_open = position[self.util.dt_open].values[0]
        multiplier = position[self.util.multiplier].values[0]
        if long_short != self.util.short :
            print(id_instrument,' liquidate short position function encounter long holding!')
            return
        trade_type = '空平'
        close_trading_cost = unit*mkt_price*self.fee*multiplier
        pnl_amt = unit * long_short * (
        mkt_price - open_price)*multiplier - open_trading_cost - close_trading_cost
        position[self.util.dt_close] = dt
        position[self.util.days_holding] = (dt - dt_open).days
        position[self.util.close_price] = mkt_price
        position[self.util.close_trading_cost] = close_trading_cost
        position[self.util.realized_pnl] = pnl_amt
        position[self.util.flag_open] = False
        position[self.util.unrealized_pnl] = 0.0

        record = pd.DataFrame(data={self.util.id_instrument: [id_instrument],
                                    self.util.dt_trade: [dt],
                                    self.util.trading_type: [trade_type],
                                    self.util.trade_price: [mkt_price],
                                    self.util.trading_cost: [close_trading_cost],
                                    self.util.unit: [unit]})

        self.df_trading_records = self.df_trading_records.append(record, ignore_index=True)
        self.df_trading_book = self.df_trading_book.append(position, ignore_index=True)
        self.cash = self.cash + margin_capital - close_trading_cost
        self.df_holdings = self.df_holdings[self.df_holdings[self.util.id_instrument]!=id_instrument].reset_index()
        self.nbr_trade += 1
        self.realized_pnl += pnl_amt


    def liquidite_position(self,dt,id_instrument,mkt_price): # 多空平仓
        position = self.df_holdings[self.df_holdings[self.util.id_instrument] == id_instrument]
        unit = position[self.util.unit].values[0]
        long_short = position[self.util.long_short].values[0]
        margin_capital = position[self.util.margin_capital].values[0]
        dt_open = position[self.util.dt_open].values[0]
        multiplier = position[self.util.multiplier].values[0]
        cost = position[self.util.cost].values[0]
        if long_short == self.util.long:
            trade_type = '多平'
        else:
            trade_type = '空平'
        close_trading_cost = unit*mkt_price*self.fee*multiplier
        pnl_amt = long_short*(unit*mkt_price*multiplier-cost) - close_trading_cost
        position[self.util.dt_close] = dt
        position[self.util.days_holding] = (dt - dt_open).days
        position[self.util.close_price] = mkt_price
        position[self.util.realized_pnl] = pnl_amt
        position[self.util.flag_open] = False
        position[self.util.unrealized_pnl] = 0.0

        record = pd.DataFrame(data={self.util.id_instrument: [id_instrument],
                                    self.util.dt_trade: [dt],
                                    self.util.trading_type: [trade_type],
                                    self.util.trade_price: [mkt_price],
                                    self.util.trading_cost: [close_trading_cost],
                                    self.util.unit: [unit]})

        self.df_trading_records = self.df_trading_records.append(record, ignore_index=True)
        self.df_trading_book = self.df_trading_book.append(position, ignore_index=True)
        self.cash = self.cash + margin_capital - close_trading_cost
        self.df_holdings = self.df_holdings[self.df_holdings[self.util.id_instrument]!=id_instrument]
        self.nbr_trade += 1
        self.realized_pnl += pnl_amt

    def adjust_unit(self,dt,id_instrument,mkt_price,trade_fund):
        idx = self.df_holdings[self.util.id_instrument] == id_instrument
        position = self.df_holdings[idx]
        holding_unit = position[self.util.unit].values[0]
        multiplier = position[self.util.multiplier]
        unit = np.floor(trade_fund*self.leverage/(self.margin*mkt_price*multiplier))
        long_short = position[self.util.long_short].values[0]
        margin_capital = position[self.util.margin_capital].values[0]
        open_price = position[self.util.open_price].values[0]
        multiplier = position[self.util.multiplier].values[0]
        cost = position[self.util.cost].values[0]

        if unit != holding_unit:
            margin_capital += (unit-holding_unit)* mkt_price * multiplier * self.margin

            if unit > holding_unit:# 加仓
                open_price = ((unit-holding_unit)*mkt_price+holding_unit*open_price)/unit #加权开仓价格
                cost += (unit-holding_unit)*mkt_price*(1+self.fee)*multiplier
            else: # 减仓
                liquidated_unit = holding_unit - unit
                fee = liquidated_unit*mkt_price*self.fee*multiplier
                liquidated_cost = cost*liquidated_unit/holding_unit
                cost -= liquidated_cost
                realized_pnl = long_short*(liquidated_unit*multiplier*mkt_price-liquidated_cost)-fee
                self.realized_pnl += realized_pnl

            self.cash -= margin_capital
            self.df_holdings[idx,self.util.unit] = unit
            self.df_holdings[idx,self.util.open_price] = open_price
            self.df_holdings[idx,self.util.cost] = cost
            self.df_holdings[idx,self.util.margin_capital] = margin_capital

            if long_short == self.util.long:
                if unit > holding_unit:
                    trade_type = '多开'
                else:
                    trade_type = '多平'
            else:
                if unit > holding_unit:
                    trade_type = '空开'
                else:
                    trade_type = '空平'
            record_trading_cost = abs(unit-holding_unit)*mkt_price*self.fee*multiplier
            record = pd.DataFrame(data={self.util.id_instrument: [id_instrument],
                                        self.util.dt_trade: [dt],
                                        self.util.trading_type: [trade_type],
                                        self.util.trade_price: [mkt_price],
                                        self.util.trading_cost: [record_trading_cost],
                                        self.util.unit: [unit]})
            self.df_trading_records = self.df_trading_records.append(record, ignore_index=True)
            self.cash = self.cash - position[self.util.margin_capital] - position[self.util.open_trading_cost]
            self.nbr_trade += 1

    def switch_long(self):
        return None

    def switch_short(self):
        return None
    #
    # def open_position(self,dt,id_instrument,mkt_price,trade_fund,long_short):# 多空开仓
    #
    #     id_position = self.get_sha()
    #     position = pd.Series()
    #     unit = np.floor(trade_fund*self.leverage/(self.margin*mkt_price*self.multiplier))
    #     position['id_instrument'] = id_instrument
    #     position['dt_open'] = dt
    #     position['long_short'] = long_short
    #     position['open_price'] = mkt_price
    #     position['open_trading_cost'] = unit*mkt_price*self.fee*self.multiplier
    #     position['unit'] = unit
    #     position['margin_capital'] = unit*mkt_price*self.multiplier*self.margin
    #     if long_short == self.util.long : trade_type = '多开'
    #     else: trade_type = '空开'
    #     record = pd.DataFrame(data={'id_instrument':[id_instrument],
    #                                 'dt_trade':[dt],
    #                                 'trading_type':[trade_type],
    #                                 'trade_price':[mkt_price],
    #                                 'trading_cost':[position['open_trading_cost']],
    #                                 'unit':[unit]})
    #     holding = pd.DataFrame(data={'id_instrument':[id_instrument],
    #                                  'dt_trade':[dt],
    #                                  'long_short':[long_short],
    #                                  'trade_price':[mkt_price],
    #                                  'trading_cost':[position['open_trading_cost']],
    #                                  'unit':[unit],
    #                                  'mkt_price':[mkt_price],
    #                                  'margin_capital':[position['margin_capital']],
    #                                  'flag_open':[True]})
    #     self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
    #     self.df_holdings = self.df_holdings.append(holding,ignore_index=True)
    #     self.cash = self.cash-position['margin_capital']-position['open_trading_cost']
    #     return position



    def mkm_update(self,dt,df_metric): # 每日更新
        df_open_trades = self.df_holdings[self.df_holdings[self.util.flag_open]]
        for (idx,row) in df_open_trades.iterrows():
            id_instrument = row[self.util.id_instrument]
            mkt_price = df_metric[df_metric['id_instrument']==id_instrument]['amt_option_price'].values[0]
            margin = mkt_price*row[self.util.unit]*row[self.util.multiplier]*self.margin
            margin_call = margin-row[self.util.margin_capital]
            self.cash -= margin_call
            df_open_trades.loc[idx,self.util.margin_capital] = margin
            df_open_trades.loc[idx,self.util.mkt_price] = mkt_price
        unrealized_pnl = df_open_trades[self.util.unrealized_pnl].sum()
        mtm_portfolio_value = sum(df_open_trades[self.util.mkt_price]*df_open_trades[self.util.unit])
        total_margin = df_open_trades[self.util.margin_capital].sum()
        money_utilization = total_margin/(total_margin+self.cash)

        account = pd.DataFrame(data={self.util.dt_date:[dt],
                                     self.util.nbr_trade:[self.nbr_trade],
                                     self.util.margin_capital:[total_margin],
                                     self.util.unrealized_pnl:[unrealized_pnl],
                                     self.util.realized_pnl:[self.realized_pnl],
                                     self.util.mkm_portfolio_value:[mtm_portfolio_value],
                                     self.util.cash:[self.cash],
                                     self.util.money_utilization:[money_utilization]})
        self.df_account.append(account,ignore_index=True)
        self.df_holdings = self.df_holdings[self.df_holdings[self.util.flag_open]]
        self.nbr_trade = 0
        self.realized_pnl = 0.0
























































