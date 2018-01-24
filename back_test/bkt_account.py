import pandas as pd
import hashlib
import datetime
from back_test.bkt_util import BktUtil



class BktAccount(object):

    def __init__(self,leverage=1.0,margin_rate=0.1,init_fund=1000000.0,tick_size=0.0001,
                 contract_multiplier=10000,fee_rate=2.0/10000, nbr_slippage=0):

        self.util = BktUtil()
        # self.leverage = leverage
        # self.margin_rate = margin_rate
        self.init_fund = init_fund
        # self.multiplier = contract_multiplier
        # self.tick = tick_size
        self.fee = fee_rate
        # self.slippage = nbr_slippage
        self.cash = init_fund
        self.total_margin_capital = 0.0
        self.total_transaction_cost = 0.0
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



    def open_long(self,dt,bktoption,trade_fund):# 多开
        bktoption.trade_dt_open = dt
        bktoption.trade_long_short = self.util.long
        id_instrument = bktoption.id_instrument
        mkt_price = bktoption.option_price
        multiplier = bktoption.multiplier
        trade_type = '多开'
        unit = bktoption.get_trade_unit(trade_fund)
        fee = unit*mkt_price*self.fee*multiplier
        premium = unit*mkt_price*multiplier
        margin_capital = 0.0
        bktoption.trade_unit = unit
        bktoption.premium = premium
        bktoption.trade_open_price = mkt_price
        bktoption.trade_margin_capital = margin_capital
        bktoption.transaction_fee = fee
        bktoption.trade_flag_open = True

        record = pd.DataFrame(data={self.util.id_instrument:[id_instrument],
                                    self.util.dt_trade:[dt],
                                    self.util.trading_type:[trade_type],
                                    self.util.trade_price:[mkt_price],
                                    self.util.trading_cost:[fee],
                                    self.util.unit:[unit]})
        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        # self.df_holdings = self.df_holdings.append(position,ignore_index=True)
        self.holdings.append(bktoption)
        self.cash = self.cash-premium-margin_capital
        self.nbr_trade += 1

    def open_short(self,dt,bktoption,trade_fund):
        bktoption.trade_dt_open = dt
        bktoption.trade_long_short = self.util.short
        id_instrument = bktoption.id_instrument
        mkt_price = bktoption.option_price
        multiplier = bktoption.multiplier
        trade_type = '空开'
        unit = bktoption.get_trade_unit(trade_fund)
        fee = unit*mkt_price*self.fee*multiplier
        premium = unit*mkt_price*multiplier
        margin_capital = unit*bktoption.get_init_margin()
        bktoption.trade_unit = unit
        bktoption.premium = premium
        bktoption.trade_open_price = mkt_price
        bktoption.trade_margin_capital = margin_capital
        bktoption.transaction_fee = fee
        bktoption.trade_flag_open = True


        record = pd.DataFrame(data={self.util.id_instrument:[id_instrument],
                                    self.util.dt_trade:[dt],
                                    self.util.trading_type:[trade_type],
                                    self.util.trade_price:[mkt_price],
                                    self.util.trading_cost:[fee],
                                    self.util.unit:[unit]})
        self.df_trading_records = self.df_trading_records.append(record,ignore_index=True)
        # self.df_holdings = self.df_holdings.append(position,ignore_index=True)
        self.holdings.append(bktoption)
        self.cash = self.cash+premium-margin_capital
        self.total_margin_capital += margin_capital
        self.total_transaction_cost += fee
        self.nbr_trade += 1



    def close_position(self,dt,bktoption): # 多空平仓
        if bktoption.trade_flag_open:
            id_instrument = bktoption.id_instrument
            mkt_price = bktoption.option_price
            unit = bktoption.trade_unit
            long_short = bktoption.trade_long_short
            margin_capital = bktoption.trade_margin_capital
            dt_open = bktoption.trade_dt_open
            multiplier = bktoption.multiplier
            premium = bktoption.premium
            open_price = bktoption.trade_open_price

            position = pd.Series()
            position[self.util.id_instrument] = id_instrument
            position[self.util.dt_open] = dt
            position[self.util.long_short] = long_short
            position[self.util.premium] = premium
            position[self.util.open_price] = open_price
            position[self.util.unit] = unit
            position[self.util.margin_capital] = margin_capital
            position[self.util.flag_open] = True
            position[self.util.multiplier] = multiplier
            if long_short == self.util.long:
                trade_type = '多平'
            else:
                trade_type = '空平'
            fee = unit * mkt_price * self.fee * multiplier
            pnl_amt = long_short*(unit*mkt_price*multiplier-bktoption.premium)-bktoption.transaction_fee-fee
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
            bktoption.liquidate()
            self.df_trading_records = self.df_trading_records.append(record, ignore_index=True)
            self.df_trading_book = self.df_trading_book.append(position, ignore_index=True)
            self.cash = self.cash+margin_capital+pnl_amt
            self.total_margin_capital -= margin_capital
            self.total_transaction_cost += fee
            self.nbr_trade += 1
            self.realized_pnl += pnl_amt
            # self.holdings.remove(bktoption)


    def rebalance_position(self,dt,bktoption,trade_fund):

        id_instrument = bktoption.id_instrument
        mkt_price = bktoption.option_price
        holding_unit = bktoption.trade_unit
        long_short = bktoption.trade_long_short
        margin_capital = bktoption.trade_margin_capital
        open_price = bktoption.trade_open_price
        multiplier = bktoption.multiplier
        premium = bktoption.premium
        unit = bktoption.get_trade_unit(trade_fund)
        if unit != holding_unit:
            if unit > holding_unit:# 加仓
                margin_add = (unit-holding_unit)*bktoption.get_init_margin()
                open_price = ((unit-holding_unit)*mkt_price+holding_unit*open_price)/unit #加权开仓价格
                premium =  (unit-holding_unit)*mkt_price*multiplier
                fee = premium*self.fee
                bktoption.transaction_fee += fee
                bktoption.trade_margin_capital += margin_add
                self.cash = self.cash-margin_add
                self.total_margin_capital += margin_add
                self.total_transaction_cost += fee

            else: # 减仓
                liquidated_unit = holding_unit - unit
                margin_returned = liquidated_unit*bktoption.trade_margin_capital/bktoption.trade_unit
                liquidated_premium = liquidated_unit*mkt_price*multiplier
                fee = liquidated_premium*self.fee
                d_fee = bktoption.transaction_fee*liquidated_unit/holding_unit
                realized_pnl = long_short*(liquidated_unit*multiplier*mkt_price
                                           -liquidated_premium)-fee-d_fee
                self.realized_pnl += realized_pnl
                self.cash = self.cash+margin_returned+realized_pnl
                self.total_margin_capital -= margin_returned
                self.total_transaction_cost += fee
                bktoption.transaction_fee -= d_fee
            bktoption.trade_unit = unit
            bktoption.premium += premium
            bktoption.trade_open_price = open_price
            bktoption.trade_margin_capital = margin_capital
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


    def switch_long(self):
        return None

    def switch_short(self):
        return None


    def mkm_update(self,dt,df_metric,col_option_price): # 每日更新
        unrealized_pnl = 0
        mtm_portfolio_value = 0
        mtm_long_positions = 0
        mtm_short_positions = 0
        # TODO: 资金使用率监控
        holdings = []
        for bktoption in self.holdings:
            if not bktoption.trade_flag_open: continue
            holdings.append(bktoption)
            mkt_price = bktoption.option_price
            unit = bktoption.trade_unit
            long_short = bktoption.trade_long_short
            margin_account = bktoption.trade_margin_capital
            multiplier = bktoption.multiplier
            premium = bktoption.premium
            maintain_margin = unit*bktoption.get_maintain_margin()
            margin_call = maintain_margin-margin_account
            unrealized_pnl += long_short*(mkt_price*unit*multiplier-premium)
            if long_short == self.util.long:
                mtm_long_positions += mkt_price*unit*multiplier
            else:
                mtm_short_positions -= mkt_price*unit*multiplier
            mtm_portfolio_value += mtm_long_positions + mtm_short_positions
            bktoption.trade_margin_capital = maintain_margin
            self.cash -= margin_call
            self.total_margin_capital += margin_call
        money_utilization = self.total_margin_capital/(self.total_margin_capital+self.cash)
        total_asset = self.cash+self.total_margin_capital+mtm_long_positions+mtm_short_positions
        self.npv = total_asset/self.init_fund
        self.holdings = holdings
        account = pd.DataFrame(data={self.util.dt_date:[dt],
                                     self.util.nbr_trade:[self.nbr_trade],
                                     self.util.margin_capital:[self.total_margin_capital],
                                     self.util.realized_pnl:[self.realized_pnl],
                                     self.util.unrealized_pnl: [unrealized_pnl],
                                     self.util.mtm_long_positions:[mtm_long_positions],
                                     self.util.mtm_short_positions:[mtm_short_positions],
                                     self.util.cash:[self.cash],
                                     self.util.money_utilization:[money_utilization],
                                     self.util.npv:[self.npv],
                                     self.util.total_asset:[total_asset]})
        self.df_account = self.df_account.append(account,ignore_index=True)
        self.nbr_trade = 0


    def liquidate_all(self,dt):
        holdings = self.holdings.copy()
        for bktoption in holdings:
            self.close_position(dt,bktoption)















































