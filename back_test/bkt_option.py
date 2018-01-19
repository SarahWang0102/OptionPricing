from OptionStrategyLib.OptionPricing.Options import OptionPlainEuropean

from OptionStrategyLib.OptionPricing.OptionMetrics import OptionMetrics
from OptionStrategyLib.OptionPricing.Evaluation import Evaluation
from back_test.bkt_util import BktUtil

import datetime
import QuantLib as ql
import numpy as np


class BktOption(object):

    def __init__(self,cd_frequency,df_daily_metrics,df_intraday_metrics=None,id_instrument='',
                 pricing_type = 'OptionPlainEuropean',engine_type = 'AnalyticEuropeanEngine'):
        self.util = BktUtil()
        self.frequency = cd_frequency
        self.id_instrument = id_instrument
        self.df_daily_metrics = df_daily_metrics # Sorted ascending by date/datetime
        if self.frequency in self.util.cd_frequency_low:
            self.df_metrics = df_daily_metrics
        else:
            self.df_metrics = df_intraday_metrics
        self.start_index = 0
        self.nbr_index = len(df_daily_metrics)
        self.last_index = len(df_daily_metrics)-1
        self.dt_list = sorted(self.df_metrics[self.util.col_date].unique())
        self.pricing_type = pricing_type
        self.engine_type = engine_type
        self.implied_vol = None
        self.trade_unit = 0
        self.daycounter = ql.ActualActual()
        self.calendar = ql.China()
        self.start()

    def start(self):
        self.current_index = self.start_index
        self.update_current_state()
        self.set_option_basics()
        self.set_pricing_metrics()


    def next(self):
        self.current_index = min(self.current_index+1,self.last_index)
        self.update_current_state()
        self.set_pricing_metrics()


    # def reset(self):
    #     self.current_index = self.start_index
    #     self.update_current_state()
    #     self.set_pricing_metrics()


    def update_current_state(self):
        self.current_state = self.df_metrics.loc[self.current_index]

        if self.frequency in self.util.cd_frequency_low:
            self.current_daily_state = self.current_state
            self.dt_date = self.current_state[self.util.col_date]
            self.update_evaluation()
        else:
            self.update_current_datetime()
            # Remove datetime data before 09:30
            dt = datetime.datetime(self.dt_datetime.year, self.dt_datetime.month, self.dt_datetime.day, 9, 30, 00)
            while self.dt_datetime < dt:
                self.current_index += 1
                self.update_current_state()
                self.update_current_datetime()
            # set evaluation date
            dt_today = self.dt_datetime.date()
            if dt_today != self.dt_date:
                self.dt_date = dt_today
                idx_today = self.dt_list.index(dt_today)
                self.current_daily_state = self.df_daily_metrics.loc[idx_today]
                self.update_evaluation()


    def update_evaluation(self):
        ql_evalDate = ql.Date(self.dt_date.day, self.dt_date.month, self.dt_date.year)
        evaluation = Evaluation(ql_evalDate, self.daycounter, self.calendar)
        self.evaluation = evaluation


    def update_current_datetime(self):
        try:
            dt_datetime = self.current_state[self.util.col_datetime]
        except Exception:
            dt_datetime = None
        self.dt_datetime = dt_datetime


    # def update_current_date(self):
    #     try:
    #         dt_date = self.current_state[self.util.col_date]
    #     except:
    #         dt = self.current_state[self.util.col_datetime]
    #         dt_date = datetime.date(dt.year,dt.month,dt.day)
    #     self.dt_date = dt_date


    def set_option_basics(self):
        self.update_option_type()
        self.update_strike()
        self.update_maturitydt()
        self.update_code_instrument()
        self.update_multiplier()


    def set_pricing_metrics(self):
        self.update_rf()
        self.update_option_price()
        self.update_underlying_price()
        if self.pricing_type == 'OptionPlainEuropean':
            ql_maturitydt = ql.Date(self.maturitydt.day,
                                    self.maturitydt.month,
                                    self.maturitydt.year)
            if self.option_type == 'call':
                ql_optiontype = ql.Option.Call
            elif self.option_type == 'put':
                ql_optiontype = ql.Option.Put
            else:
                print('No option type!')
                return
            option = OptionPlainEuropean(self.strike,ql_maturitydt,ql_optiontype)
        else:
            print('Unsupported Option Type !')
            option = None
        self.pricing_metrics = OptionMetrics(option)


    def update_strike(self):
        try:
            strike = self.current_daily_state[self.util.col_strike]
        except Exception as e:
            print(e)
            strike = None
        try:
            adj_strike = self.current_daily_state[self.util.col_adj_strike]
        except Exception as e:
            print(e)
            adj_strike = None
        self.strike = strike
        self.adj_strike = adj_strike


    def update_maturitydt(self):
        try:
            maturitydt = self.current_daily_state[self.util.col_maturitydt]
        except Exception as e:
            print(e)
            print(self.current_daily_state)
            maturitydt = None
        self.maturitydt = maturitydt


    def update_option_type(self):
        try:
            option_type = self.current_daily_state[self.util.col_option_type]
        except Exception as e:
            print(e)
            option_type = None
        self.option_type = option_type

    def update_code_instrument(self):
        try:
            code_instrument = self.current_daily_state[self.util.col_code_instrument]
        except Exception as e:
            print(e)
            code_instrument = None
        self.code_instrument = code_instrument

    def update_option_price(self):
        try:
            option_price = self.current_state[self.util.col_close]
        except Exception as e:
            print(e)
            option_price = None
        try:
            adj_option_price = self.current_state[self.util.col_adj_option_price]
        except Exception as e:
            print(e)
            adj_option_price = None
        self.option_price = option_price
        self.adj_option_price = adj_option_price




    def update_underlying_price(self):
        try:
            underlying_price = self.current_state[self.util.col_underlying_price]
        except Exception as e:
            print(e)
            underlying_price = None
        self.underlying_price = underlying_price


    def update_rf(self):
        try:
            rf = self.current_daily_state[self.util.col_rf]
        except Exception as e:
            rf = 0.03
        self.rf = rf

    def update_implied_vol(self):
        try:
            self.update_rf()
            self.update_underlying_price()
            self.update_option_price()
            implied_vol = self.pricing_metrics.implied_vol(self.evaluation,self.rf,
                                    self.underlying_price, self.option_price,self.engine_type)
        except Exception as e:
            print(e)
            implied_vol = None
        self.implied_vol = implied_vol

    def update_multiplier(self):
        try:
            multiplier = self.current_daily_state[self.util.col_multiplier]
        except Exception as e:
            print(e)
            multiplier = None
        self.multiplier = multiplier


    def get_holding_volume(self):
        try:
            holding_volume = self.current_daily_state[self.util.col_holding_volume]
        except Exception as e:
            print(e)
            holding_volume = None
        return holding_volume

    def get_trading_volume(self):
        try:
            trading_volume = self.current_daily_state[self.util.col_trading_volume]
        except Exception as e:
            print(e)
            trading_volume = None
        return trading_volume


    def get_implied_vol_given(self):
        try:
            implied_vol = self.current_daily_state[self.util.col_implied_vol]
        except Exception as e:
            print(e)
            implied_vol = None
        return implied_vol

    def get_close(self):
        try:
            option_price = self.current_daily_state[self.util.col_close]
        except Exception as e:
            print(e)
            option_price = None
        return option_price

    def get_underlying_close(self):
        try:
            p = self.current_daily_state[self.util.col_underlying_price]
        except Exception as e:
            print(e)
            p = None
        return p

    def get_settlement(self):
        try:
            amt_settle = self.current_daily_state[self.util.col_settlement]
        except Exception as e:
            print(e)
            amt_settle = None
        return amt_settle

    def get_last_settlement(self):
        try:
            amt_pre_settle = self.current_daily_state[self.util.col_last_settlement]
        except Exception as e:
            print(e)
            amt_pre_settle = None
        if amt_pre_settle == None:
            idx_date = self.dt_list.index(self.dt_date)
            if idx_date == 0: return amt_pre_settle
            dt_last = self.dt_list[self.dt_list.index(self.dt_date) - 1]
            df_last_state = self.df_daily_metrics.loc[dt_last]
            amt_pre_settle = df_last_state[self.util.col_last_settlement]
        return amt_pre_settle

    def get_last_close(self):
        try:
            amt_pre_close = self.current_daily_state[self.util.col_last_close]
        except Exception as e:
            print(e)
            amt_pre_close = None
        if amt_pre_close == None:
            idx_date = self.dt_list.index(self.dt_date)
            if idx_date == 0: return amt_pre_close
            dt_last = self.dt_list[self.dt_list.index(self.dt_date) - 1]
            df_last_state = self.df_daily_metrics.loc[dt_last]
            amt_pre_close = df_last_state[self.util.col_last_close]
        return amt_pre_close

    def get_underlying_last_close(self):
        idx_date = self.dt_list.index(self.dt_date)
        if idx_date == 0: return
        # dt_last = self.dt_list[self.dt_list.index(self.dt_date) - 1]
        df_last_state = self.df_daily_metrics.loc[idx_date-1]
        amt_pre_close = df_last_state[self.util.col_close]
        return amt_pre_close

    def get_implied_vol(self):
        if self.implied_vol == None : self.update_implied_vol()
        return self.implied_vol

    def get_delta(self):
        try:
            if self.implied_vol == None: self.update_implied_vol()
            delta = self.pricing_metrics.delta(self.evaluation, self.rf,self.underlying_price,
                                               self.underlying_price,self.engine_type,self.implied_vol)
        except Exception as e:
            print(e)
            delta = None
        return delta


    def get_theta(self):
        try:
            if self.implied_vol == None: self.update_implied_vol()
            theta = self.pricing_metrics.theta(self.evaluation, self.rf,self.underlying_price,
                                               self.underlying_price,self.engine_type,self.implied_vol)
        except Exception as e:
            print(e)
            theta = None
        return theta


    def get_vega(self):
        if self.implied_vol == None : self.update_implied_vol()
        try:
            vega = self.pricing_metrics.vega(self.evaluation, self.rf,self.underlying_price,
                                               self.underlying_price,self.engine_type,self.implied_vol)
        except Exception as e:
            print(e)
            vega = None
        return vega


    def get_iv_roll_down(self,black_var_surface,dt): # iv(tao-1)-iv(tao), tao:maturity
        if self.implied_vol == None : self.update_implied_vol()
        mdt = self.maturitydt
        evalDate = self.dt_date
        ttm = (mdt-evalDate).days/365.0
        black_var_surface.enableExtrapolation()
        implied_vol_t1 = black_var_surface.blackVol(ttm-dt, self.strike)
        iv_roll_down = implied_vol_t1 - self.implied_vol
        return iv_roll_down


    def get_carry(self,bvs_call,bvs_put,n=1):
        dt = n/365.0
        if self.option_type == 'call':
            iv_roll_down = self.get_iv_roll_down(bvs_call,dt)
        else:
            iv_roll_down = self.get_iv_roll_down(bvs_put,dt)
        if np.isnan(iv_roll_down): iv_roll_down =0.0
        vega = self.get_vega()
        theta = self.get_theta()
        option_carry = (vega*iv_roll_down-theta)/self.option_price-self.rf
        return option_carry,theta,vega,iv_roll_down


    def get_init_margin(self):

        # 认购期权义务仓开仓保证金＝[合约前结算价+Max（12%×合约标的前收盘价-认购期权虚值，
        #                           7%×合约标的前收盘价)]×合约单位
        # 认沽期权义务仓开仓保证金＝Min[合约前结算价 + Max（12 %×合约标的前收盘价 - 认沽期权虚值，
        #                               7 %×行权价格），行权价格] ×合约单位
        amt_last_settle = self.get_last_settlement()
        amt_underlying_last_close = self.get_underlying_last_close()
        if self.option_type =='call':
            otm = max(0,self.strike-self.underlying_price)
            init_margin = (amt_last_settle+max(0.12*amt_underlying_last_close-otm,
                                              0.07*amt_underlying_last_close))*self.multiplier
        else:
            otm = max(0,self.underlying_price-self.strike)
            init_margin = min(amt_last_settle+max(0.12*amt_underlying_last_close-otm,
                                                  0.07*self.strike),self.strike)*self.multiplier
        return init_margin

    def get_maintain_margin(self):
        # 认购期权义务仓维持保证金＝[合约结算价 + Max（12 %×合约标的收盘价 - 认购期权虚值，
        #                                           7 %×合约标的收盘价）]×合约单位
        # 认沽期权义务仓维持保证金＝Min[合约结算价 + Max（12 %×合标的收盘价 - 认沽期权虚值，7 %×行权价格），行权价格]×合约单位
        amt_settle = self.get_settlement()
        amt_underlying_close = self.get_underlying_close()
        if self.option_type =='call':
            otm = max(0,self.strike-self.underlying_price)
            maintain_margin = (amt_settle+max(0.12*amt_underlying_close-otm,
                                              0.07*amt_underlying_close))*self.multiplier

        else:
            otm = max(0,self.underlying_price-self.strike)
            maintain_margin = min(amt_settle+max(0.12*amt_underlying_close-otm,
                                                 0.07*self.strike),self.strike)*self.multiplier
        return maintain_margin

    def price_limit(self):
        # 认购期权最大涨幅＝max｛合约标的前收盘价×0.5 %，min[（2×合约标的前收盘价－行权价格），合约标的前收盘价]×10％｝
        # 认购期权最大跌幅＝合约标的前收盘价×10％
        # 认沽期权最大涨幅＝max｛行权价格×0.5 %，min[（2×行权价格－合约标的前收盘价），合约标的前收盘价]×10％｝
        # 认沽期权最大跌幅＝合约标的前收盘价×10％
        return None

    def get_trade_unit(self,fund):
        return np.floor(fund/(self.option_price * self.multiplier))

    def liquidate(self):
        self.trade_flag_open = False
        self.trade_unit = None
        self.trade_dt_open = None
        self.trade_long_short = None
        self.trade_cost = None
        self.trade_open_price = None
        self.trade_margin_calital = None

































