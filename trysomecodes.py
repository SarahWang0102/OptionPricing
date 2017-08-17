from xlrd import open_workbook
import pickle
import datetime
import os
with open(os.getcwd()+'/intermediate_data/total_hedging_bs_estimated_vols.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/total_hedging_dates_puts.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

print(len(daily_params))
print(len(dates))