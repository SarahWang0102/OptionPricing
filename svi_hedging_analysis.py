import svi_read_data as wind_data
import matplotlib.pyplot as plt
from utilities import convert_datelist_from_datetime_to_ql as to_ql_dates
from utilities import convert_date_from_ql_to_datetime as to_dt_date
from utilities import convert_date_from_datetime_to_ql as to_ql_date
import svi_prepare_vol_data as svi_data
import svi_calibration_utility as svi_util
import QuantLib as ql
import numpy as np
import timeit
import os
import pickle


start = timeit.default_timer()

calendar = ql.China()
daycounter = ql.ActualActual()

def Date(d,m,y):
    return ql.Date(d,m,y)
'''
with open(os.getcwd()+'/intermediate_data/hedging_daily_params_pcprates.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/hedging_dates_pcprates.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/hedging_daily_svi_dataset_pcprates.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]
'''
with open(os.getcwd()+'/intermediate_data/hedging_daily_params_calls.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/hedging_dates_calls.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.getcwd()+'/intermediate_data/hedging_daily_svi_dataset_calls.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]

# Hedge option using underlying 50ETF
daily_hedge_errors = {}
daily_pct_hedge_errors = {}
option_last_close_Ms = {}
f0, axarr0 = plt.subplots()
f1, axarr1 = plt.subplots()
f2, axarr2 = plt.subplots()
f3, axarr3 = plt.subplots()
for idx_date,date in enumerate(dates[0:10]):
    try:
        date = to_ql_date(date)
        calibrated_params = daily_params.get(to_dt_date(date))
        dataset = daily_svi_dataset.get(to_dt_date(date))
        curve = svi_data.get_curve_treasury_bond(date, daycounter)
        cal_vols, put_vols, maturity_dates, spot, rfs = dataset
        expiration_dates = to_ql_dates(maturity_dates)
        data_months = svi_util.orgnize_data_for_optimization_single_optiontype(
            date, daycounter, cal_vols, expiration_dates, spot, curve, ql.Option.Call)
        month_indexs = wind_data.get_contract_months(date)
        for i in range(4):
            nbr_month = month_indexs[i]
            data = data_months.get(i)
            logMoneynesses = data[0]
            totalvariance = data[1]
            expiration_date = data[2]
            impliedvols = data[3]
            ttm = daycounter.yearFraction(date, expiration_date)
            params = daily_params.get(to_dt_date(date))[i]

            a_star, b_star, rho_star, m_star, sigma_star = params
            x_svi = np.arange(min(logMoneynesses) - 0.005, max(logMoneynesses) + 0.02,
                              0.1 / 100)  # log_forward_moneyness
            tv_svi2 = np.multiply(
                a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)
            if i == 0:
                axarr0.plot(logMoneynesses, impliedvols,label = str(date)+','+str(expiration_date))
                #axarr0.plot(x_svi, tv_svi2, 'b--')
            elif i == 1:
                axarr1.plot(logMoneynesses, impliedvols,label = str(date)+','+str(expiration_date))
                #axarr1.plot(x_svi, tv_svi2, 'b--')
            elif i == 2:
                axarr2.plot(logMoneynesses, impliedvols,label = str(date)+','+str(expiration_date))
                #axarr2.plot(x_svi, tv_svi2, 'b--')
            else:
                axarr3.plot(logMoneynesses, impliedvols,label = str(date)+','+str(expiration_date))
                #axarr3.plot(x_svi, tv_svi2, 'b--')
    except Exception as e:
        print(e)
        continue

stop = timeit.default_timer()
print('calibration time : ',stop-start)
axarr0.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
axarr1.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
axarr2.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
axarr3.legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)
plt.show()


