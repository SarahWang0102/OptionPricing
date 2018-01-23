import pandas as pd
import numpy as np
import hashlib
import datetime
from back_test.bkt_option_set import OptionSet
from WindPy import w

class BktUtil():

    def __init__(self):

        self.long = 1
        self.short = -1
        self.type_call = 'call'
        self.type_put = 'put'
        self.type_all = 'all'
        self.cd_frequency_low = ['daily','weekly','monthly','yearly']
        self.cd_frequency_intraday = ['1min','5min']

        """database column names"""

        self.col_date = 'dt_date'
        self.col_datetime = 'dt_datetime'
        self.col_maturitydt = 'dt_maturity'

        self.col_code_instrument = 'code_instrument'
        self.col_id_instrument = 'id_instrument'
        self.col_option_type = 'cd_option_type'

        self.col_strike = 'amt_strike'
        self.col_adj_strike = 'amt_adj_strike'
        self.col_close = 'amt_close'
        self.col_adj_option_price = 'amt_adj_option_price'
        self.col_option_price = 'amt_option_price'
        self.col_underlying_price = 'amt_underlying_price'
        self.col_settlement = 'amt_settlement'
        self.col_last_settlement = 'amt_last_settlement'
        self.col_last_close = 'amt_last_close'
        self.col_multiplier = 'nbr_multiplier'

        self.col_holding_volume = 'amt_holding_volume'
        self.col_trading_volume = 'amt_trading_volume'

        self.col_implied_vol = 'pct_implied_vol'

        self.col_delta = 'amt_delta'
        self.col_theta = 'amt_theta'
        self.col_vega = 'amt_vega'
        self.col_rho = 'amt_rho'
        self.col_carry = 'amt_carry'
        self.col_iv_roll_down = 'amt_iv_roll_down'

        self.nbr_invest_days='nbr_invest_days'
        self.col_rf = 'risk_free_rate'


        """output dataframe column names"""

        self.id_position='id_position'
        self.id_instrument='id_instrument'
        self.multiplier='multiplier'
        self.mkt_price = 'mkt_price'
        self.dt_open='dt_open'
        self.long_short='long_short'
        self.open_price='open_price'
        self.premium='premium'
        # self.open_trading_cost='open_trading_cost'
        self.unit='unit'
        self.npv='npv'
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
        # self.mkm_portfolio_value='mkm_portfolio_value'
        self.mtm_short_positions = 'mtm_short_positions'
        self.mtm_long_positions = 'mtm_long_positions'

        self.cash='cash'
        self.money_utilization='money_utilization'
        self.total_asset = 'total_asset'
        self.npv = 'npv'

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
                           self.premium,
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
                                self.mtm_long_positions,
                                self.mtm_short_positions,
                                self.cash,
                                self.money_utilization,
                                self.total_asset,
                                self.npv
                                ]

        self.record_columns = [self.dt_trade,
                               self.id_instrument,
                               self.trading_type,
                               self.trade_price,
                               self.trading_cost,
                               self.unit]



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



