from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.pyplot as plt
import os

fig1 = plt.figure('houhou')
host = host_subplot(111)

par = host.twinx()

host.set_xlabel("Distance")
host.set_ylabel("Density")
par.set_ylabel("Temperature")


fig2 = plt.figure('houhou is sorry')
host2 = host_subplot(111)

par2 = host2.twinx()

host2.set_xlabel("Distance2")
host2.set_ylabel("Density2")
par2.set_ylabel("Temperature2")


p1, = host.plot([0, 1, 2], [0, 1, 2], label="Density")
p2, = par.plot([0, 1, 2], [0, 3, 2], label="Temperature")

p11, = host2.plot([0, 1, 2], [1, 10, 2], label="Density2")
p21, = par2.plot([0, 1, 2], [9, 3, 2], label="Temperature2")


host.spines['top'].set_visible(False)
host.yaxis.set_ticks_position('left')
host.xaxis.set_ticks_position('bottom')
fig1.legend(handles=[p1,p2],labels=["Density","Temperature"],
            bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)
host2.spines['top'].set_visible(False)
host2.yaxis.set_ticks_position('left')
host2.xaxis.set_ticks_position('bottom')

fig2.legend(handles=[p11,p21],labels=["Density2","Temperature2"],
            bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)

fig1.savefig('../save_figure/CPI.png', dpi=300, format='png')

fig2.savefig('../save_figure/CPI2.png', dpi=300, format='png')
plt.show()


fig1 = plt.figure('houhou')
host = host_subplot(111)
par = host.twinx()
host.set_xlabel("Distance")
host.set_ylabel("Density")
par.set_ylabel("Temperature")
p1, = host.plot([0, 1, 2], [0, 1, 2], label="Density")
p2, = par.plot([0, 1, 2], [0, 3, 2], label="Temperature")
host.spines['top'].set_visible(False)
host.yaxis.set_ticks_position('left')
host.xaxis.set_ticks_position('bottom')
plt.legend(handles=[p1,p2],labels=["Density","Temperature"],
            bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)
fig1.savefig('../save_figure/CPI.png', dpi=300, format='png')


fig2 = plt.figure('houhou is sorry')
host2 = host_subplot(111)
par2 = host2.twinx()
host2.set_xlabel("Distance2")
host2.set_ylabel("Density2")
par2.set_ylabel("Temperature2")
p11, = host2.plot([0, 1, 2], [1, 10, 2], label="Density2")
p21, = par2.plot([0, 1, 2], [9, 3, 2], label="Temperature2")
host2.spines['top'].set_visible(False)
host2.yaxis.set_ticks_position('left')
host2.xaxis.set_ticks_position('bottom')
plt.legend(handles=[p11,p21],labels=["Density2","Temperature2"],
            bbox_to_anchor=(0., 1.02, 1., .202), loc=3,
           ncol=4, mode="expand", borderaxespad=0.)
fig2.savefig('../save_figure/CPI2.png', dpi=300, format='png')
plt.show()
