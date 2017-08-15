import os
import datetime
import pickle
import numpy as np

with open(os.getcwd()+'/intermediate_data/hedging_daily_hedge_errors_svi_put.pickle','rb') as f:
    svi,svi_pct = pickle.load(f)


print(svi_pct)

with open(os.getcwd()+'/intermediate_data/hedging_daily_hedge_errors_bs_call.pickle','rb') as f:
    bs,bs_pct = pickle.load(f)

print(bs_pct)

avg_svi_errors_M0 = 0.0
avg_svi_errors_M1 = 0.0
avg_svi_errors_M2 = 0.0
avg_svi_errors_M3 = 0.0
avg_bs_errors_M0 = 0.0
avg_bs_errors_M1 = 0.0
avg_bs_errors_M2 = 0.0
avg_bs_errors_M3 = 0.0
for dt in svi_pct.keys():
    avg_svi_errors_M0 += sum(np.abs(svi_pct.get(dt).get(0)))
    avg_bs_errors_M0 += sum(np.abs(bs_pct.get(dt).get(0)))
    avg_svi_errors_M1 += sum(np.abs(svi_pct.get(dt).get(1)))
    avg_bs_errors_M1 += sum(np.abs(bs_pct.get(dt).get(1)))
    avg_svi_errors_M2 += sum(np.abs(svi_pct.get(dt).get(2)))
    avg_bs_errors_M2 += sum(np.abs(bs_pct.get(dt).get(2)))
    avg_svi_errors_M3 += sum(np.abs(svi_pct.get(dt).get(3)))
    avg_bs_errors_M3 += sum(np.abs(bs_pct.get(dt).get(3)))
avg_svi_errors_M0 = avg_svi_errors_M0/len(svi_pct.keys())
avg_bs_errors_M0 = avg_bs_errors_M0/len(svi_pct.keys())
avg_svi_errors_M1 = avg_svi_errors_M1/len(svi_pct.keys())
avg_bs_errors_M1 = avg_bs_errors_M1/len(svi_pct.keys())
avg_svi_errors_M2 = avg_svi_errors_M2/len(svi_pct.keys())
avg_bs_errors_M2 = avg_bs_errors_M2/len(svi_pct.keys())
avg_svi_errors_M3 = avg_svi_errors_M3/len(svi_pct.keys())
avg_bs_errors_M3 = avg_bs_errors_M3/len(svi_pct.keys())

print('SVI')
print(avg_svi_errors_M0)
print(avg_svi_errors_M1)
print(avg_svi_errors_M2)
print(avg_svi_errors_M3)
print('BS')
print(avg_bs_errors_M0)
print(avg_bs_errors_M1)
print(avg_bs_errors_M2)
print(avg_bs_errors_M3)

