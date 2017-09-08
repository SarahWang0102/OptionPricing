import numpy as np
import math
import QuantLib as ql

# down-and-out barrier call is worthless unless its minimum remains above some “low barrier” H.
def down_out_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
    a, b, rho, m, sigma = parames
    npv_paths = []
    path_container = []
    knock_out_times = 0
    for nbr_path in range(simulation_no):
        npv = 0.0
        path = []
        evalDate = begDate
        St = S0
        I = True
        nbr_date = 0
        while evalDate <= maturityDate:
            e = noise.item(nbr_path,nbr_date)
            #print(nbr_path,' : ',noise)
            ttm = daycounter.yearFraction(evalDate, maturityDate)
            Ft = St * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
            St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
            path.append(St)
            if St < barrier: I = False # down and our
            evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
            nbr_date += 1
        ttm = daycounter.yearFraction(begDate,maturityDate)
        if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
        npv_paths.append(npv)
        path_container.append(path)
        if I==False : knock_out_times += 1
    price = np.sum(npv_paths)/simulation_no
    #print('Option price is :', price)
    #print(barrier, ' : ',knock_out_times)
    return price,path_container,knock_out_times

# down-and-in barrier is a normal European call with strike K, if its minimum went below some “low barrier” H.
def down_in_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
    a, b, rho, m, sigma = parames
    npv_paths = []
    path_container = []
    knock_in_times = 0
    for nbr_path in range(simulation_no):
        npv = 0.0
        path = []
        evalDate = begDate
        St = S0
        I = False
        nbr_date = 0
        while evalDate <= maturityDate:
            e = noise.item(nbr_path,nbr_date)
            ttm = daycounter.yearFraction(evalDate, maturityDate)
            Ft = St * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
            St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
            path.append(St)
            if St <= barrier: I = True # down and in
            evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
            nbr_date += 1
        ttm = daycounter.yearFraction(begDate,maturityDate)
        if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
        npv_paths.append(npv)
        path_container.append(path)
        if I==True : knock_in_times += 1
    price = np.sum(npv_paths)/simulation_no
    print('Option price is :', price)
    print(barrier, ' : ',knock_in_times)
    return price,path_container,knock_in_times

# up-and-in barrier is worthless unless its maximum crossed some “high barrier” H
def up_in_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
    a, b, rho, m, sigma = parames
    npv_paths = []
    path_container = []
    knock_in_times = 0
    for nbr_path in range(simulation_no):
        npv = 0.0
        path = []
        evalDate = begDate
        St = S0
        I = False
        nbr_date = 0
        while evalDate <= maturityDate:
            e = noise.item(nbr_path,nbr_date)
            ttm = daycounter.yearFraction(evalDate, maturityDate)
            Ft = St * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
            St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
            path.append(St)
            if St >= barrier: I = True # up and in
            evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
            nbr_date += 1
        ttm = daycounter.yearFraction(begDate,maturityDate)
        if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
        npv_paths.append(npv)
        path_container.append(path)
        if I==True : knock_in_times += 1
    price = np.sum(npv_paths)/simulation_no
    print('Option price is :', price)
    print(barrier, ' : ',knock_in_times)
    return price,path_container,knock_in_times

# up-and-out barrier is worthless unless its maximum remains below some “high barrier” H
def up_out_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
    a, b, rho, m, sigma = parames
    npv_paths = []
    path_container = []
    knock_out_times = 0
    for nbr_path in range(simulation_no):
        npv = 0.0
        path = []
        evalDate = begDate
        St = S0
        I = True
        nbr_date = 0
        while evalDate <= maturityDate:
            e = noise.item(nbr_path,nbr_date)
            ttm = daycounter.yearFraction(evalDate, maturityDate)
            Ft = St * math.exp(rf*ttm)
            moneyness = math.log(strike/Ft, math.e)
            vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
            St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
            path.append(St)
            if St > barrier: I = False # down and out
            evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
            nbr_date += 1
        ttm = daycounter.yearFraction(begDate,maturityDate)
        if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
        npv_paths.append(npv)
        path_container.append(path)
        if I==False : knock_out_times += 1
    price = np.sum(npv_paths)/simulation_no
    #print('Option price is :', price)
    #print(barrier, ' : ',knock_out_times)
    return price,path_container,knock_out_times

def barrier_npv_ql(evalDate,hist_spots,barrierType, barrier, payoff, exercise,process):
    ql.Settings.instance().evaluationDate = evalDate
    barrier_engine = ql.AnalyticBarrierEngine(process)
    european_engine = ql.AnalyticEuropeanEngine(process)
    # check if hist_spots hit the barrier
    if len(hist_spots) == 0:
        option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
        option.setPricingEngine(barrier_engine)
        try:
            option_price = option.NPV()
        except:
            return 0.0
    else:
        if barrierType == ql.Barrier.DownOut:
            if min(hist_spots) < barrier :
                return 0.0
            else:
                option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
                option.setPricingEngine(barrier_engine)
                try:
                    option_price = option.NPV()
                except:
                    return 0.0
        elif barrierType == ql.Barrier.UpOut:
            if max(hist_spots) > barrier:
                return 0.0
            else:
                option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
                option.setPricingEngine(barrier_engine)
                try:
                    option_price = option.NPV()
                except:
                    return 0.0
        elif barrierType == ql.Barrier.DownIn:
            if min(hist_spots)>barrier:
                option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
                option.setPricingEngine(barrier_engine)
                try:
                    option_price = option.NPV()
                except:
                    return 0.0
            else:
                option = ql.EuropeanOption(payoff, exercise)
                option.setPricingEngine(european_engine)
                option_price =  option.NPV()
        else:
            if max(hist_spots) < barrier:
                option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
                option.setPricingEngine(barrier_engine)
                try:
                    option_price = option.NPV()
                except:
                    return 0.0
            else:
                option = ql.EuropeanOption(payoff, exercise)
                option.setPricingEngine(european_engine)
                option_price = option.NPV()
    if math.isnan(option_price):
        return 0.0
    else:
        return option_price
