import pandas as pd
import numpy as np
import hashlib
import datetime

class BktAccountUtil():

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



class BktAccount(object):

    def __init__(self,leverage=1.0,margin_rate=0.1,init_fund=1000000.0,tick_size=0.0001,
                 contract_multiplier=10000,fee_rate=2.0/10000, nbr_slippage=0):

        self.util = BktAccountUtil()
        self.leverage = leverage
        self.margin_rate = margin_rate
        self.init_fund = init_fund
        self.multiplier = contract_multiplier
        self.tick = tick_size
        self.fee = fee_rate
        self.slippage = nbr_slippage

        self.cash = init_fund
        self.npv = 1.0
        self.mtm_value = 0.0
        self.realized_value = 0.0
        self.nbr_trade = 0
        self.realized_pnl = 0.0
        self.df_trading_book = pd.DataFrame(columns=self.util.tb_columns)  # 持仓信息
        # self.df_holdings = pd.DataFrame(columns=self.util.tb_columns)  # 持仓信息
        self.df_account = pd.DataFrame(columns=self.util.account_columns)  # 交易账户
        self.df_trading_records = pd.DataFrame(columns=self.util.record_columns)  # 交易记录
        self.holdings = []
    def get_sha(self):

        sha = hashlib.sha256()
        now = str(datetime.datetime.now()).encode('utf-8')
        sha.update(now)
        id_position = sha.hexdigest()
        return id_position



    def open_long(self,dt,bktoption,trade_fund,multiplier=None):# 多开
        id_instrument = bktoption.id_instrument
        mkt_price = bktoption.option_price
        long_short = self.util.long
        trade_type = '多开'
        position = pd.Series()
        if multiplier==None:
            multiplier = self.multiplier
        unit = np.floor(trade_fund*self.leverage/(mkt_price*multiplier))
        fee = unit*mkt_price*self.fee*multiplier
        cost = unit*mkt_price*(1+self.fee)*multiplier
        margin_capital = unit*bktoption.get_init_margin()
        bktoption.trade_unit = unit
        bktoption.trade_dt_open = dt
        bktoption.trade_long_short = long_short
        bktoption.trade_cost = cost
        bktoption.trade_open_price = mkt_price
        bktoption.trade_margin_calital = margin_capital

        record = pd.DataFrame(data={self.util.id_instrument:[id_instrument],
                                    self.util.dt_trade:[dt],
                                    self.util.trading_type:[trade_type],
                                    self.util.trade_price:[mkt_price],
                                    self.util.trading_cost:[fee],
                                    self.util.unit:[unit]})
        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        # self.df_holdings = self.df_holdings.append(position,ignore_index=True)
        self.holdings.append(bktoption)
        self.cash = self.cash-margin_capital-fee
        self.nbr_trade += 1

    def open_short(self,dt,bktoption,trade_fund,multiplier=None):
        id_instrument = bktoption.id_instrument
        mkt_price = bktoption.option_price
        long_short = self.util.short
        trade_type = '空开'
        # position = pd.Series()
        if multiplier==None:
            multiplier = self.multiplier
        unit = np.floor(trade_fund*self.leverage/(mkt_price*multiplier))
        fee = unit * mkt_price * self.fee * multiplier
        cost = unit * mkt_price * (1 + self.fee) * multiplier
        margin_capital = unit*bktoption.get_init_margin()
        bktoption.trade_unit = unit
        bktoption.trade_dt_open = dt
        bktoption.trade_long_short = long_short
        bktoption.trade_cost = cost
        bktoption.trade_open_price = mkt_price
        bktoption.margin_calital = margin_capital

        record = pd.DataFrame(data={self.util.id_instrument:[id_instrument],
                                    self.util.dt_trade:[dt],
                                    self.util.trading_type:[trade_type],
                                    self.util.trade_price:[mkt_price],
                                    self.util.trading_cost:[fee],
                                    self.util.unit:[unit]})
        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        # self.df_holdings = self.df_holdings.append(position,ignore_index=True)
        self.holdings.append(bktoption)
        self.cash = self.cash-margin_capital-fee
        self.nbr_trade += 1



    def liquidite_position(self,dt,bktoption): # 多空平仓
        id_instrument = bktoption.id_instrument
        mkt_price = bktoption.option_price
        unit = bktoption.trade_unit
        long_short = bktoption.trade_long_short
        margin_capital = bktoption.trade_margin_calital
        dt_open = bktoption.trade_dt_open
        multiplier = bktoption.multiplier
        cost = bktoption.trade_cost
        open_price = bktoption.trade_open_price
        position = pd.Series()
        position[self.util.id_instrument] = id_instrument
        position[self.util.dt_open] = dt
        position[self.util.long_short] = long_short
        position[self.util.cost] = cost
        position[self.util.open_price] = open_price
        position[self.util.unit] = unit
        position[self.util.margin_capital] = margin_capital
        position[self.util.flag_open] = True
        position[self.util.multiplier] = multiplier
        if long_short == self.util.long:
            trade_type = '多平'
        else:
            trade_type = '空平'
        fee = unit*mkt_price*self.fee*multiplier
        pnl_amt = long_short*(unit*mkt_price*multiplier-cost) - fee
        position[self.util.dt_close] = dt
        position[self.util.days_holding] = (dt - dt_open).days
        position[self.util.close_price] = mkt_price
        position[self.util.realized_pnl] = pnl_amt
        record = pd.DataFrame(data={self.util.id_instrument: [id_instrument],
                                    self.util.dt_trade: [dt],
                                    self.util.trading_type: [trade_type],
                                    self.util.trade_price: [mkt_price],
                                    self.util.trading_cost: [fee],
                                    self.util.unit: [unit]})
        self.df_trading_records = self.df_trading_records.append(record, ignore_index=True)
        self.df_trading_book = self.df_trading_book.append(position, ignore_index=True)
        self.holdings.remove(bktoption)
        self.cash = self.cash + margin_capital + pnl_amt
        self.nbr_trade += 1
        self.realized_pnl += pnl_amt

    def adjust_unit(self,dt,bktoption,trade_fund):
        id_instrument = bktoption.id_instrument
        mkt_price = bktoption.option_price
        holding_unit = bktoption.trade_unit
        long_short = bktoption.trade_long_short
        margin_capital = bktoption.trade_margin_capital
        open_price = bktoption.trade_open_price
        multiplier = bktoption.multiplier
        cost = bktoption.trade_cost
        unit = bktoption.get_trade_unit(trade_fund*self.leverage)
        # unit = np.floor(trade_fund*self.leverage/(mkt_price*multiplier))
        if unit != holding_unit:
            if unit > holding_unit:# 加仓
                margin_add = (unit-holding_unit)*bktoption.get_init_margin()
                open_price = ((unit-holding_unit)*mkt_price+holding_unit*open_price)/unit #加权开仓价格
                cost += (unit-holding_unit)*mkt_price*(1+self.fee)*multiplier
                fee = (unit-holding_unit) * mkt_price * self.fee * multiplier
                self.cash = self.cash-margin_add-fee
                margin_capital += (unit-holding_unit)*bktoption.get_init_margin()

            else: # 减仓
                liquidated_unit = holding_unit - unit
                margin_returned = liquidated_unit*bktoption.get_maintain_margin()
                fee = liquidated_unit*mkt_price*self.fee*multiplier
                liquidated_cost = cost*liquidated_unit/holding_unit
                cost -= liquidated_cost
                realized_pnl = long_short*(liquidated_unit*multiplier*mkt_price
                                           -liquidated_cost)-fee
                self.realized_pnl += realized_pnl
                self.cash = self.cash+margin_returned+realized_pnl
            bktoption.trade_unit = unit
            bktoption.trade_cost = cost
            bktoption.trade_open_price = open_price
            bktoption.margin_calital = margin_capital
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
            record = pd.DataFrame(data={self.util.id_instrument: [id_instrument],
                                        self.util.dt_trade: [dt],
                                        self.util.trading_type: [trade_type],
                                        self.util.trade_price: [mkt_price],
                                        self.util.trading_cost: [fee],
                                        self.util.unit: [unit]})
            self.df_trading_records = self.df_trading_records.append(record, ignore_index=True)
            self.nbr_trade += 1
        else:
            self.liquidite_position(dt,bktoption)

    def switch_long(self):
        return None

    def switch_short(self):
        return None


    def mkm_update(self,dt,df_metric,col_option_price): # 每日更新
        # df_open_trades = self.df_holdings
        unrealized_pnl = 0
        mtm_portfolio_value = 0
        total_margin = 0
        money_utilization = 0
        for bktoption in self.holdings:
            mkt_price = bktoption.option_price
            unit = bktoption.trade_unit
            long_short = bktoption.trade_long_short
            margin_capital = bktoption.trade_margin_capital
            multiplier = bktoption.multiplier
            cost = bktoption.trade_cost
            maintain_margin = unit*bktoption.get_maintain_margin()
            margin_call = maintain_margin-margin_capital
            self.cash -= margin_call
            unrealized_pnl += long_short*(mkt_price*unit*multiplier-cost)
            mtm_portfolio_value += mkt_price*unit*multiplier
            total_margin += maintain_margin
        money_utilization = total_margin/(total_margin+self.cash)
        account = pd.DataFrame(data={self.util.dt_date:[dt],
                                     self.util.nbr_trade:[self.nbr_trade],
                                     self.util.margin_capital:[total_margin],
                                     self.util.realized_pnl:[self.realized_pnl],
                                     self.util.unrealized_pnl: [unrealized_pnl],
                                     self.util.mkm_portfolio_value:[mtm_portfolio_value],
                                     self.util.cash:[self.cash],
                                     self.util.money_utilization:[money_utilization]})
        self.df_account = self.df_account.append(account,ignore_index=True)
        self.npv = (self.cash+total_margin+unrealized_pnl+self.realized_pnl)/self.init_fund
        self.nbr_trade = 0
        self.realized_pnl = 0.0
























































