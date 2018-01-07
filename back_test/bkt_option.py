

class BktOption(object):

    def __init__(self,cd_frequency,option,df_hist_metrics):
        self.frequency = cd_frequency
        self.option_basicinfo = option
        self.df_metrics = df_hist_metrics
        self.nbr_index = len(df_hist_metrics)
        self.current_index = 0
        self.last_index = len(df_hist_metrics)-1

    def current_state(self):
        self.current_state = self.df_metrics.loc[self.current_index]

    def next(self):
        self.current_index = max(self.current_index+1,self.last_index)


