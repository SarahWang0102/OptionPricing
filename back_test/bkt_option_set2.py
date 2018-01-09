import datetime
import pandas as pd
from back_test.bkt_option import BktOption
from back_test.bkt_util import BktUtil



class OptionSet(object):


    def __init__(self, cd_frequency, df_option_metrics,col_date='dt_date',col_datetime='dt_datetime'):
        self.bktutil = BktUtil()
        self.frequency = cd_frequency
        self.df_metrics = df_option_metrics
        self.bktoption_list = []
        self.index = 0
        if self.frequency in self.bktutil.cd_frequency_intraday:
            self.datetime_list = sorted(self.df_metrics[col_datetime].unique())
            self.eval_datetime = self.datetime_list[0]
            self.add_dtdate_column(col_date,col_datetime)
        self.adjust_multiplier()


    def start(self, col_date='dt_date',col_datetime='dt_datetime',col_id='id_instrument'):
        self.dt_list = sorted(self.df_metrics[col_date].unique())
        self.start_date = self.dt_list[0] #0
        self.end_date = self.dt_list[-1] # len(self.dt_list)-1
        self.eval_date = self.start_date
        self.update_bktoption_list()
        # for bkt in self.bktoption_list: bkt.start()


    def next(self):
        if self.frequency in self.bktutil.cd_frequency_low:
            self.update_eval_date()
            self.update_bktoption_list()
            for bkt in self.bktoption_list: bkt.next()
        else:
            self.update_eval_datetime()
            if self.eval_datetime.date() != self.eval_date:
                self.eval_date = self.eval_datetime.date()
                self.update_bktoption_list()
            for bkt in self.bktoption_list: bkt.next()

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

    def update_bktoption_list(self,col_date='dt_date',col_datetime='dt_datetime',col_id='id_instrument'):
        if self.frequency in self.bktutil.cd_frequency_low:
            df_current = self.df_metrics[self.df_metrics[col_date] == self.eval_date].reset_index()
        else:
            df_current = self.df_metrics[self.df_metrics[col_datetime] == self.eval_datetime].reset_index()
        # print('before drop duplicate')
        # print(df_current)
        df_current = self.drop_duplicate_strikes(df_current)
        # print('after drop duplicate')
        # print(df_current)
        option_ids = df_current[col_id].unique()
        bkt_ids = []
        for bktoption in self.bktoption_list:
            if bktoption.id_instrument not in option_ids:
                self.bktoption_list.remove(bktoption)
            bkt_ids.append(bktoption.id_instrument)
        for optionid in option_ids:
            if optionid not in bkt_ids:
                df_option = self.df_metrics[self.df_metrics[col_id] == optionid].reset_index()
                bktoption = BktOption(self.frequency, df_option, optionid)
                self.bktoption_list.append(bktoption)


    def adjust_multiplier(self):
        for (idx,row) in self.df_metrics.iterrows():
            self.df_metrics.loc[idx,'adjusted_strike'] = round(row['amt_strike']*row['nbr_multiplier']/10000,2)


    def add_dtdate_column(self,col_date='dt_date',col_datetime='dt_datetime'):
        if col_date not in self.df_metrics.columns.tolist():
            for (idx,row) in self.df_metrics.iterrows():
                self.df_metrics.loc[idx, col_date] = row[col_datetime].date()


    def drop_duplicate_strikes(self,df_metrics):
        maturities = sorted(df_metrics['dt_maturity'].unique())
        df = pd.DataFrame()
        for mdt in maturities:
            df_mdt_call = df_metrics[(df_metrics['dt_maturity']==mdt) &
                                     (df_metrics['cd_option_type']=='call')]\
                            .sort_values(by='amt_trading_volume', ascending=False) \
                            .drop_duplicates(subset=['adjusted_strike'])
            df_mdt_put = df_metrics[(df_metrics['dt_maturity'] == mdt) &
                                    (df_metrics['cd_option_type'] == 'put')]\
                            .sort_values(by='amt_trading_volume', ascending=False) \
                            .drop_duplicates(subset=['adjusted_strike'])
            df = df.append(df_mdt_call,ignore_index=True)
            df = df.append(df_mdt_put,ignore_index=True)
        return df

    # def get_volsurface_squre(self):

    def get_implied_vol(self,engineType):
        ret = {}
        for bkt in self.bktoption_list:
            ret[bkt.id_instrument] = bkt.implied_vol(engineType)
        return ret









































