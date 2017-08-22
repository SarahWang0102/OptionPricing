import operator
import matplotlib.pyplot as plt
import svi_prepare_vol_data as svi_data
import svi_calibration_utility as svi_util
import svi_read_data as raw_data
import QuantLib as ql
import plot_util as pu
from WindPy import w



def get_iv_plot_data_PCPRate(cal_vols_data, put_vols_data):
    call_volatilities_op = {}
    put_volatilities_op = {}
    strikes_op = {}
    ql.Settings.instance().evaluationDate = evalDate
    for idx_month,call_vol_dict in enumerate(cal_vols_data):
        put_vol_dict = put_vols_data[idx_month]
        call_volatilities = []
        put_volatilities = []
        strikes = []
        call_sorted = sorted(call_vol_dict.items(), key=operator.itemgetter(0))
        call_vol_dict_sorted = dict(call_sorted)
        put_sorted = sorted(put_vol_dict.items(), key=operator.itemgetter(0))
        put_vol_dict_sorted = dict(put_sorted)

        for k in call_vol_dict_sorted.keys():
            strikes.append(k)
            call_volatilities.append(call_vol_dict_sorted.get(k)[0])
            put_volatilities.append(put_vol_dict_sorted.get(k)[0])

        strikes_op.update({idx_month:strikes})
        call_volatilities_op.update({idx_month:call_volatilities})
        put_volatilities_op.update({idx_month:put_volatilities})
    return strikes_op,call_volatilities_op,put_volatilities_op

def get_iv_plot_data(cal_vols_data, put_vols_data):
    call_volatilities_op = {}
    put_volatilities_op = {}
    strikes_op = {}
    ql.Settings.instance().evaluationDate = evalDate
    for idx_month,call_vol_dict in enumerate(cal_vols_data):
        put_vol_dict = put_vols_data[idx_month]
        call_volatilities = []
        put_volatilities = []
        strikes = []
        call_sorted = sorted(call_vol_dict.items(), key=operator.itemgetter(0))
        call_vol_dict_sorted = dict(call_sorted)
        put_sorted = sorted(put_vol_dict.items(), key=operator.itemgetter(0))
        put_vol_dict_sorted = dict(put_sorted)

        for k in call_vol_dict_sorted.keys():
            strikes.append(k)
            call_volatilities.append(call_vol_dict_sorted.get(k))
            put_volatilities.append(put_vol_dict_sorted.get(k))

        strikes_op.update({idx_month:strikes})
        call_volatilities_op.update({idx_month:call_volatilities})
        put_volatilities_op.update({idx_month:put_volatilities})
    return strikes_op,call_volatilities_op,put_volatilities_op
w.start()
# Evaluation Settings
calendar   = ql.China()
daycounter = ql.ActualActual()
evalDate = ql.Date(19,7,2017)
begDate  = evalDate

# Underlying close prices
spotprice_dic = raw_data.get_underlying_ts()


curve = svi_data.get_curve_treasury_bond(evalDate, daycounter)

#rf_avg_months =  calculate_PCParity_riskFreeRate(evalDate,daycounter,calendar)

