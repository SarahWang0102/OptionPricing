import pandas as pd
import numpy as np
import hashlib
import datetime

class BktUtil():

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

        self.cd_frequency_low = ['daily','weekly','monthly','yearly']

        self.cd_frequency_intraday = ['1min','5min']






























