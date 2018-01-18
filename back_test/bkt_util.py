import pandas as pd
import numpy as np
import hashlib
import datetime

class BktUtil():

    def __init__(self):
        self.long = 1
        self.short = -1
        self.call = 'call'
        self.put = 'put'
        self.cd_frequency_low = ['daily','weekly','monthly','yearly']
        self.cd_frequency_intraday = ['1min','5min']

        self.col_date = 'dt_date'
        self.col_datetime = 'dt_datetime'
        self.col_maturitydt = 'dt_maturity'

        self.col_code_instrument = 'code_instrument'
        self.col_id_instrument = 'id_instrument'
        self.col_option_type = 'cd_option_type'

        self.col_strike = 'amt_strike'
        self.col_adj_strike = 'amt_adj_strike'
        self.col_close_price = 'amt_close'
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
































