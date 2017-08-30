import Utilities.svi_prepare_vol_data as svi_data
import exotic_options.exotic_option_utilities as exotic_otil
from Utilities.utilities import *
import Utilities.hedging_utility as hedge_util
import QuantLib as ql
import numpy as np
import math
import datetime
import matplotlib.pyplot as plt
import Utilities.plot_util as pu
import os
import pickle



with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_params_puts.pickle','rb') as f:
    daily_params = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_dates_puts.pickle','rb') as f:
    dates = pickle.load(f)[0]
with open(os.path.abspath('..')+'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]


# Evaluation Settings
begDate = ql.Date(14,7,2017)
maturityDate = ql.Date(27,12,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
spot = 2.45
S0 = 2.45*100
strike = S0

calibrated_params = daily_params.get(to_dt_date(begDate))  # on calibrate_date

cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c = daily_svi_dataset.get(to_dt_date(begDate))
black_var_surface = hedge_util.get_local_volatility_surface(calibrated_params, to_ql_dates(maturity_dates_c),
                                                            begDate, daycounter, calendar, spot_c, rf_c)


rf = rf_c.get(3)

# SVI model params
params =  calibrated_params[3]
# Monte Carlo Simulation
N = 500
delta_t = 1.0/365
dates = []
evalDate = begDate
while evalDate <= maturityDate:
    dates.append(datetime.date(evalDate.year(),evalDate.month(),evalDate.dayOfMonth()))
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
plt.figure()
barrier_pct = 0.8
barriers_down = []
barrier_up = []
prices_dob = []
prices_dib = []
prices_uib = []
prices_uob = []
noise = np.random.normal(0,1,(N,len(dates)))
step = 0.01

while barrier_pct < 1.0:
    barrier = strike * barrier_pct
    barriers_down.append(barrier_pct)
    price,path_container,out_times = exotic_otil.down_out_barrier_npv(begDate,maturityDate,daycounter,calendar,N,S0,
                                                                      strike,barrier,rf,delta_t,params,noise)
    prices_dob.append(price)
    price_dib, path_container_dib, in_times_dib = exotic_otil.down_in_barrier_npv(begDate, maturityDate, daycounter,
                                                                                  calendar, N, S0, strike,barrier, rf, delta_t, params, noise)
    prices_dib.append(price_dib)
    barrier_pct += step


barrier_pct2 = 1.0
while barrier_pct2 < 1.18:
    barrier = strike*barrier_pct2
    barrier_up.append(barrier_pct2)
    price_uib, path_container_uib, in_times_uib = exotic_otil.up_in_barrier_npv(begDate, maturityDate, daycounter, calendar, N, S0, strike,barrier, rf, delta_t, params, noise)
    prices_uib.append(price_uib)
    price_uob, path_container_uob, in_times_uob = exotic_otil.up_out_barrier_npv(begDate, maturityDate, daycounter, calendar, N, S0, strike,barrier, rf, delta_t, params, noise)
    prices_uob.append(price_uob)
    barrier_pct2 += step

plt.rcParams['font.sans-serif'] = ['STKaiti']
f1,ax1 = plt.subplots()
ax1.plot(barriers_down,prices_dob,color = pu.c1,marker = '^',linestyle = pu.l1,linewidth = 2,label = 'DOB价格')
ax1.legend()
# plt.title('DOB-'+ str(begDate))
ax1.set_xlabel('障碍行权价比')
# Hide the right and top spines
ax1.spines['right'].set_visible(False)
ax1.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
ax1.yaxis.set_ticks_position('left')
ax1.xaxis.set_ticks_position('bottom')
f1.savefig( 'DOB-'+ str(begDate)+ '.png', dpi=300, format='png')

f2,ax2 = plt.subplots()
ax2.plot(barriers_down,prices_dib,color = pu.c1,marker = '^',linestyle = pu.l1,linewidth = 2,label = 'DIB价格')
ax2.legend()
#plt.title('DIB-'+str(begDate))
ax2.set_xlabel('障碍行权价比')
# Hide the right and top spines
ax2.spines['right'].set_visible(False)
ax2.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
ax2.yaxis.set_ticks_position('left')
ax2.xaxis.set_ticks_position('bottom')
f2.savefig( 'DIB-'+ str(begDate)+ '.png', dpi=300, format='png')

f3,ax3 = plt.subplots()
ax3.plot(barrier_up,prices_uib,color = pu.c1,marker = '^',linestyle = pu.l1,linewidth = 2,label = 'UIB价格')
ax3.legend()
#plt.title('UIB-'+str(begDate))
ax3.set_xlabel('障碍行权价比')
# Hide the right and top spines
ax3.spines['right'].set_visible(False)
ax3.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
ax3.yaxis.set_ticks_position('left')
ax3.xaxis.set_ticks_position('bottom')
f3.savefig( 'UIB-'+ str(begDate)+ '.png', dpi=300, format='png')

f4,ax4 = plt.subplots()
ax4.plot(barrier_up,prices_uob,color = pu.c1,marker = '^',linestyle = pu.l1,linewidth = 2,label = 'UOB价格')
ax4.legend()
#plt.title('UOB-'+str(begDate))
ax4.set_xlabel('障碍行权价比')
# Hide the right and top spines
ax4.spines['right'].set_visible(False)
ax4.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
ax4.yaxis.set_ticks_position('left')
ax4.xaxis.set_ticks_position('bottom')
f4.savefig( 'UOB-'+ str(begDate)+ '.png', dpi=300, format='png')

'''
for path in path_container:
    plt.plot(dates,path)
'''
plt.show()









