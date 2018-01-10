import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import Utilities.svi_prepare_vol_data as svi_data
import pickle
import os
from Utilities.utilities import *

with open(os.getcwd()+'/intermediate_data/total_hedging_daily_svi_dataset_puts.pickle','rb') as f:
    daily_svi_dataset = pickle.load(f)[0]


def orgnize_data(
        evalDate,daycounter,vols_data_moneyness,expiration_dates):
    data_for_optimiztion_months = {}
    for idx_month, option_data in enumerate(vols_data_moneyness):
        expiration_date = expiration_dates[idx_month]
        ttm = daycounter.yearFraction(evalDate, expiration_date)
        impliedvols = {}
        strikes = []
        for moneyness in option_data.keys():
            vol = option_data.get(moneyness)[0]
            strike = option_data.get(moneyness)[1]
            impliedvols.update({strike:vol})
            strikes.append(strike)
        data = [strikes,impliedvols,expiration_date]
        data_for_optimiztion_months.update({idx_month:data})
    return data_for_optimiztion_months

# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(19, 7, 2017)
#evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))

# Construct Black Variance Surface
#data_BVS,mdts_BVS,strike_BVS,implied_vols,spot = get_impliedvolmat_call_BS(evalDate, daycounter,calendar)
curve = svi_data.get_curve_treasury_bond(evalDate,daycounter)
#data_BVS,iv_matrix,mdts_BVS,strike_BVS,spot = svi_data.get_impliedvolmat_call_givenKs(evalDate,daycounter,calendar,curve)

optiontype = ql.Option.Put

# Local Vol Surface
cal_vols_c, put_vols_c, maturity_dates_c, spot_c, rf_c = daily_svi_dataset.get(to_dt_date(evalDate))
expiration_dates = to_ql_dates(maturity_dates_c)
orgnized_data = orgnize_data(evalDate, daycounter, put_vols_c, expiration_dates)



strikes = orgnized_data.get(3)[0]
strikes = sorted(strikes)

vol_matrix = []
for i in range(4):
    vols_Mi = []
    for k in strikes:
        vol_dic = orgnized_data.get(i)[1]
        if k in vol_dic.keys():
            vols_Mi.append(vol_dic.get(k))
        else:
            vols_Mi.append(0.0)
    vol_matrix.append(vols_Mi)

print(vol_matrix)
print(strikes)
'''
vols =[[0.23, 0.22, 0.21, 0.20, 0.1950477511030433, 0.1869643847850921, 0.18512257254379158, 0.1779362477913733, 0.17766815956707938, 0.18046607629185935, 0.18380602259380485, 0.1938139906836207],
       [0.2279790136227556, 0.21351387450867695, 0.2011611368429878, 0.19479531430027805, 0.19168074987912384, 0.1854322862213014, 0.18418849990992253, 0.18271449526098235, 0.18245189490052213, 0.1829192259330565, 0.18611618999750465, 0.19029705365597444],
       [0.20153142988739048, 0.19576074284104286, 0.19070596874783702, 0.1891626143037103, 0.18819509769620482, 0.1844214118961223, 0.1845263279847316, 0.18341553539491257, 0.18471851891766994, 0.1851833685176748, 0.18690876279121632, 0.19000233269956135]]
'''
vols = [[0.25, 0.24, 0.22, 0.21, 0.20226778985225433, 0.19016157408553241, 0.18838210394041205, 0.18468155850417883, 0.18131396348190326, 0.1783938708699072, 0.18018870246766885, 0.18667891512042392],
        [0.2449897447635236, 0.22837076995826824, 0.21949149068217633, 0.20985304700906196, 0.2041719266214876, 0.20033927445461783, 0.19807488063669001, 0.19085764979481112, 0.19159774017588876, 0.1919016701828232, 0.1934624432856883, 0.19404949435809657],
        [0.2125275028151895, 0.20811693067114082, 0.2025986300844737, 0.20158943603285462, 0.2000892759230489, 0.19688870909481423, 0.19564828876427126, 0.1944272155713479, 0.1963103799474153, 0.193943895027244, 0.19543218041022398, 0.19545078282387943]]

expiration_dates = expiration_dates[1:4]
matrix = ql.Matrix(len(strikes), len(expiration_dates))

vol_BS = []
for i in range(matrix.rows()):
    for j in range(matrix.columns()):
        matrix[i][j] = vols[j][i]

black_var_surface = ql.BlackVarianceSurface(
    evalDate, calendar,
    expiration_dates, strikes,
    matrix, daycounter)
# yield_ts = ql.YieldTermStructureHandle(curve)
# dividend_ts = ql.YieldTermStructureHandle(ql.FlatForward(evalDate, 0.0, daycounter))
#local_vol_surface = ql.LocalVolSurface(ql.BlackVolTermStructureHandle(black_var_surface),yield_ts,dividend_ts,spot_c)
# Plot
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})
#plot_years = np.arange(0.0, 0.44, 0.005)
#plot_strikes = np.arange(2.3, 2.65, 0.001)

plot_years = np.arange(0.1,0.4,0.01)
plot_strikes = np.arange(strikes[0],strikes[-1],0.01)
fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))
surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.2)
ax.set_xlabel('K')
ax.set_ylabel('T')
#contracts = ['当月', '下月', '当季', '下季']
#ax.set_yticks(plot_years)
#ax.set_yticklabels(contracts)
fig.colorbar(surf, shrink=0.5, aspect=5)

fig.savefig('implied vol surface .png', dpi=300, format='png')
plt.show()
