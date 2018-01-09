import datetime
from back_test.bkt_option import BktOption
from back_test.bkt_util import BktUtil
class OptionSet(object):


    def __init__(self, cd_frequency, df_option_metrics, col_date='dt_date'):
        self.bktutil = BktUtil()
        self.frequency = cd_frequency
        self.df_metrics = df_option_metrics
        self.dt_list = sorted(self.df_metrics[col_date].unique())
        self.last_index = len(self.dt_list) - 1


    def start(self, col_date='dt_date',col_datetime='dt_datetime'):
        self.current_index = 0
        self.update_current_state()
        self.update_current_date()
        if self.frequency in self.bktutil.cd_frequency_intraday:
            self.update_current_datetime()
            # Add column 'dt_date' if not exist
            for (idx, row) in self.df_metrics.iterrows():
                self.df_metrics.loc[idx, col_date] = row[col_datetime].date()
            # Remove datetime data before 09:30
            dt = datetime.datetime(self.eval_date.year,self.eval_date.month,self.eval_date.day,9,30,00)
            while self.eval_datetime < dt:
                self.current_index += 1
                self.update_current_state()

        self.start_index = self.current_index
        self.start_state = self.current_state


    def next(self):
        self.current_index = min(self.current_index + 1, self.last_index)
        self.update_current_state()


    def reset(self):
        self.current_index = 0
        self.update_current_state()


    def update_current_state(self, col_date='dt_date',col_datetime='dt_datetime',col_id='id_instrument'):
        if self.frequency in self.bktutil.cd_frequency_low:
            self.update_current_date()
            df = self.df_metrics[self.df_metrics[col_date] == self.eval_date].reset_index()
            dict_bkt_option = {}
            for (idx, row) in df.iterrows():
                id_instrument = row[col_id]
                bktoption = BktOption(self.frequency, row)
                dict_bkt_option.update({id_instrument: bktoption})
        else:
            self.update_current_datetime()
            df = self.df_metrics[self.df_metrics[col_datetime] == self.eval_datetime].reset_index()
            dict_bkt_option = {}
            for (idx, row) in df.iterrows():
                id_instrument = row[col_id]
                bktoption = BktOption(self.frequency, row)
                dict_bkt_option.update({id_instrument: bktoption})
        self.current_state = dict_bkt_option


    def update_current_datetime(self,col_datetime='dt_datetime'):
        try:
            dt_datetime = self.current_state[col_datetime]
        except Exception as e:
            print(e)
            dt_datetime = None
        self.eval_datetime = dt_datetime


    def update_current_date(self,column_date='dt_date',col_datetime='dt_datetime'):
        try:
            dt_date = self.current_state[column_date]
        except:
            dt = self.current_state[col_datetime]
            dt_date = datetime.date(dt.year,dt.month,dt.day)
        self.eval_date = dt_date


    def get_state_by_index(self,nbr_index, col_date='dt_date'):
        dt = self.dt_list[nbr_index]
        return self.df_metrics[self.df_metrics[col_date] == dt].reset_index()








































