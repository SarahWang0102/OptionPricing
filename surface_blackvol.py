from WindPy import w
import QuantLib as ql
import pandas as pd
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from matplotlib import cm
import svi_prepare_vol_data as svi_data

w.start()

# Evaluation Settings
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(19, 7, 2017)
#evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
# Construct Black Variance Surface
#data_BVS,mdts_BVS,strike_BVS,implied_vols,spot = get_impliedvolmat_call_BS(evalDate, daycounter,calendar)
curve = svi_data.get_curve_treasury_bond(evalDate,daycounter)
data_BVS,iv_matrix,mdts_BVS,strike_BVS,spot = svi_data.get_impliedvolmat_call_givenKs(evalDate,daycounter,calendar,curve)
for i in range(iv_matrix.rows()):
    for j in range(iv_matrix.columns()):
        iv_matrix[i][j] = data_BVS[j][i]
black_var_surface = ql.BlackVarianceSurface(
    evalDate, calendar,
    mdts_BVS, strike_BVS,
    iv_matrix, daycounter)

# Plot
plt.rcParams['font.sans-serif'] = ['STKaiti']
plot_years = np.arange(0.0, 0.44, 0.005)
plot_strikes = np.arange(2.3, 2.65, 0.001)
fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))

surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.2)
ax.set_xlabel('行权价')
ax.set_ylabel('距到期时间')
ax.set_zlabel('隐含波动率')
fig.colorbar(surf, shrink=0.5, aspect=5)

fig.savefig('implied_vol_surface '+ str(evalDate) +'.png', dpi=300, format='png')
plt.show()
w.stop()
