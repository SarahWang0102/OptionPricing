import datetime


class OptionSet(object):


    def __init__(self, cd_frequency, df_option_metrics, col_date='dt_date'):
        self.df_metrics = df_option_metrics
        self.dt_list = sorted(self.df_metrics[col_date].unique())
        self.last_index = len(self.dt_list) - 1


    def start(self):
        self.current_index = 0
        self.update_current_state()
        self.start_state = self.current_state


    def next(self):
        self.current_index = min(self.current_index + 1, self.last_index)
        self.update_current_state()


    def reset(self):
        self.current_index = 0
        self.update_current_state()


    def update_current_state(self, col_date='dt_date'):
        self.current_date = self.dt_list[self.current_index]
        self.current_state = self.df_metrics[self.df_metrics[col_date] == self.current_date].reset_index()


    def get_state_by_index(self,nbr_index, col_date='dt_date'):
        dt = self.dt_list[nbr_index]
        return self.df_metrics[self.df_metrics[col_date] == dt].reset_index()
