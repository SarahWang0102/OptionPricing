import QuantLib as ql
import numpy as np
# Calibration Helper Methods
def setup_helpers(engine,expiration_dates,strikes,data,ref_date,spot,yield_ts,dividend_ts,calendar):
    heston_helpers = []
    grid_data = []
    for i, date in enumerate(expiration_dates):
        for j,strike in enumerate(strikes):
            t_days = date - ref_date
            period = ql.Period(t_days,ql.Days)
            vol = data[i][j]
            helper = ql.HestonModelHelper(
                period,calendar,spot,strike,ql.QuoteHandle(ql.SimpleQuote(vol)),
                yield_ts,dividend_ts)
            helper.setPricingEngine(engine)
            heston_helpers.append(helper)
            grid_data.append((date, strike))
    return heston_helpers,grid_data

def cost_function_generator(model,helpers,norm = False):
    def cost_function(params):
        params_ = ql.Array(list(params))
        model.setParams(params_)
        error = [h.calibrationError() for h in helpers]
        if norm:
            return  np.sqrt(np.sum(np.abs(error)))
        else:
            return error
    return cost_function

def calibration_report(helpers,grid_data,detailed=False):
    avg = 0.0
    if detailed:
        print( "%15s %25s %15s %15s %20s" % (
            "Strikes", "Expiry", "Market Value",
             "Model Value", "Relative Error (%)"))
        print("="*100)
    for i,opt in enumerate(helpers):
        modelvalue = opt.modelValue()
        marketvalue = opt.marketValue()
        err = 100.0 * (opt.modelValue()/marketvalue - 1.0)
        date,strike = grid_data[i]
        if detailed:
            print("%15.2f %25s %14.5f %15.5f %20.7f " % (
                strike, str(date), marketvalue,
                opt.modelValue(), err))
        avg += abs(err)
    avg = avg/len(helpers)
    if detailed: print("-"*100)
    summary = "Average Abs Error (%%) : %5.9f" % (avg)
    print(summary)
    return avg

def setup_model(_yield_ts,_dividend_ts,_spot,init_condition=(0.02,0.2,0.5,0.1,0.01)):
    theta,kappa,sigma,rho,v0 = init_condition
    process = ql.HestonProcess(_yield_ts,_dividend_ts,ql.QuoteHandle(ql.SimpleQuote(_spot)),
                               v0,kappa,theta,sigma,rho)
    model = ql.HestonModel(process)
    engine = ql.AnalyticHestonEngine(model)
    return model,engine