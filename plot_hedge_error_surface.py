from hedging_utility import get_1st_percentile_dates, get_2nd_percentile_dates, get_3rd_percentile_dates, get_4th_percentile_dates,hedging_performance
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.ticker import LinearLocator, FormatStrFormatter
import numpy as np
import os
import pickle

with open(os.getcwd() + '/intermediate_data/hedging_daily_hedge_errors_svi_put_no_smoothing.pickle', 'rb') as f:
    daily_hedge_errors, daily_pct_hedge_errors = pickle.load(f)


print(len(daily_pct_hedge_errors))

p1 = get_1st_percentile_dates(daily_pct_hedge_errors)
p2 = get_2nd_percentile_dates(daily_pct_hedge_errors)
p3 = get_3rd_percentile_dates(daily_pct_hedge_errors)
p4 = get_4th_percentile_dates(daily_pct_hedge_errors)
container = [p1, p2, p3, p4]
samples = ['2015.9-2016.1', '2016.2-2016.7', '2016.8-2017.1', '2017.2-2017.7']
error_container = []
for idx_c, r in enumerate(container):
    errors = []
    mny_0, mny_1, mny_2, mny_3 = hedging_performance(r, r.keys())
    for i in range(4):
        e_moneyness0 = round(sum(np.abs(mny_0.get(i))) / len(mny_0.get(i)), 4)
        e_moneyness1 = round(sum(np.abs(mny_1.get(i)))  / len(mny_1.get(i)), 4)
        e_moneyness2 = round(sum(np.abs(mny_2.get(i)))  / len(mny_2.get(i)), 4)
        e_moneyness3 = round(sum(np.abs(mny_3.get(i)))  / len(mny_3.get(i)), 4)
        error_moneynesses = [e_moneyness0,e_moneyness1,e_moneyness2,e_moneyness3]
        errors.append(error_moneynesses)
    error_container.append(errors)
print('error_container=',error_container)
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
for i,hedge_error in enumerate(error_container):

    fig = plt.figure(i)
    ax = fig.gca(projection='3d')
    #error_container= [[[13.359500000000001, 19.993600000000001, 28.59, 69.070300000000003], [4.9744000000000002, 10.3071, 12.9634, 24.4953], [3.6293000000000002, 5.8552999999999997, 7.3331, 12.361000000000001], [3.8273000000000001, 4.2294999999999998, 4.6673999999999998, 7.9375]], [[6.6010999999999997, 19.863499999999998, 29.998899999999999, 53.892899999999997], [4.6913, 9.1672999999999991, 13.236800000000001, 19.4527], [3.335, 4.7685000000000004, 7.0239000000000003, 11.2691], [3.169, 3.7827999999999999, 4.1516000000000002, 5.5315000000000003]], [[2.2143000000000002, 20.157800000000002, 40.564100000000003, 61.774299999999997], [3.1901999999999999, 8.6633999999999993, 16.091899999999999, 27.546099999999999], [2.9045999999999998, 4.1166999999999998, 5.4749999999999996, 12.397500000000001], [2.5779999999999998, 3.5362, 4.0418000000000003, 6.931]], [[2.2221000000000002, 10.0025, 21.2394, 64.867400000000004], [1.7461, 4.4267000000000003, 13.0975, 25.3064], [2.2302, 3.9517000000000002, 7.9691999999999998, 16.511199999999999], [2.2614000000000001, 3.1128999999999998, 5.1795, 10.4039]]]

    x = np.array([0.955,0.985,1.015,1.045]) # moneynesses
    y = np.arange(0, 4, 1) # contract month
    X, Y = np.meshgrid(x, y)
    Z = np.array(hedge_error).reshape(len(X), len(Y))

    print('Z : ',Z)
    # Plot the surface.
    surf = ax.plot_surface(X, Y, Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                    linewidth=0.1)

    fig.colorbar(surf, shrink=0.5, aspect=5)
    contracts = ['当月','下月','当季','下季']
    ax.set_xlabel('S/k')
    #ax.set_ylabel('合约月份')
    ax.set_yticks(y)
    ax.set_yticklabels(contracts)
    fig.savefig('hedge errors svi no smoothing, sample '+str(i)+'.png', dpi=300, format='png')

plt.show()
