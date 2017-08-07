import svi_prepare_vol_data as svi_data
import QuantLib as ql
import numpy as np
import math
import datetime
import matplotlib.pyplot as plt
import plot_util as pu

# down-and-out barrier call is worthless unless its minimum remains above some “low barrier” H.
def down_out_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
    a, b, rho, m, sigma = parames
    npv_paths = []
    path_container = []
    knock_out_times = 0
    for nbr_path in range(simulation_no):
        npv = 0.0
        path = []
        evalDate = begDate
        St = S0
        I = True
        nbr_date = 0
        while evalDate <= maturityDate:
            e = noise.item(nbr_path,nbr_date)
            #print(nbr_path,' : ',noise)
            ttm = daycounter.yearFraction(evalDate, maturityDate)
            Ft = St * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
            St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
            path.append(St)
            if St < barrier: I = False # down and our
            evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
            nbr_date += 1
        ttm = daycounter.yearFraction(begDate,maturityDate)
        if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
        npv_paths.append(npv)
        path_container.append(path)
        if I==False : knock_out_times += 1
    price = np.sum(npv_paths)/simulation_no
    #print('Option price is :', price)
    #print(barrier, ' : ',knock_out_times)
    return price,path_container,knock_out_times

# down-and-in barrier is a normal European call with strike K, if its minimum went below some “low barrier” H.
def down_in_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
    a, b, rho, m, sigma = parames
    npv_paths = []
    path_container = []
    knock_in_times = 0
    for nbr_path in range(simulation_no):
        npv = 0.0
        path = []
        evalDate = begDate
        St = S0
        I = False
        nbr_date = 0
        while evalDate <= maturityDate:
            e = noise.item(nbr_path,nbr_date)
            ttm = daycounter.yearFraction(evalDate, maturityDate)
            Ft = St * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
            St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
            path.append(St)
            if St <= barrier: I = True # down and in
            evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
            nbr_date += 1
        ttm = daycounter.yearFraction(begDate,maturityDate)
        if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
        npv_paths.append(npv)
        path_container.append(path)
        if I==True : knock_in_times += 1
    price = np.sum(npv_paths)/simulation_no
    print('Option price is :', price)
    print(barrier, ' : ',knock_in_times)
    return price,path_container,knock_in_times

# up-and-in barrier is worthless unless its maximum crossed some “high barrier” H
def up_in_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
    a, b, rho, m, sigma = parames
    npv_paths = []
    path_container = []
    knock_in_times = 0
    for nbr_path in range(simulation_no):
        npv = 0.0
        path = []
        evalDate = begDate
        St = S0
        I = False
        nbr_date = 0
        while evalDate <= maturityDate:
            e = noise.item(nbr_path,nbr_date)
            ttm = daycounter.yearFraction(evalDate, maturityDate)
            Ft = St * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
            St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
            path.append(St)
            if St >= barrier: I = True # up and in
            evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
            nbr_date += 1
        ttm = daycounter.yearFraction(begDate,maturityDate)
        if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
        npv_paths.append(npv)
        path_container.append(path)
        if I==True : knock_in_times += 1
    price = np.sum(npv_paths)/simulation_no
    print('Option price is :', price)
    print(barrier, ' : ',knock_in_times)
    return price,path_container,knock_in_times

# up-and-out barrier is worthless unless its maximum remains below some “high barrier” H
def up_out_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
    a, b, rho, m, sigma = parames
    npv_paths = []
    path_container = []
    knock_out_times = 0
    for nbr_path in range(simulation_no):
        npv = 0.0
        path = []
        evalDate = begDate
        St = S0
        I = True
        nbr_date = 0
        while evalDate <= maturityDate:
            e = noise.item(nbr_path,nbr_date)
            ttm = daycounter.yearFraction(evalDate, maturityDate)
            Ft = St * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
            St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
            path.append(St)
            if St > barrier: I = False # down and our
            evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
            nbr_date += 1
        ttm = daycounter.yearFraction(begDate,maturityDate)
        if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
        npv_paths.append(npv)
        path_container.append(path)
        if I==False : knock_out_times += 1
    price = np.sum(npv_paths)/simulation_no
    #print('Option price is :', price)
    #print(barrier, ' : ',knock_out_times)
    return price,path_container,knock_out_times


# Evaluation Settings
begDate = ql.Date(14,7,2017)
maturityDate = ql.Date(27,12,2017)
calendar = ql.China()
daycounter = ql.ActualActual()
spot = 2.45
S0 = 2.45*100
strike = S0
rf_Ks_months = svi_data.calculate_PCParity_riskFreeRate(begDate, daycounter, calendar)
rf = rf_Ks_months.get(3).get(spot)
# SVI model params
params =  0.0107047521466, 0.297485230118, 0.647754886901, 0.0262354285707, 0.0554674716145
# Monte Carlo Simulation
N = 50000
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
    price,path_container,out_times = down_out_barrier_npv(begDate,maturityDate,daycounter,calendar,N,S0,strike,barrier,rf,delta_t,params,noise)
    prices_dob.append(price)
    price_dib, path_container_dib, in_times_dib = down_in_barrier_npv(begDate, maturityDate, daycounter, calendar, N, S0, strike,barrier, rf, delta_t, params, noise)
    prices_dib.append(price_dib)
    barrier_pct += step


barrier_pct2 = 1.0
while barrier_pct2 < 1.18:
    barrier = strike*barrier_pct2
    barrier_up.append(barrier_pct2)
    price_uib, path_container_uib, in_times_uib = up_in_barrier_npv(begDate, maturityDate, daycounter, calendar, N, S0, strike,barrier, rf, delta_t, params, noise)
    prices_uib.append(price_uib)
    price_uob, path_container_uob, in_times_uob = up_out_barrier_npv(begDate, maturityDate, daycounter, calendar, N, S0, strike,barrier, rf, delta_t, params, noise)
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









