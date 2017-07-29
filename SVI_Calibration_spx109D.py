import xlrd
import QuantLib as ql
from WindPy import *
import numpy as np
import matplotlib.pyplot as plt
import datetime
import svi_calibration_util as svi_util

###############################################################################
## Settings
w.start()
evalDate    = ql.Date(3,7,2017)
calendar    = ql.UnitedStates()
daycounter  = ql.ActualActual()
ql.Settings.instance().evaluationDate = evalDate
################################################################################
## spx 18 day market data
spx_idx  = 2429.01
book     = xlrd.open_workbook('spx109D_20170703.xlsx')
sheet    = book.sheet_by_index(0)
strikes  = []
bid_call = []
ask_call = []
vol_call = []
bid_put  = []
ask_put  = []
vol_put  = []
maturity_date = ql.Date(20,10,2017)

for i in range(3,sheet.nrows):
    if sheet.col(1)[i].value != sheet.col(15)[i].value : print('strikes are not equal!!')
    strikes.append(sheet.col(1)[i].value)
    bid_call.append(sheet.col(2)[i].value)
    ask_call.append(sheet.col(3)[i].value)
    vol_call.append(sheet.col(5)[i].value/100)
    bid_put.append(sheet.col(16)[i].value)
    ask_put.append(sheet.col(17)[i].value)
    vol_put.append(sheet.col(19)[i].value/100)

# us treasury bond yild term structure
#book_curve = xlrd.open_workbook('uscurve_20170703.xlsx')
#sheet_curve = book_curve.sheet_by_index(0)
#col_rates = sheet_curve.col(2)
#libiorData = w.wsd("LIUSDON.IR,LIUSD1W.IR,LIUSD1M.IR,LIUSD2M.IR,LIUSD3M.IR,LIUSD6M.IR,LIUSD12M.IR", "ytm_b", "2017-07-03", "2017-07-03", "returnType=3")
#rates = np.divide(libiorData.Data[0],100)
rates = np.divide( [1.17167, 1.18833, 1.22689, 1.25389, 1.30072, 1.456, 1.74844], 100)
dates = [calendar.advance(evalDate,ql.Period(1,ql.Days)),
         calendar.advance(evalDate,ql.Period(1,ql.Weeks)),
         calendar.advance(evalDate,ql.Period(1,ql.Months)),
         calendar.advance(evalDate,ql.Period(2,ql.Months)),
         calendar.advance(evalDate,ql.Period(3,ql.Months)),
         calendar.advance(evalDate,ql.Period(6,ql.Months)),
         calendar.advance(evalDate,ql.Period(1,ql.Years))]
curve  = ql.ForwardCurve(dates,rates,daycounter)
ref_date = curve.referenceDate()
max_date = curve.maxDate()
dates = np.array([datetime.date(ref_date.year(),ref_date.month(),ref_date.dayOfMonth()) + datetime.timedelta(days=i) for i in range(max_date - ref_date)])
times = np.linspace(0.0, (max_date-ref_date)/365,100)
rates = [curve.zeroRate(t,ql.Continuous).rate() for t in times]
#plt.figure(1)
#plt.plot(times,rates)
#plt.title('US treasury yts 2017/07/03')

###############################################################################
## Implement SVI model
vols = vol_call
print('vols: ',vols)
expiration_date = maturity_date
spot = spx_idx
risk_free_rate = curve.zeroRate(expiration_date,daycounter,ql.Continuous).rate()
print('rf: ',risk_free_rate)

## Calibrate parameters
method = 'nm'
## 'ols' for SLSQP method, optimizing a, d, c, m, sigma together by one objfuction;
## 'nm' for Nelder-Mead simplex method
init_adc = [1,1,1] # Never used for ols optimization
init_msigma = [1,1]
log_forward_moneyness, totalvariance,volatility, _a_star, _d_star, _c_star, m_star, sigma_star \
    = svi_util.svi_calibration_helper(method,evalDate, init_adc,init_msigma, calendar, daycounter, risk_free_rate, vols, expiration_date, strikes, spot)
x_svi  = np.arange(min(log_forward_moneyness), max(log_forward_moneyness), 0.1 / 100) # log_forward_moneyness
y_svi  = np.divide((x_svi - m_star),sigma_star)
tv_svi = _a_star + _d_star*y_svi + _c_star* np.sqrt(y_svi**2 + 1) # totalvariance objective fution values


print('_a_star, _d_star, _c_star, m_star, sigma_star: ',_a_star, _d_star, _c_star, m_star, sigma_star)
x = [_a_star, _d_star, _c_star, m_star, sigma_star]
print('x : ',x)
# Constraints: 0 <= c <=4sigma; |d| <= c and |d| <= 4sigma - c; 0 <= a <= max{vi}
if 0 <= _a_star<= max(totalvariance): print('1 bnd succeeded')
else: print('1 bnd failed')
if -4*sigma_star<= _d_star <= 4*sigma_star : print('2 bnd succeeded')
else: print('2 bnd failed')
if 0<=_c_star<=4*sigma_star: print('3 bnd succeeded')
else: print('3 bnd failed')
if x[2] - abs(x[1]) >= 0: print('1 cons succeeded')
else: print('1 cons failed')
if 4 * sigma_star - x[2] - abs(x[1]) : print('2 cons succeeded')
else: print('2 cons failed')

########################################################################################################################
## Get a,b,rho
ttm      = daycounter.yearFraction(evalDate,expiration_date)
a_star   = np.divide(_a_star, ttm)
b_star   = np.divide(_c_star, (sigma_star * ttm))
rho_star = np.divide(_d_star, _c_star)
tv_svi2  = np.multiply( a_star + b_star * (rho_star * (x_svi - m_star) + np.sqrt((x_svi - m_star) ** 2 + sigma_star ** 2)), ttm)

print('c = b`rho`t',_c_star,b_star*sigma_star*ttm)
print('d = rho*b*sigma*t',_d_star,rho_star*b_star*sigma_star*ttm)
print('_a = a*t', _a_star,a_star*ttm)
print('a_star,b_star,rho_star,m_star,sigma_star: ',a_star,b_star,rho_star,m_star,sigma_star)
########################################################################################################################
##


########################################################################################################################
# plot input data -- moneyness-imliedvol
plt.figure(2)
plt.plot(log_forward_moneyness, totalvariance, 'ro')
# Plot SVI volatility smile -- moneyness-impliedVol
plt.plot(x_svi, tv_svi, 'b--')
t = str(daycounter.yearFraction(evalDate, expiration_date))
plt.title('SVI total variance, T = ' + t)

########################################################################################################################
## Double check parameters calculation -- two lines should be exactly the same
plt.figure(3)
plt.plot(x_svi, tv_svi, 'b--')
plt.plot(x_svi, tv_svi2, 'r--')

plt.show()
