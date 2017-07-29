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
evalDate = ql.Date(12, 6, 2017)

# Construct Black Variance Surface
#data_BVS,mdts_BVS,strike_BVS,implied_vols,spot = get_impliedvolmat_call_BS(evalDate, daycounter,calendar)
data_BVS,iv_matrix,mdts_BVS,strike_BVS,spot = svi_data.get_impliedvolmat_call_wind_givenKs(evalDate)
for i in range(iv_matrix.rows()):
    for j in range(iv_matrix.columns()):
        iv_matrix[i][j] = data_BVS[j][i]
black_var_surface = ql.BlackVarianceSurface(
    evalDate, calendar,
    mdts_BVS, strike_BVS,
    iv_matrix, daycounter)

# Plot
plot_years = np.arange(0, 0.5, 0.05)
plot_strikes = np.arange(2.45, 2.6, 0.01)
fig = plt.figure()
ax = fig.gca(projection='3d')
X, Y = np.meshgrid(plot_strikes, plot_years)
Z = np.array([black_var_surface.blackVol(y, x)
              for xr, yr in zip(X, Y)
                  for x, y in zip(xr,yr) ]
             ).reshape(len(X), len(X[0]))

surf = ax.plot_surface(X,Y,Z, rstride=1, cstride=1, cmap=cm.coolwarm,
                linewidth=0.1)
fig.colorbar(surf, shrink=0.5, aspect=5)
plt.show()


w.stop()
