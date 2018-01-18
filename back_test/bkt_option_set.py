import datetime
import pandas as pd
from back_test.bkt_option import BktOption
from back_test.bkt_util import BktUtil
import QuantLib as ql
import numpy as np


class OptionSet(object):


    def __init__(self, cd_frequency, df_option_metrics,n=2,col_date='dt_date',col_datetime='dt_datetime',
                 pricing_type='OptionPlainEuropean', engine_type='AnalyticEuropeanEngine'):
        self.util = BktUtil()
        self.frequency = cd_frequency
        self.df_metrics = df_option_metrics
        self.pricing_type = pricing_type
        self.engine_type = engine_type
        self.hp = n
        self.daycounter = ql.ActualActual()
        self.calendar = ql.China()
        self.bktoption_list = []
        self.bktoption_list_mdt0 = []
        self.bktoption_list_mdt1 = []
        self.bktoption_list_mdt2 = []
        self.bktoption_list_mdt3 = []
        self.eligible_maturities = []
        self.index = 0
        self.update_multiplier_adjustment()
        self.start()

        # if self.frequency in self.bktutil.cd_frequency_intraday:
        #     self.datetime_list = sorted(self.df_metrics[col_datetime].unique())
        #     self.eval_datetime = self.datetime_list[0]
        #     self.add_dtdate_column(col_date,col_datetime)


    def start(self):
        self.dt_list = sorted(self.df_metrics[self.util.col_date].unique())
        self.start_date = self.dt_list[0] #0
        self.end_date = self.dt_list[-1] # len(self.dt_list)-1
        self.eval_date = self.start_date
        self.update_current_daily_state()
        self.update_eligible_maturities()
        # if self.frequency in self.bktutil.cd_frequency_intraday:
        #     self.update_current_datetime_state()
        self.update_bktoption()


    def next(self):
        if self.frequency in self.util.cd_frequency_low:
            self.update_eval_date()
            self.update_current_daily_state()
            self.update_eligible_maturities()
        # else:
        #     self.update_eval_datetime()
        #     self.update_current_datetime_state()
        #     if self.eval_datetime.date() != self.eval_date:
        #         self.eval_date = self.eval_datetime.date()
        #         self.update_current_daily_state()
        #         self.update_eligible_maturities()
        self.update_bktoption()


    def update_bktoption(self):

        if self.frequency in self.util.cd_frequency_low:
            bkt_ids = []
            bktoption_list = []
            df_current = self.df_daily_state
            df_current = self.get_duplicate_strikes_dropped(df_current)
            option_ids = df_current[self.util.col_id_instrument].unique()
            for bktoption in self.bktoption_list:
                if bktoption.id_instrument in option_ids and bktoption.maturitydt in self.eligible_maturities:
                    # go to next state
                    bktoption.next()
                    bktoption_list.append(bktoption)
                    bkt_ids.append(bktoption.id_instrument)
            for optionid in option_ids:
                if optionid in bkt_ids: continue
                df_option = self.df_metrics[self.df_metrics[self.util.col_id_instrument] == optionid].reset_index()
                if df_option[self.util.col_maturitydt].values[0] not in self.eligible_maturities : continue
                bktoption = BktOption(self.frequency, df_option,id_instrument=optionid)
                bktoption_list.append(bktoption)
                bkt_ids.append(optionid)
            self.bktoption_list = bktoption_list
            # else:
            #     df_current = self.df_datetime_state

    def update_eval_date(self):
        self.index += 1
        self.eval_date = self.dt_list[min(self.dt_list.index(self.eval_date)+1
                            ,len(self.dt_list)-1)]


    # def update_eval_datetime(self):
    #     self.index += 1
    #     self.eval_datetime = self.datetime_list[min(self.datetime_list.index(self.eval_datetime)+1,
    #                                            len(self.datetime_list)-1)]


    def update_current_daily_state(self):
        self.df_daily_state = self.df_metrics[self.df_metrics[self.util.col_date]==self.eval_date].reset_index()


    # def update_current_datetime_state(self,col_datetime='dt_datetime'):
    #     self.df_datetime_state = self.df_metrics[self.df_metrics[col_datetime]==self.eval_datetime].reset_index()


    def update_eligible_maturities(self): # n: 要求合约剩余期限大于n（天）
        if self.hp < 2:
            print('要求合约剩余期限大于2日！')
            self.hp = 2
        maturity_dates = self.df_daily_state[self.util.col_maturitydt].unique()
        maturity_dates2 = []
        for mdt in maturity_dates:
            ttm = (mdt-self.eval_date).days
            if ttm > self.hp : maturity_dates2.append(mdt)
        self.eligible_maturities = maturity_dates2


    def get_volsurface_squre(self,option_type):
        ql_maturities = []
        option_list = []
        for option in self.bktoption_list:
            mdt = option.maturitydt
            ttm = (mdt-self.eval_date).days
            cd_type = option.option_type
            if cd_type == option_type and ttm > self.hp:
                option_list.append(option)
        df = self.get_duplicate_strikes_dropped(self.collect_implied_vol(option_list))
        df_mdt_list = []
        iv_name_list = []
        maturity_list = []
        for idx,mdt in enumerate(self.eligible_maturities):
            iv_rename = 'implied_vol_'+str(idx)
            df_mkt = df[(df[self.util.col_maturitydt]==mdt)&(df[self.util.col_option_type]==option_type)] \
            .rename(columns={self.util.col_implied_vol: iv_rename}).set_index(self.util.col_adj_strike)
            if len(df_mkt) == 0: continue
            df_mdt_list.append(df_mkt)
            iv_name_list.append(iv_rename)
            maturity_list.append(mdt)
        df_vol = pd.concat(df_mdt_list, axis=1, join='inner')
        strikes = []
        for k in df_vol.index:
            strikes.append(float(k))
        volset = []
        for name in iv_name_list:
            volset.append(df_vol[name].tolist())
        for mdate in maturity_list:
            ql_maturities.append(ql.Date(mdate.day, mdate.month, mdate.year))
        vol_matrix = ql.Matrix(len(strikes), len(maturity_list))
        for i in range(vol_matrix.rows()):
            for j in range(vol_matrix.columns()):
                vol_matrix[i][j] = volset[j][i]
        ql_evalDate = self.to_ql_date(self.eval_date)
        black_var_surface = ql.BlackVarianceSurface(
            ql_evalDate, self.calendar, ql_maturities, strikes, vol_matrix, self.daycounter)
        return black_var_surface


    def get_duplicate_strikes_dropped(self,df_metrics):
        maturities = sorted(df_metrics[self.util.col_maturitydt].unique())
        df = pd.DataFrame()
        for mdt in maturities:
            df_mdt_call = df_metrics[(df_metrics[self.util.col_maturitydt]==mdt) &
                                     (df_metrics[self.util.col_option_type]=='call')]\
                            .sort_values(by=self.util.col_trading_volume, ascending=False) \
                            .drop_duplicates(subset=[self.util.col_adj_strike])
            df_mdt_put = df_metrics[(df_metrics[self.util.col_maturitydt] == mdt) &
                                    (df_metrics[self.util.col_option_type] == 'put')]\
                            .sort_values(by=self.util.col_trading_volume, ascending=False) \
                            .drop_duplicates(subset=[self.util.col_adj_strike])
            df = df.append(df_mdt_call,ignore_index=True)
            df = df.append(df_mdt_put,ignore_index=True)
        return df

    def update_multiplier_adjustment(self):
        # TODO: no need for interation
        for (idx,row) in self.df_metrics.iterrows():
            self.df_metrics.loc[idx,self.util.col_adj_strike] = \
                round(row[self.util.col_strike]*row[self.util.col_multiplier]/10000,2)
            # self.df_metrics.loc[idx,'adj_underlying_price'] = round(row[col_underlying_price]*row[col_multiplier]/10000,2)
            self.df_metrics.loc[idx,self.util.col_adj_option_price] = \
                round(row[self.util.col_close_price]*row[self.util.col_multiplier]/10000,2)


    def add_dtdate_column(self):
        if self.util.col_date not in self.df_metrics.columns.tolist():
            for (idx,row) in self.df_metrics.iterrows():
                self.df_metrics.loc[idx, self.util.col_date] = row[self.util.col_datetime].date()

    def collect_implied_vol(self,bktoption_list):
        df = pd.DataFrame()
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.util.cd_frequency_low:
                df.loc[idx, self.util.col_date] = self.eval_date
            # else:
            #     df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, self.util.col_id_instrument] = option.id_instrument
            df.loc[idx, self.util.col_adj_strike] = option.adj_strike
            df.loc[idx, self.util.col_option_type] = option.option_type
            df.loc[idx, self.util.col_maturitydt] = option.maturitydt
            iv = option.get_implied_vol()
            df.loc[idx, self.util.col_implied_vol] = iv
            df.loc[idx, self.util.col_trading_volume] = option.get_trading_volume()
        return df

    def collect_delta(self,bktoption_list):
        df = pd.DataFrame()
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.util.cd_frequency_low:
                df.loc[idx, self.util.col_date] = self.eval_date
            # else:
            #     df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, self.util.col_id_instrument] = option.id_instrument
            df.loc[idx, self.util.col_adj_strike] = option.adj_strike
            df.loc[idx, self.util.col_option_type] = option.option_type
            df.loc[idx, self.util.col_maturitydt] = option.maturitydt
            df.loc[idx, self.util.col_implied_vol] = option.get_implied_vol()
            df.loc[idx, self.util.col_delta] = option.get_delta()
        return df

    def collect_theta(self,bktoption_list):
        df = pd.DataFrame()
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.util.cd_frequency_low:
                df.loc[idx, self.util.col_date] = self.eval_date
            # else:
            #     df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, self.util.col_id_instrument] = option.id_instrument
            df.loc[idx, self.util.col_adj_strike] = option.adj_strike
            df.loc[idx, self.util.col_option_type] = option.option_type
            df.loc[idx, self.util.col_maturitydt] = option.maturitydt
            df.loc[idx, self.util.col_implied_vol] = option.get_implied_vol()

            df.loc[idx, self.util.col_theta] = option.get_theta()
        return df

    def collect_vega(self,bktoption_list):
        df = pd.DataFrame()
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.util.cd_frequency_low:
                df.loc[idx, self.util.col_date] = self.eval_date
            # else:
            #     df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, self.util.col_id_instrument] = option.id_instrument
            df.loc[idx, self.util.col_adj_strike] = option.adj_strike
            df.loc[idx, self.util.col_option_type] = option.option_type
            df.loc[idx, self.util.col_maturitydt] = option.maturitydt
            df.loc[idx, self.util.col_implied_vol] = option.get_implied_vol()
            df.loc[idx, self.util.col_vega] = option.get_vega()
        return df


    def collect_carry(self,bktoption_list):
        df = pd.DataFrame()
        bvs_call = self.get_volsurface_squre('call')
        bvs_put = self.get_volsurface_squre('put')
        res = []
        for idx,option in enumerate(bktoption_list):
            iv = option.get_implied_vol()
            carry, theta, vega, iv_roll_down = option.get_carry(bvs_call, bvs_put, self.hp)
            if np.isnan(carry): carry = -999.0
            if np.isnan(theta): theta = -999.0
            if np.isnan(vega): vega = -999.0
            if np.isnan(iv_roll_down): iv_roll_down = -999.0
            if self.frequency in self.util.cd_frequency_low:
                df.loc[idx, self.util.col_date] = self.eval_date
            # else:
            #     df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, self.util.col_id_instrument] = option.id_instrument
            df.loc[idx, self.util.col_code_instrument] = option.code_instrument
            df.loc[idx, self.util.col_adj_strike] = option.adj_strike
            df.loc[idx, self.util.col_option_type] = option.option_type
            df.loc[idx, self.util.col_maturitydt] = option.maturitydt
            df.loc[idx, self.util.col_implied_vol] = iv
            df.loc[idx, self.util.col_option_price] = option.option_price
            df.loc[idx, self.util.col_carry] = carry
            db_row = {
                self.util.col_date:self.eval_date,
                self.util.col_id_instrument:option.id_instrument,
                self.util.nbr_invest_days:self.hp,
                self.util.col_code_instrument:option.code_instrument,
                self.util.col_adj_strike:float(option.adj_strike),
                self.util.col_option_type:option.option_type,
                self.util.col_maturitydt:option.maturitydt,
                self.util.col_implied_vol:float(iv),
                self.util.col_option_price:float(option.option_price),
                self.util.col_carry:float(carry),
                self.util.col_theta:float(theta),
                self.util.col_vega:float(vega),
                self.util.col_iv_roll_down:float(iv_roll_down)
            }
            res.append(db_row)
        return df,res


    def to_ql_date(self,date):
        return ql.Date(date.day,date.month,date.year)


















