cal_vols_data, put_vols_data = svi_data.get_call_put_impliedVols_strikes(evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
cal_vols_data_moneyness, put_vols_data_monetness,expiration_dates,spot,x = svi_data.get_call_put_impliedVols_moneyness_PCPrate_pcvt(evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
strikes_op_m,call_volatilities_op_m,put_volatilities_op_m =get_iv_plot_data_PCPRate(cal_vols_data_moneyness, put_vols_data_monetness)
#cal_vols_data_moneyness, put_vols_data_monetness = get_call_put_impliedVols_moneyness(evalDate,curve,daycounter,calendar,maxVol=1.0,step=0.0001,precision=0.001,show=False)
#strikes_op_m,call_volatilities_op_m,put_volatilities_op_m =get_iv_plot_data(cal_vols_data_moneyness, put_vols_data_monetness)


strikes_op,call_volatilities_op,put_volatilities_op =get_iv_plot_data_PCPRate(cal_vols_data, put_vols_data)
f, axarr = plt.subplots(nrows=2, ncols=2, figsize=(6, 6), sharey=True)
print(strikes_op)
index = 0
line1, = axarr[0,0].plot(strikes_op.get(index), call_volatilities_op.get(index),color = pu.c1,marker = "*",linestyle = pu.l1,linewidth = 2,label="call iv")
line2, = axarr[0,0].plot(strikes_op.get(index), put_volatilities_op.get(index),color = pu.c2,marker = "*",linestyle = pu.l2,linewidth = 2,label="put iv")
index = 1
line2_1, = axarr[0,1].plot(strikes_op.get(index), call_volatilities_op.get(index),color = pu.c1,marker = "*",linestyle = pu.l1,linewidth = 2,label="call iv")
line2_2, = axarr[0,1].plot(strikes_op.get(index), put_volatilities_op.get(index),color = pu.c2,marker = "*",linestyle = pu.l2,linewidth = 2,label="put iv")
index = 2
line3_1, = axarr[1,0].plot(strikes_op.get(index), call_volatilities_op.get(index),color = pu.c1,marker = "*",linestyle = pu.l1,linewidth = 2,label="call iv")
line3_2, = axarr[1,0].plot(strikes_op.get(index), put_volatilities_op.get(index),color = pu.c2,marker = "*",linestyle = pu.l2,linewidth = 2,label="put iv")
index = 3
line4_1, = axarr[1,1].plot(strikes_op.get(index), call_volatilities_op.get(index),color = pu.c1,marker = "*",linestyle = pu.l1,linewidth = 2,label="call iv")
line4_2, = axarr[1,1].plot(strikes_op.get(index), put_volatilities_op.get(index),color = pu.c2,marker = "*",linestyle = pu.l2,linewidth = 2,label="put iv")

axarr[0,0].set_title("IV this month contracts")
axarr[0,1].set_title("IV next month contracts")
axarr[1,0].set_title("IV this season contracts")
axarr[1,1].set_title("IV next month contracts")
axarr[0,0].legend()
axarr[0,1].legend()
axarr[1,0].legend()
axarr[1,1].legend()


f_m, axarr_m = plt.subplots(nrows=2, ncols=2, figsize=(6, 6), sharey=True)
index = 0
axarr_m[0,0].plot(strikes_op_m.get(index), call_volatilities_op_m.get(index),color = pu.c1,marker = "*",linestyle = pu.l1,linewidth = 2,label="call iv")
axarr_m[0,0].plot(strikes_op_m.get(index), put_volatilities_op_m.get(index),color = pu.c2,marker = "*",linestyle = pu.l2,linewidth = 2,label="put iv")
index = 1
axarr_m[0,1].plot(strikes_op_m.get(index), call_volatilities_op_m.get(index),color = pu.c1,marker = "*",linestyle = pu.l1,linewidth = 2,label="call iv")
axarr_m[0,1].plot(strikes_op_m.get(index), put_volatilities_op_m.get(index),color = pu.c2,marker = "*",linestyle = pu.l2,linewidth = 2,label="put iv")
index = 2
axarr_m[1,0].plot(strikes_op_m.get(index), call_volatilities_op_m.get(index),color = pu.c1,marker = "*",linestyle = pu.l1,linewidth = 2,label="call iv")
axarr_m[1,0].plot(strikes_op_m.get(index), put_volatilities_op_m.get(index),color = pu.c2,marker = "*",linestyle = pu.l2,linewidth = 2,label="put iv")
index = 3
axarr_m[1,1].plot(strikes_op_m.get(index), call_volatilities_op_m.get(index),color = pu.c1,marker = "*",linestyle = pu.l1,linewidth = 2,label="call iv")
axarr_m[1,1].plot(strikes_op_m.get(index), put_volatilities_op_m.get(index),color = pu.c2,marker = "*",linestyle = pu.l2,linewidth = 2,label="put iv")

axarr_m[0,0].set_title("IV this month contracts")
axarr_m[0,1].set_title("IV next month contracts")
axarr_m[1,0].set_title("IV this season contracts")
axarr_m[1,1].set_title("IV next season contracts")
axarr_m[0,0].legend()
axarr_m[0,1].legend()
axarr_m[1,0].legend()
axarr_m[1,1].legend()


plt.draw()
plt.show()

#### ADD moneyness plot