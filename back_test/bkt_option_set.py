import datetime
import pandas as pd
from back_test.bkt_option import BktOption
from back_test.bkt_util import BktUtil
import QuantLib as ql


class OptionSet(object):


    def __init__(self, cd_frequency, df_option_metrics,col_date='dt_date',col_datetime='dt_datetime',
                 pricing_type='OptionPlainEuropean', engine_type='AnalyticEuropeanEngine'):
        self.bktutil = BktUtil()
        self.frequency = cd_frequency
        self.df_metrics = df_option_metrics
        self.pricing_type = pricing_type
        self.engine_type = engine_type
        self.daycounter = ql.ActualActual()
        self.calendar = ql.China()
        self.bktoption_list = []
        self.bktoption_list_mdt0 = []
        self.bktoption_list_mdt1 = []
        self.bktoption_list_mdt2 = []
        self.bktoption_list_mdt3 = []
        self.eligible_maturities = []
        self.index = 0
        if self.frequency in self.bktutil.cd_frequency_intraday:
            self.datetime_list = sorted(self.df_metrics[col_datetime].unique())
            self.eval_datetime = self.datetime_list[0]
            self.add_dtdate_column(col_date,col_datetime)
        self.update_multiplier_adjustment()


    def start(self, col_date='dt_date',col_datetime='dt_datetime',col_id='id_instrument'):
        self.dt_list = sorted(self.df_metrics[col_date].unique())
        self.start_date = self.dt_list[0] #0
        self.end_date = self.dt_list[-1] # len(self.dt_list)-1
        self.eval_date = self.start_date
        self.update_bktoption_list()
        self.update_current_daily_state()

    def next(self):
        if self.frequency in self.bktutil.cd_frequency_low:
            self.update_eval_date()
            self.update_bktoption_list()
            self.update_current_daily_state()
            for bkt in self.bktoption_list: bkt.next()
        else:
            self.update_eval_datetime()
            if self.eval_datetime.date() != self.eval_date:
                self.eval_date = self.eval_datetime.date()
                self.update_bktoption_list()
            for bkt in self.bktoption_list: bkt.next()

    def update_bktoption_list(self,col_date='dt_date',col_datetime='dt_datetime',col_id='id_instrument'):
        if self.frequency in self.bktutil.cd_frequency_low:
            df_current = self.df_metrics[self.df_metrics[col_date] == self.eval_date].reset_index()
        else:
            df_current = self.df_metrics[self.df_metrics[col_datetime] == self.eval_datetime].reset_index()
        df_current = self.get_duplicate_strikes_dropped(df_current)
        option_ids = df_current[col_id].unique()
        bkt_ids = []
        for bktoption in self.bktoption_list:
            if bktoption.id_instrument not in option_ids:
                self.bktoption_list.remove(bktoption)
            bkt_ids.append(bktoption.id_instrument)
        for optionid in option_ids:
            if optionid in bkt_ids: continue
            df_option = self.df_metrics[self.df_metrics[col_id] == optionid].reset_index()
            bktoption = BktOption(self.frequency, df_option, optionid)
            self.bktoption_list.append(bktoption)

    def update_eval_date(self):
        self.index += 1
        self.eval_date = self.dt_list[min(self.dt_list.index(self.eval_date)+1
                            ,len(self.dt_list)-1)]


    def update_eval_datetime(self):
        self.eval_datetime = self.datetime_list[min(self.datetime_list.index(self.eval_datetime)+1,
                                               len(self.datetime_list)-1)]


    def update_current_daily_state(self):
        if self.frequency in self.bktutil.cd_frequency_low:
            self.df_daily_state = self.df_metrics[self.df_metrics['dt_date']==self.eval_date].reset_index()
        else:
            self.df_daily_state = None

    def update_eligible_maturities(self,n): # n: 要求合约剩余期限大于n（天）
        if n < 1:
            print('要求合约剩余期限大于1日！')
            return []
        maturity_dates = sorted(self.df_daily_state['dt_maturity'].unique())
        ttm0 = (maturity_dates[0]-self.eval_date).days
        if ttm0 < n: maturity_dates.remove(maturity_dates[0])
        self.eligible_maturities = maturity_dates


    def get_volsurface_squre(self,option_type,n,col_adj_strike='adj_strike',
                             col_option_type='cd_option_type',col_maturitydt='dt_maturity',
                             col_implied_vol = 'implied_vol'):
        ql_maturities = []
        if len(self.eligible_maturities) == 0: self.update_eligible_maturities(n)
        df = self.get_duplicate_strikes_dropped(self.collect_implied_vol(self.bktoption_list))
        df_mdt_list = []
        iv_name_list = []
        maturity_list = []
        for idx,mdt in enumerate(self.eligible_maturities):
            iv_rename = 'implied_vol_'+str(idx)
            df_mkt = df[(df[col_maturitydt]==mdt)&(df[col_option_type]==option_type)] \
            .rename(columns={col_implied_vol: iv_rename}).set_index(col_adj_strike)
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


    def set_bktoptions_mdt0(self,n=1): # n: 要求合约剩余期限大于n（天）
        self.bktoption_list_mdt0 = self.get_bktoptions_by_mdtnbr(0,n)

    def set_bktoptions_mdt1(self,n=1): # n: 要求合约剩余期限大于n（天）
        self.bktoption_list_mdt1 = self.get_bktoptions_by_mdtnbr(1,n)

    def set_bktoptions_mdt2(self,n=1): # n: 要求合约剩余期限大于n（天）
        self.bktoption_list_mdt2 = self.get_bktoptions_by_mdtnbr(2,n)

    def set_bktoptions_mdt3(self,n=1): # n: 要求合约剩余期限大于n（天）
        self.bktoption_list_mdt3 = self.get_bktoptions_by_mdtnbr(3,n)

    def get_mdt0(self,n=1): # n: 要求合约剩余期限大于n（天）
        if len(self.eligible_maturities) == 0 : self.update_eligible_maturities(n)
        return self.eligible_maturities[0]

    def get_mdt1(self,n=1): # n: 要求合约剩余期限大于n（天）
        if len(self.eligible_maturities) == 0 : self.update_eligible_maturities(n)
        return self.eligible_maturities[1]

    def get_mdt2(self,n=1): # n: 要求合约剩余期限大于n（天）
        if len(self.eligible_maturities) == 0 : self.update_eligible_maturities(n)
        return self.eligible_maturities[2]

    def get_mdt3(self,n=1): # n: 要求合约剩余期限大于n（天）
        if len(self.eligible_maturities) == 0 : self.update_eligible_maturities(n)
        return self.eligible_maturities[3]

    def get_bktoptions_by_mdtnbr(self,nbr,n):
        self.update_eligible_maturities(n)
        maturity_dates = self.eligible_maturities
        if nbr > len(maturity_dates)-1: return
        mdt = maturity_dates[nbr]
        bktoption_list_mdt = []
        for option in self.bktoption_list:
            if option.maturitydt == mdt: bktoption_list_mdt.append(option)
        return bktoption_list_mdt


    def get_duplicate_strikes_dropped(self,df_metrics,col_adj_strike='adj_strike',
                                      col_trading_volume='amt_trading_volume'):
        maturities = sorted(df_metrics['dt_maturity'].unique())
        df = pd.DataFrame()
        for mdt in maturities:
            df_mdt_call = df_metrics[(df_metrics['dt_maturity']==mdt) &
                                     (df_metrics['cd_option_type']=='call')]\
                            .sort_values(by=col_trading_volume, ascending=False) \
                            .drop_duplicates(subset=[col_adj_strike])
            df_mdt_put = df_metrics[(df_metrics['dt_maturity'] == mdt) &
                                    (df_metrics['cd_option_type'] == 'put')]\
                            .sort_values(by=col_trading_volume, ascending=False) \
                            .drop_duplicates(subset=[col_adj_strike])
            df = df.append(df_mdt_call,ignore_index=True)
            df = df.append(df_mdt_put,ignore_index=True)
        return df

    def update_multiplier_adjustment(self,col_adj_option_price = 'adj_option_price',
                                     col_adj_strike = 'adj_strike',
                                     col_option_price='amt_close',
                                     col_multiplier='nbr_multiplier',
                                     col_strike='amt_strike'):
        for (idx,row) in self.df_metrics.iterrows():
            self.df_metrics.loc[idx,col_adj_strike] = round(row[col_strike]*row[col_multiplier]/10000,2)
            # self.df_metrics.loc[idx,'adj_underlying_price'] = round(row[col_underlying_price]*row[col_multiplier]/10000,2)
            self.df_metrics.loc[idx,col_adj_option_price] = round(row[col_option_price]*row[col_multiplier]/10000,2)


    def add_dtdate_column(self,col_date='dt_date',col_datetime='dt_datetime'):
        if col_date not in self.df_metrics.columns.tolist():
            for (idx,row) in self.df_metrics.iterrows():
                self.df_metrics.loc[idx, col_date] = row[col_datetime].date()

    def collect_implied_vol(self,bktoption_list,col_adj_strike = 'adj_strike'):
        df = pd.DataFrame()
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.bktutil.cd_frequency_low:
                df.loc[idx, 'dt_date'] = self.eval_date
            else:
                df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, 'id_instrument'] = option.id_instrument
            df.loc[idx, col_adj_strike] = option.adj_strike
            df.loc[idx, 'cd_option_type'] = option.option_type
            df.loc[idx, 'dt_maturity'] = option.maturitydt
            iv = option.get_implied_vol()
            df.loc[idx, 'implied_vol'] = iv
            df.loc[idx, 'amt_trading_volume'] = option.get_trading_volume()
            # print(option.id_instrument, '   ', option.strike, '  ',option.option_type, '  ',iv )
        return df

    def collect_delta(self,bktoption_list,col_adj_strike = 'adj_strike'):
        df = pd.DataFrame()
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.bktutil.cd_frequency_low:
                df.loc[idx, 'dt_date'] = self.eval_date
            else:
                df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, 'id_instrument'] = option.id_instrument
            df.loc[idx, col_adj_strike] = option.adj_strike
            df.loc[idx, 'cd_option_type'] = option.option_type
            df.loc[idx, 'dt_maturity'] = option.maturitydt
            df.loc[idx, 'implied_vol'] = option.get_implied_vol()
            df.loc[idx, 'amt_delta'] = option.get_delta()
        return df

    def collect_theta(self,bktoption_list,col_adj_strike = 'adj_strike'):
        df = pd.DataFrame()
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.bktutil.cd_frequency_low:
                df.loc[idx, 'dt_date'] = self.eval_date
            else:
                df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, 'id_instrument'] = option.id_instrument
            df.loc[idx, col_adj_strike] = option.adj_strike
            df.loc[idx, 'cd_option_type'] = option.option_type
            df.loc[idx, 'dt_maturity'] = option.maturitydt
            df.loc[idx, 'implied_vol'] = option.get_implied_vol()

            df.loc[idx, 'amt_theta'] = option.get_theta()
        return df

    def collect_vega(self,bktoption_list,col_adj_strike = 'adj_strike'):
        df = pd.DataFrame()
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.bktutil.cd_frequency_low:
                df.loc[idx, 'dt_date'] = self.eval_date
            else:
                df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, 'id_instrument'] = option.id_instrument
            df.loc[idx, col_adj_strike] = option.adj_strike
            df.loc[idx, 'cd_option_type'] = option.option_type
            df.loc[idx, 'dt_maturity'] = option.maturitydt
            df.loc[idx, 'implied_vol'] = option.get_implied_vol()

            df.loc[idx, 'amt_vega'] = option.get_vega()
        return df


    def collect_carry(self,bktoption_list,n,col_adj_strike = 'adj_strike',col_option_price='amt_close'):
        df = pd.DataFrame()
        bvs_call = self.get_volsurface_squre('call',n)
        bvs_put = self.get_volsurface_squre('put',n)
        for idx,option in enumerate(bktoption_list):
            if self.frequency in self.bktutil.cd_frequency_low:
                df.loc[idx, 'dt_date'] = self.eval_date
            else:
                df.loc[idx, 'dt_datetime'] = self.eval_datetime
            df.loc[idx, 'id_instrument'] = option.id_instrument
            df.loc[idx, 'code_instrument'] = option.code_instrument
            df.loc[idx, col_adj_strike] = option.adj_strike
            df.loc[idx, 'cd_option_type'] = option.option_type
            df.loc[idx, 'dt_maturity'] = option.maturitydt
            df.loc[idx, 'implied_vol'] = option.get_implied_vol()
            df.loc[idx, col_option_price] = option.option_price
            df.loc[idx, 'carry'] = option.get_carry(bvs_call,bvs_put)
        return df


    def to_ql_date(self,date):
        return ql.Date(date.day,date.month,date.year)


















































