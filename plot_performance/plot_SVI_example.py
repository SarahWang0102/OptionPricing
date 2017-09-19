import matplotlib.pyplot as plt
import numpy as np
import Utilities.plot_util as pu

a_star, b_star, rho_star, m_star, sigma_star = 0.04, 0.4,-0.4,0.1,0.2

#print(risk_free_rates)
mark = "o"
line = pu.l3
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 13})


ff, ax = plt.subplots()
x_svi  = np.arange(-1, 1, 0.1 / 100)
tv_svi = a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2))
ax.plot(x_svi, tv_svi, color = pu.c1,linestyle = pu.l1,linewidth = 2,label="SVI隐含方差曲线")
ax.spines['right'].set_visible(False)
ax.spines['top'].set_visible(False)
ax.yaxis.set_ticks_position('left')
ax.xaxis.set_ticks_position('bottom')
ax.set_xlabel('x')
ax.legend()

ff.savefig('SVI total variance example .png', dpi=300, format='png')
plt.show()


