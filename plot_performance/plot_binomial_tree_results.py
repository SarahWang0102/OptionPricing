import QuantLib as ql
import matplotlib.pyplot as plt
from Utilities import plot_util as pu
maturity_date = ql.Date(15, 1, 2016)
spot_price = 127.62
strike_price = 130
volatility = 0.20 # the historical vols or implied vols
dividend_rate =  0.0163
option_type = ql.Option.Call

risk_free_rate = 0.001
day_count = ql.Actual365Fixed()
calendar = ql.UnitedStates()

calculation_date = ql.Date(8, 5, 2015)
ql.Settings.instance().evaluationDate = calculation_date
payoff = ql.PlainVanillaPayoff(option_type, strike_price)
settlement = calculation_date

am_exercise = ql.AmericanExercise(settlement, maturity_date)
american_option = ql.VanillaOption(payoff, am_exercise)

eu_exercise = ql.EuropeanExercise(maturity_date)
european_option = ql.VanillaOption(payoff, eu_exercise)
spot_handle = ql.QuoteHandle(
    ql.SimpleQuote(spot_price)
)
flat_ts = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, risk_free_rate, day_count)
)
dividend_yield = ql.YieldTermStructureHandle(
    ql.FlatForward(calculation_date, dividend_rate, day_count)
)
flat_vol_ts = ql.BlackVolTermStructureHandle(
    ql.BlackConstantVol(calculation_date, calendar, volatility, day_count)
)
bsm_process = ql.BlackScholesMertonProcess(spot_handle,
                                           dividend_yield,
                                           flat_ts,
                                           flat_vol_ts)
def binomial_price(option, bsm_process, steps):
    binomial_engine = ql.BinomialVanillaEngine(bsm_process, "crr", steps)
    option.setPricingEngine(binomial_engine)
    return option.NPV()
plt.rcParams['font.sans-serif'] = ['STKaiti']
plt.rcParams.update({'font.size': 11})
steps = range(5, 200, 1)
eu_prices = [binomial_price(european_option, bsm_process, step) for step in steps]
am_prices = [binomial_price(american_option, bsm_process, step) for step in steps]
# theoretican European option price
european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
bs_price = european_option.NPV()
f,axarr = plt.subplots()
plt.plot([5,200],[bs_price, bs_price], label="BS模型解析解", lw=2,color=pu.c1,linestyle=pu.l1)

plt.plot(steps, eu_prices, label="二叉树模型欧式期权", lw=2, alpha=0.6,color=pu.c2,linestyle=pu.l1)
plt.plot(steps, am_prices, label="二叉树模型美式期权", lw=2, alpha=0.6,color=pu.c3,linestyle=pu.l1)
axarr.spines['right'].set_visible(False)
axarr.spines['top'].set_visible(False)
# Only show ticks on the left and bottom spines
axarr.yaxis.set_ticks_position('left')
axarr.xaxis.set_ticks_position('bottom')

plt.xlabel("n")
plt.ylabel("价格")
plt.ylim(6.7,7)
#plt.title("Binomial Tree Price For Varying Steps")
plt.legend()
f.savefig('CPIV.png', dpi=300, format='png')
plt.show()