class FactorStrategyBkt(object):

    def __init__(self,df_option_metrics,hp,money_utilization=0.2,init_fund=1000000.0,tick_size=0.0001,fee_rate=2.0/10000,
                 nbr_slippage=0,max_money_utilization=0.5,buy_ratio=0.5,sell_ratio=0.5,nbr_top_bottom=5
                 ):
        self.util = BktUtil()
        self.init_fund = init_fund
        self.money_utl = money_utilization
        self.holding_period = hp
        self.df_option_metrics = df_option_metrics
        self.buy_ratio = buy_ratio
        self.sell_ratio = sell_ratio
        self.nbr_top_bottom = nbr_top_bottom
        self.option_type = None
        self.min_ttm = None
        self.max_ttm = None
        self.bkt_account = BktAccount(fee_rate=fee_rate,init_fund=init_fund)
        self.bkt_optionset = OptionSet('daily', df_option_metrics, hp)

    def set_min_ttm(self,min_ttm):
        self.min_ttm = min_ttm

    def set_max_ttm(self,max_ttm):
        self.max_ttm = max_ttm

    def set_option_type(self,option_type):
        self.option_type = option_type


    def get_candidate_set(self,eval_date):
        if self.option_type == None:
            option_list = self.bkt_optionset.bktoption_list
        else:
            if self.option_type == self.util.type_call:
                option_list = self.bkt_optionset.bktoption_list_call
            else:
                option_list = self.bkt_optionset.bktoption_list_put

        if self.min_ttm != None and self.max_ttm != None:
            list = []
            d1 = w.tdaysoffset(self.min_ttm, eval_date).Data[0][0].date()
            d2 = w.tdaysoffset(self.max_ttm, eval_date).Data[0][0].date()
            for option in option_list:
                if option.maturitydt >= d1 and option.maturitydt <= d2:
                    list.append(option)
            option_list = list
        return option_list


    def get_carry_tnb(self,option_list,n):
        df_ranked = self.bkt_optionset.rank_by_carry(option_list)
        df_ranked = df_ranked[df_ranked[self.util.col_carry] != -999.0]
        df_buy = df_ranked.loc[0:n-1]
        df_sell = df_ranked.loc[len(df_ranked)-n:]
        return df_buy,df_sell

    def run(self):
        bkt_optionset = self.bkt_optionset
        bkt = self.bkt_account

        while bkt_optionset.index < len(bkt_optionset.dt_list):
            if bkt_optionset.index == 0:
                bkt_optionset.next()
                continue

            evalDate = bkt_optionset.eval_date
            hp_enddate = w.tdaysoffset(self.holding_period, evalDate).Data[0][0].date()

            df_metrics_today = self.df_option_metrics[(self.df_option_metrics[self.util.col_date]==evalDate)]

            # 到期全部清仓
            if evalDate == bkt_optionset.end_date:
                print(' Liquidate all possitions !!! ')
                bkt.liquidate_all(evalDate)
                break

            for bktoption in bkt.holdings:
                if bktoption.maturitydt <= evalDate:
                    print('Liquidate position at maturity : ', evalDate, ' , ', bktoption.maturitydt)
                    bkt.close_position(evalDate, bktoption)

            """持有期到期"""
            if (bkt_optionset.index-1)%self.holding_period == 0:
                print('调仓 : ', evalDate)
                option_list = self.get_candidate_set(evalDate)
                df_buy, df_sell = self.get_carry_tnb(option_list, self.nbr_top_bottom)
                # 平仓
                for bktoption in bkt.holdings:
                    if bktoption.maturitydt <= hp_enddate:
                        bkt.close_position(evalDate, bktoption)
                    else:
                        if bktoption.trade_long_short == 1 and bktoption in df_buy['bktoption']: continue
                        if bktoption.trade_long_short == -1 and bktoption in df_sell['bktoption']: continue
                        bkt.close_position(evalDate, bktoption)

                # 开仓
                fund_buy = bkt.cash * self.money_utl * self.buy_ratio
                fund_sell = bkt.cash * self.money_utl * self.sell_ratio
                # if hp_enddate < bkt_optionset.end_date:
                n1 = len(df_buy)
                n2 = len(df_sell)
                for (idx, row) in df_buy.iterrows():
                    bktoption = row['bktoption']
                    if bktoption in bkt.holdings and bktoption.trade_flag_open:
                        bkt.rebalance_position(evalDate, bktoption, fund_buy/n1)
                    else:
                        bkt.open_long(evalDate, bktoption, fund_buy/n1)

                for (idx, row) in df_sell.iterrows():
                    bktoption = row['bktoption']
                    if bktoption in bkt.holdings and bktoption.trade_flag_open:
                        bkt.rebalance_position(evalDate, bktoption, fund_sell/n2)
                    else:
                        bkt.open_short(evalDate, bktoption, fund_sell/n2)

            bkt.mkm_update(evalDate, df_metrics_today, self.util.col_close)
            print(evalDate,' , ' ,bkt.npv)
            bkt_optionset.next()

















































