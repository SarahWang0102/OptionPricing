from xlrd import open_workbook
import pickle
import datetime
import os
date = datetime.date(2017,2,17)
daily_params  = {}
daily_params.update({date:1})
flag = 1
if flag != 0: print('y')
a = [1,2]
with open(os.getcwd()+'/intermediate_data/test.pickle','wb') as f:
    pickle.dump([daily_params],f)

with open(os.getcwd()+'/intermediate_data/test.pickle','rb') as f:
    results = pickle.load(f)

print(results)