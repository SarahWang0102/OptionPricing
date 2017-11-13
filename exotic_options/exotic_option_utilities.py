from pricing_options.OptionEngine import OptionEngine
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

def calculate_barrier_price(evaluation,barrier_option,hist_spots,process,engineType):
    barrier = barrier_option.barrier
    barrierType = barrier_option.barrierType
    barrier_ql = barrier_option.option_ql
    exercise = barrier_option.exercise
    payoff = barrier_option.payoff
    barrier_engine = ql.BinomialBarrierEngine(process, 'crr', 400)
    european_engine = ql.BinomialVanillaEngine(process, 'crr', 400)
    # european_engine = ql.AnalyticEuropeanEngine(process)
    # barrier_engine = ql.AnalyticBarrierEngine(process)
    barrier_ql.setPricingEngine(barrier_engine)
    option_ql = ql.EuropeanOption(payoff, exercise)
    option_ql.setPricingEngine(european_engine)
    # check if hist_spots hit the barrier
    if len(hist_spots) == 0:
        option_price = barrier_ql.NPV()
        option_delta = barrier_ql.delta()
    else:
        if barrierType == ql.Barrier.DownOut:
            if min(hist_spots) <= barrier :
                barrier_engine = None
                european_engine = None
                return 0.0,0.0
            else:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
        elif barrierType == ql.Barrier.UpOut:
            if max(hist_spots) >= barrier:
                barrier_engine = None
                european_engine = None
                return 0.0,0.0
            else:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
        elif barrierType == ql.Barrier.DownIn:
            if min(hist_spots) > barrier:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
            else:
                option_price =  option_ql.NPV()
                option_delta = option_ql.delta()
        else:
            if max(hist_spots) < barrier:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
            else:
                option_price = option_ql.NPV()
                option_delta = option_ql.delta()
    barrier_engine = None
    european_engine = None
    barrier_ql = None
    option_ql = None
    if math.isnan(option_price):
        return 0.0,0.0
    else:
        return option_price,option_delta

def calculate_barrier_price_vol(evaluation,daycounter,calendar,barrier_option,hist_spots,
                                spot,vol,engineType):
    underlying = ql.SimpleQuote(spot)
    barrier = barrier_option.barrier
    barrierType = barrier_option.barrierType
    barrier_ql = barrier_option.option_ql
    exercise = barrier_option.exercise
    payoff = barrier_option.payoff
    process = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, vol)
    # barrier_engine = ql.BinomialBarrierEngine(process, 'crr', 400)
    # european_engine = ql.BinomialVanillaEngine(process, 'crr', 400)
    european_engine = ql.AnalyticEuropeanEngine(process)
    barrier_engine = ql.AnalyticBarrierEngine(process)
    barrier_ql.setPricingEngine(barrier_engine)
    option_ql = ql.EuropeanOption(payoff, exercise)
    option_ql.setPricingEngine(european_engine)
    # check if hist_spots hit the barrier
    if len(hist_spots) == 0:
        option_price = barrier_ql.NPV()
        # option_delta = barrier_ql.delta()
        option_delta = calculate_effective_delta(
            evaluation, daycounter, calendar, barrier_option, spot, vol)
    else:
        if barrierType == ql.Barrier.DownOut:
            if min(hist_spots) <= barrier :
                barrier_engine = None
                european_engine = None
                return 0.0,0.0
            else:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
        elif barrierType == ql.Barrier.UpOut:
            if max(hist_spots) >= barrier:
                barrier_engine = None
                european_engine = None
                return 0.0,0.0
            else:
                option_price = barrier_ql.NPV()
                # option_delta = barrier_ql.delta()
                option_delta = calculate_effective_delta(
                    evaluation,daycounter,calendar,barrier_option,spot,vol)
        elif barrierType == ql.Barrier.DownIn:
            if min(hist_spots) > barrier:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
            else:
                option_price =  option_ql.NPV()
                option_delta = option_ql.delta()
        else:
            if max(hist_spots) < barrier:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
            else:
                option_price = option_ql.NPV()
                option_delta = option_ql.delta()
    barrier_engine = None
    european_engine = None
    barrier_ql = None
    option_ql = None
    if math.isnan(option_price):
        return 0.0,0.0
    else:
        return option_price,option_delta

def calculate_effective_delta(evaluation,daycounter,calendar,barrier_option,
                                spot,vol, dS=0.0001):

    barrier = barrier_option.barrier
    barrierType = barrier_option.barrierType
    barrier_ql = barrier_option.option_ql
    exercise = barrier_option.exercise
    payoff = barrier_option.payoff
    process1 = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, ql.SimpleQuote(spot+dS), vol)
    process2 = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, ql.SimpleQuote(spot-dS), vol)

    barrier_engine1 = ql.AnalyticBarrierEngine(process1)
    barrier_engine2 = ql.AnalyticBarrierEngine(process2)

    barrier_ql.setPricingEngine(barrier_engine1)
    option_price1 = barrier_ql.NPV()
    barrier_ql.setPricingEngine(barrier_engine2)
    option_price2 = barrier_ql.NPV()
    delta_eff = (option_price1-option_price2)/(2*dS)
    return delta_eff
















