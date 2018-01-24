import datetime
import QuantLib as ql

# class BktUtil():
#
#     def __init__(self):
#         self.long = 1
#         self.short = -1
#         self.call = 'call'
#         self.put = 'put'
#         self.cd_frequency_low = ['daily','weekly','monthly','yearly']
#         self.cd_frequency_intraday = ['1min','5min']
#
#         self.col_date = 'dt_date'
#         self.col_datetime = 'dt_datetime'
#         self.col_maturitydt = 'dt_maturity'
#
#         self.col_code_instrument = 'code_instrument'
#         self.col_id_instrument = 'id_instrument'
#         self.col_option_type = 'cd_option_type'
#
#         self.col_strike = 'amt_strike'
#         self.col_adj_strike = 'amt_adj_strike'
#         self.col_close = 'amt_close'
#         self.col_adj_option_price = 'amt_adj_option_price'
#         self.col_option_price = 'amt_option_price'
#         self.col_underlying_price = 'amt_underlying_price'
#         self.col_settlement = 'amt_settlement'
#         self.col_last_settlement = 'amt_last_settlement'
#         self.col_last_close = 'amt_last_close'
#         self.col_multiplier = 'nbr_multiplier'
#
#         self.col_holding_volume = 'amt_holding_volume'
#         self.col_trading_volume = 'amt_trading_volume'
#
#         self.col_implied_vol = 'pct_implied_vol'
#
#         self.col_delta = 'amt_delta'
#         self.col_theta = 'amt_theta'
#         self.col_vega = 'amt_vega'
#         self.col_rho = 'amt_rho'
#         self.col_carry = 'amt_carry'
#         self.col_iv_roll_down = 'amt_iv_roll_down'
#
#         self.nbr_invest_days='nbr_invest_days'
#         self.col_rf = 'risk_free_rate'
#
#




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

    def to_ql_date(self,date):
        return ql.Date(date.day,date.month,date.year)

    def to_dt_date(self,ql_date):
        return datetime.date(ql_date.year(),ql_date.month(),ql_date.dayOfMonth())


























