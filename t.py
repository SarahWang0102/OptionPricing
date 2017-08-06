import datetime
import matplotlib.pyplot as plt
import plot_util as pu

dates               = [datetime.date(2017, 7, 18), datetime.date(2017, 7, 19), datetime.date(2017, 7, 20)]
underlying_chg      = []
spread_this_month   = [-0.11732033224299879, -0.16051632253518644, -0.15316860049574194]
spread_next_month   = [-0.028780890979521703, -0.04655114093975984, -0.034238303438286107]
spread_this_season  = [-0.09432627207419347, -0.09775127772199657, -0.05715156691360227]
spread_next_season  = [-0.06384582794086516, -0.07258031439924831, -0.05624903769841611]
volum_next_month    = [186.403459, 221.137011, 195.165904]
callvol_next_month  = [0.1550708854438636, 0.13744643397647363, 0.15216795254398924]
putvol_next_month   = [0.18385177642338532, 0.18399757491623348, 0.18640625598227534]
underlying_close    = [2.659, 2.702, 2.71]

plt.rcParams['font.sans-serif'] = ['STKaiti']
f, axarr = plt.subplots(3, sharex=True)

#axarr[0].set_title(u"看涨看跌期权隐含波动率差(CPIV)")
line1, = axarr[0].plot(dates, spread_this_month, color=pu.c1, linestyle=pu.l1, linewidth=2, label=u'CPIV当月')
line2, = axarr[0].plot(dates, spread_next_month, color=pu.c2, linestyle=pu.l2, linewidth=2, label=u'CPIV下月')
line3, = axarr[0].plot(dates, spread_this_season, color=pu.c3, linestyle=pu.l3, linewidth=2, label=u'CPIV当季')
line4, = axarr[0].plot(dates, spread_next_season, color=pu.c4, linestyle=pu.l4, linewidth=2, label=u'CPIV下季')
line4.set_dashes(pu.dash)
line5, = axarr[1].plot(dates, volum_next_month, color=pu.c5, linestyle=pu.l5, linewidth=2, label="成交量(百万)")

line6, = axarr[2].plot(dates, callvol_next_month, color=pu.c6, linestyle=pu.l6, linewidth=2, label="隐含波动率-看涨")
line7, = axarr[2].plot(dates, putvol_next_month, color=pu.c7, linestyle=pu.l7, linewidth=2, label="隐含波动率-看跌")

# Shrink current axis by 20%
box0 = axarr[0].get_position()
axarr[0].set_position([box0.x0, box0.y0, box0.width * 0.8, box0.height])
# Put a legend to the right of the current axis
lgd0 = axarr[0].legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)

box1 = axarr[1].get_position()
axarr[1].set_position([box1.x0, box1.y0, box1.width * 0.8, box1.height])
lgd1 = axarr[1].legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)

box2 = axarr[2].get_position()
axarr[2].set_position([box2.x0, box2.y0, box2.width * 0.8, box2.height])
lgd2 = axarr[2].legend(loc='center left', bbox_to_anchor=(1, 0.5),frameon=False)

f.savefig('image_output.png', dpi=300, format='png', bbox_extra_artists=(lgd0,lgd1,lgd2,), bbox_inches='tight')
#axarr[3].legend()
axarr[1].grid()
axarr[0].grid()
#axarr[3].grid()
plt.draw()
plt.show()
