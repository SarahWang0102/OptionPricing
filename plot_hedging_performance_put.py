import os
import datetime
import pickle
import numpy as np
import math

def hedging_performance(svi_pct,dates):
    mny_0 = {} # S/k <0.97
    mny_1 = {} # 0.97 - 1.00
    mny_2 = {} # 1.00 - 1.03
    mny_3 = {} # S/k > 1.03

    for date in dates:
        if date in svi_pct.keys():
            pct_Ms = svi_pct.get(date)
        else:
            print('date not in list')
            continue
        # month number = 1
        for nbr_m in pct_Ms.keys():
            if nbr_m not in mny_0.keys():mny_0.update({nbr_m:[]})
            if nbr_m not in mny_1.keys():mny_1.update({nbr_m: []})
            if nbr_m not in mny_2.keys():mny_2.update({nbr_m:[]})
            if nbr_m not in mny_3.keys():mny_3.update({nbr_m: []})
            moneyness = pct_Ms.get(nbr_m)[0]
            errors = pct_Ms.get(nbr_m)[1]
            if type(moneyness) == float:
                moneyness = [moneyness]
                errors = [errors]
            for idx_m,mny in enumerate(moneyness):
                e = errors[idx_m]
                if math.isnan(e) :
                    print(e)
                    e = 0.0
                if mny <= 0.97:
                    mny_0.get(nbr_m).append(e)
                elif mny > 0.97 and mny <= 1.00 :
                    mny_1.get(nbr_m).append(e)
                elif mny > 1.00 and mny <= 1.03:
                    mny_2.get(nbr_m).append(e)
                else:
                    mny_3.get(nbr_m).append(e)
    return mny_0,mny_1,mny_2,mny_3

with open(os.getcwd()+'/intermediate_data/hedging_daily_hedge_errors_svi_put.pickle','rb') as f:
    svi,svi_pct = pickle.load(f)


print(svi_pct)

with open(os.getcwd()+'/intermediate_data/hedging_daily_hedge_errors_bs_put.pickle','rb') as f:
    bs,bs_pct = pickle.load(f)

print(bs_pct)

'''
# Moneyness
dates = svi_pct.keys()
print(dates)
mny_0,mny_1,mny_2,mny_3 = hedging_performance(svi_pct,dates)
print("SVI Model Average Hedging Percent Error,PUT : ")

print("="*100)
print("%20s %20s %30s" % ("contract month","moneyness", "avg hedging error(%)"))
print("-"*100)
for i in range(4):
    if len(mny_0.get(i)) > 0: print("%20s %20s %25s" % (i,' < 0.97',round(sum(mny_0.get(i))*100/len(mny_0.get(i)),4)))
    if len(mny_1.get(i))>0: print("%20s %20s %25s" % (i,' 0.97 - 1.00', round(sum(mny_1.get(i))*100 / len(mny_1.get(i)),4)))
    if len(mny_2.get(i)) > 0: print("%20s %20s %25s" % (i,' 1.00 - 1.03', round(sum(mny_2.get(i))*100 / len(mny_2.get(i)),4)))
    if len(mny_3.get(i)) > 0: print("%20s %20s %25s" % (i,' > 1.03', round(sum(mny_3.get(i))*100 / len(mny_3.get(i)),4)))
    print("-" * 100)
'''
#dates = [datetime.date(2017, 6, 9), datetime.date(2017, 6, 12), datetime.date(2017, 6, 13), datetime.date(2017, 6, 14), datetime.date(2017, 6, 15), datetime.date(2017, 6, 16), datetime.date(2017, 6, 19), datetime.date(2017, 6, 20), datetime.date(2017, 6, 21), datetime.date(2017, 6, 22), datetime.date(2017, 6, 23), datetime.date(2017, 6, 26), datetime.date(2017, 6, 27), datetime.date(2017, 7, 3), datetime.date(2017, 7, 4), datetime.date(2017, 7, 5), datetime.date(2017, 7, 6), datetime.date(2017, 7, 7), datetime.date(2017, 7, 10), datetime.date(2017, 7, 11), datetime.date(2017, 7, 12)]
dates = [datetime.date(2017, 6, 7), datetime.date(2017, 6, 8), datetime.date(2017, 6, 9), datetime.date(2017, 6, 12), datetime.date(2017, 6, 13), datetime.date(2017, 6, 14), datetime.date(2017, 6, 15), datetime.date(2017, 6, 16), datetime.date(2017, 6, 19), datetime.date(2017, 6, 20), datetime.date(2017, 6, 21), datetime.date(2017, 6, 22), datetime.date(2017, 6, 23), datetime.date(2017, 6, 26), datetime.date(2017, 6, 27), datetime.date(2017, 6, 28), datetime.date(2017, 7, 3), datetime.date(2017, 7, 5), datetime.date(2017, 7, 6), datetime.date(2017, 7, 7), datetime.date(2017, 7, 10), datetime.date(2017, 7, 11), datetime.date(2017, 7, 12)]
mny_0,mny_1,mny_2,mny_3 = hedging_performance(bs_pct,dates)
print("="*100)
print("BS Model Average Hedging Percent Error,PUT : ")

print("="*100)
print("%20s %20s %30s" % ("contract month","moneyness", "avg hedging error(%)"))
print("-"*100)
for i in range(4):
    if len(mny_0.get(i)) > 0: print("%20s %20s %25s" % (i,' < 0.97',round(sum(mny_0.get(i))*100/len(mny_0.get(i)),4)))
    if len(mny_1.get(i)) > 0: print("%20s %20s %25s" % (i,' 0.97 - 1.00', round(sum(mny_1.get(i))*100 / len(mny_1.get(i)),4)))
    if len(mny_2.get(i)) > 0: print("%20s %20s %25s" % (i,' 1.00 - 1.03', round(sum(mny_2.get(i))*100 / len(mny_2.get(i)),4)))
    if len(mny_3.get(i)) > 0: print("%20s %20s %25s" % (i,' > 1.03', round(sum(mny_3.get(i))*100 / len(mny_3.get(i)),4)))
    print("-" * 100)
print('total date : ', len(dates))










'''
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

'''