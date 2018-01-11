from OptionStrategyLib.OptionPricing.Options import OptionPlainEuropean

from OptionStrategyLib.OptionPricing.OptionMetrics import OptionMetrics
from OptionStrategyLib.OptionPricing.Evaluation import Evaluation
from back_test.bkt_util import BktUtil

import datetime
import QuantLib as ql


class BktOption(object):

    def __init__(self,cd_frequency,df_option_metrics,id_instrument='',
                 pricing_type = 'OptionPlainEuropean',engine_type = 'AnalyticEuropeanEngine'):
        self.bktutil = BktUtil()
        self.frequency = cd_frequency
        self.id_instrument = id_instrument
        self.df_metrics = df_option_metrics # Sorted ascending by date/datetime
        self.nbr_index = len(df_option_metrics)
        self.current_index = 0
        self.last_index = len(df_option_metrics)-1
        self.daycounter = ql.ActualActual()
        self.calendar = ql.China()
        self.pricing_type = pricing_type
        self.engine_type = engine_type
        self.implied_vol = None
        self.start()

    def start(self):
        self.start_state = self.df_metrics.loc[0]
        self.current_index = 0
        self.update_current_state()
        self.set_option_basics()
        self.set_pricing_metrics()
        if self.frequency in self.bktutil.cd_frequency_intraday:
            self.update_current_datetime()
            # Remove datetime data before 09:30
            dt = datetime.datetime(self.evalDate.year,self.evalDate.month,self.evalDate.day,9,30,00)
            while self.dt_datetime < dt:
                self.current_index += 1
                self.update_current_state()
                self.update_current_datetime()
            self.start_index = self.current_index



    def next(self):
        self.current_index = min(self.current_index+1,self.last_index)
        self.update_current_state()
        self.set_pricing_metrics()


    def reset(self):
        self.current_index = self.start_index
        self.update_current_state()
        self.set_pricing_metrics()



    def update_current_state(self):
        self.current_state = self.df_metrics.loc[self.current_index]
        self.update_current_date()
        if self.frequency in self.bktutil.cd_frequency_intraday:
            self.update_current_datetime()
        if self.frequency in ['daily','weekly','monthly','yearly']:
            ql_evalDate = ql.Date(self.evalDate.day, self.evalDate.month, self.evalDate.year)
            evaluation = Evaluation(ql_evalDate, self.daycounter, self.calendar)
            self.evaluation = evaluation


    def update_current_datetime(self,col_datetime='dt_datetime'):
        try:
            dt_datetime = self.current_state[col_datetime]
        except Exception:
            dt_datetime = None
        self.dt_datetime = dt_datetime


    def update_current_date(self,column_date='dt_date',col_datetime='dt_datetime'):
        try:
            dt_date = self.current_state[column_date]
        except:
            dt = self.current_state[col_datetime]
            dt_date = datetime.date(dt.year,dt.month,dt.day)
        self.evalDate = dt_date


    def set_option_basics(self,col_option_type='cd_option_type',col_strike='amt_strike',
                          col_maturitydt='dt_maturity',col_code = 'code_instrument'):
        self.update_option_type(col_option_type)
        self.update_strike(col_strike)
        self.update_maturitydt(col_maturitydt)
        self.update_code_instrument(col_code)
        # self.update_current_state()


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


    def update_strike(self,col_strike='amt_strike',col_adj_strike = 'adj_strike'):
        try:
            strike = self.current_state[col_strike]
        except Exception as e:
            print(e)
            strike = None
        try:
            adj_strike = self.current_state[col_adj_strike]
        except Exception as e:
            print(e)
            adj_strike = None
        self.strike = strike
        self.adj_strike = adj_strike


    def update_maturitydt(self,col_maturitydt='dt_maturity'):
        try:
            maturitydt = self.current_state[col_maturitydt]
        except Exception as e:
            print(e)
            print(self.current_state)
            maturitydt = None
        self.maturitydt = maturitydt


    def update_option_type(self,col_option_type='cd_option_type'):
        try:
            option_type = self.current_state[col_option_type]
        except Exception as e:
            print(e)
            option_type = None
        self.option_type = option_type

    def update_code_instrument(self,col_code = 'code_instrument'):
        try:
            code_instrument = self.current_state[col_code]
        except Exception as e:
            print(e)
            code_instrument = None
        self.code_instrument = code_instrument

    def update_option_price(self,col_option_price='amt_close',col_adj_option_price = 'adj_option_price'):
        try:
            option_price = self.current_state[col_option_price]
        except Exception as e:
            print(e)
            option_price = None
        try:
            adj_option_price = self.current_state[col_adj_option_price]
        except Exception as e:
            print(e)
            adj_option_price = None
        self.option_price = option_price
        self.adj_option_price = adj_option_price


    def update_underlying_price(self,col_underlying_price='underlying_price'):
        try:
            underlying_price = self.current_state[col_underlying_price]
        except Exception as e:
            print(e)
            underlying_price = None
        self.underlying_price = underlying_price
        return  underlying_price


    def update_rf(self,col_rf='risk_free_rate'):
        try:
            rf = self.current_state[col_rf]
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


    def get_holding_volume(self,col_holding_volume='amt_holding_volume'):
        try:
            holding_volume = self.current_state[col_holding_volume]
        except Exception as e:
            print(e)
            holding_volume = None
        return holding_volume

    def get_trading_volume(self,col_trading_volume='amt_trading_volume'):
        try:
            trading_volume = self.current_state[col_trading_volume]
        except Exception as e:
            print(e)
            trading_volume = None
        return trading_volume

    def get_multiplier(self,col_multiplier='nbr_multiplier'):
        try:
            multiplier = self.current_state[col_multiplier]
        except Exception as e:
            print(e)
            multiplier = None
        return multiplier

    def get_implied_vol_given(self,col_implied_vol_given='pct_implied_vol'):
        try:
            implied_vol = self.current_state[col_implied_vol_given]
        except Exception as e:
            print(e)
            implied_vol = None
        return implied_vol

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
        evalDate = self.evalDate
        ttm = (mdt-evalDate).days/365.0
        k = self.strike
        max_strike = max(black_var_surface.maxStrike(),black_var_surface.minStrike())
        # min_strike = min(black_var_surface.maxStrike(),black_var_surface.minStrike())
        # if k >= max_strike : k = max_strike-0.01
        # if k <= min_strike : k = min_strike+0.01
        # print(min_strike,max_strike,k)
        # print(min_strike,max_strike,k)
        black_var_surface.enableExtrapolation()
        implied_vol_t1 = black_var_surface.blackVol(ttm-dt, k)
        iv_roll_down = implied_vol_t1 - self.implied_vol
        return iv_roll_down


    def get_carry(self,bvs_call,bvs_put,dt=1.0/365.0):
        # if self.implied_vol == None : self.update_implied_vol()

        if self.option_type == 'call':
            iv_roll_down = self.get_iv_roll_down(bvs_call,dt)
        else:
            iv_roll_down = self.get_iv_roll_down(bvs_put,dt)
        vega = self.get_vega()
        theta = self.get_theta()
        # print(vega)
        # print(theta)
        option_carry = (vega*iv_roll_down-theta)/self.option_price-self.rf
        # print(option_carry)
        return option_carry











































