from OptionStrategyLib.OptionPricing.Options import OptionPlainEuropean

from OptionStrategyLib.OptionPricing.OptionMetrics import OptionMetrics
from OptionStrategyLib.OptionPricing.Evaluation import Evaluation
import datetime
import QuantLib as ql


class BktOption(object):

    def __init__(self,cd_frequency,df_option_metrics):
        self.frequency = cd_frequency
        self.df_metrics = df_option_metrics # Sorted ascending by date/datetime
        self.nbr_index = len(df_option_metrics)
        self.current_index = 0
        self.last_index = len(df_option_metrics)-1
        self.daycounter = ql.China()
        self.calendar = ql.ActualActual()


    def start(self):
        self.start_state = self.df_metrics.loc[0]
        self.current_index = 0
        self.update_current_state()
        self.update_current_datetime()
        dt = datetime.datetime(self.evalDate.year,self.evalDate.month,self.evalDate.day,9,30,00)
        while self.dt_datetime < dt:
            self.current_index += 1
            self.update_current_state()
            self.update_current_datetime()
        self.start_index = self.current_index



    def next(self):
        self.current_index = min(self.current_index+1,self.last_index)
        self.update_current_state()


    def reset(self):
        self.current_index = self.start_index
        self.update_current_state()


    def update_current_state(self):
        self.current_state = self.df_metrics.loc[self.current_index]
        self.update_current_date()
        if self.frequency in ['daily','weekly','monthly','yearly']:
            ql_evalDate = ql.Date(self.evalDate.day, self.evalDate.month, self.evalDate.year)
            evaluation = Evaluation(ql_evalDate, self.daycounter, self.calendar)
            self.evaluation = evaluation


    def set_option_basics(self,col_option_type='cd_option_type',col_strike='amt_strike',
                          col_maturitydt='dt_maturity'):
        self.update_option_type(col_option_type)
        self.update_strike(col_strike)
        self.update_maturitydt(col_maturitydt)
        self.update_current_state()


    def set_pricing_metrics(self,optionType):
        if optionType == 'OptionPlainEuropean':
            option = OptionPlainEuropean(self.strike,self.maturitydt,self.option_type)
        else:
            print('Unsupported Option Type !')
            option = None
        self.pricing_metrics = OptionMetrics(option)


    def update_current_datetime(self,col_datetime='dt_datetime'):
        try:
            dt_datetime = self.current_state[col_datetime]
        except Exception as e:
            print(e)
            dt_datetime = None
        self.dt_datetime = dt_datetime


    def update_current_date(self,column_date='dt_date',col_datetime='dt_datetime'):
        try:
            dt_date = self.current_state[column_date]
        except:
            dt = self.current_state[col_datetime]
            dt_date = datetime.date(dt.year,dt.month,dt.day)
        self.evalDate = dt_date


    def update_strike(self,col_strike='amt_strike'):
        try:
            strike = self.current_state[col_strike]
        except Exception as e:
            print(e)
            strike = None
        self.strike = strike


    def update_maturitydt(self,col_maturitydt='dt_maturity'):
        try:
            maturitydt = self.current_state[col_maturitydt]
        except Exception as e:
            print(e)
            maturitydt = None
        self.maturitydt = maturitydt


    def update_option_type(self,col_option_type='cd_option_type'):
        try:
            option_type = self.current_state[col_option_type]
        except Exception as e:
            print(e)
            option_type = None
        self.option_type = option_type


    def update_option_price(self,col_option_price='amt_close'):
        try:
            option_price = self.current_state[col_option_price]
        except Exception as e:
            print(e)
            option_price = None
        self.option_price = option_price


    def update_holding_volume(self,col_holding_volume='amt_holding_volume'):
        try:
            holding_volume = self.current_state[col_holding_volume]
        except Exception as e:
            print(e)
            holding_volume = None
        self.holding_volume = holding_volume


    def update_multiplier(self,col_multiplier='nbr_multiplier'):
        try:
            multiplier = self.current_state[col_multiplier]
        except Exception as e:
            print(e)
            multiplier = None
        self.multiplier = multiplier


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
            print(e)
            rf = None
        self.rf = rf


    def implied_vol(self,engineType):
        try:
            implied_vol = self.pricing_metrics.implied_vol(self.evaluation,self.rf,
                                    self.underlying_price, self.underlying_price,engineType)
        except Exception as e:
            print(e)
            implied_vol = None
        self.implied_vol = implied_vol
        return implied_vol


    def implied_vol_given(self,col_implied_vol='pct_implied_vol'):
        try:
            implied_vol = self.current_state[col_implied_vol]
        except Exception as e:
            print(e)
            implied_vol = None
        self.implied_vol_given = implied_vol
        return implied_vol


    def delta(self,engineType):
        try:
            delta = self.pricing_metrics.delta(self.evaluation, self.rf,self.underlying_price,
                                               self.underlying_price,engineType)
        except Exception as e:
            print(e)
            delta = None
        self.delta = delta
        return delta


    def theta(self,engineType):
        try:
            theta = self.pricing_metrics.theta(self.evaluation, self.rf,self.underlying_price,
                                               self.underlying_price,engineType)
        except Exception as e:
            print(e)
            theta = None
        self.theta = theta
        return theta


    def vega(self,engineType):
        try:
            vega = self.pricing_metrics.vega(self.evaluation, self.rf,self.underlying_price,
                                               self.underlying_price,engineType)
        except Exception as e:
            print(e)
            vega = None
        self.vega = vega
        return vega


    def iv_roll_down(self,black_var_surface,dt=1.0/365.0): # iv(tao-1)-iv(tao), tao:maturity
        mdt = self.maturitydt
        evalDate = self.evalDate
        ttm = (mdt-evalDate).days/365.0
        implied_vol_t1 = black_var_surface.blackVol(ttm-dt, self.strike)
        iv_roll_down = implied_vol_t1 - self.implied_vol
        return iv_roll_down


    def carry(self,black_var_surface,dt=1.0/365.0):
        iv_roll_down = self.iv_roll_down(black_var_surface,dt)
        option_carry = (-self.theta+self.vega*iv_roll_down)/self.option_price-self.rf
        return option_carry











































