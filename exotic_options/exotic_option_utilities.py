from pricing_options.OptionEngine import OptionEngine
import numpy as np
import math
import QuantLib as ql


# def calculate_matrics(evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
#                       black_var_surface,const_vol, engineType,barrier,strike):
#     ttm = daycounter.yearFraction(begDate, maturitydt)
#     # if abs(barrier - spot) < 0.02*spot or abs(strike - spot) < 0.02*spot:
#     if abs(barrier - spot) < 0.02*spot :
#         # print('m')
#         svi_vol = black_var_surface.blackVol(ttm, daily_close)*math.sqrt(daycounter.yearFraction(begDate, maturitydt))
#     else:
#         svi_vol = black_var_surface.blackVol(ttm, daily_close)
#     price_svi, delta_svi = exotic_util.calculate_barrier_price_vol(
#         evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
#         svi_vol, engineType)
#     price_bs, delta_bs = exotic_util.calculate_barrier_price_vol(
#         evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, daily_close,
#         const_vol, engineType)
#     return price_svi, delta_svi,price_bs,delta_bs,svi_vol

def calculate_matrics_MAVol(evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
                            black_var_surfaces, const_vol, engineType, ttm):
    optionType = optionBarrierEuropean.optionType
    barrier = optionBarrierEuropean.barrier
    barrier_type = optionBarrierEuropean.barrierType
    # svi_vols = []
    svi_vol = 0.0
    cont = 0
    for black_var_surface in black_var_surfaces:
        vol = black_var_surface.blackVol(ttm, spot)
        if vol > 0.0:
            svi_vol += vol
            cont += 1
    # svi_vol = sum(svi_vols)/len(svi_vols)
    if cont > 0: svi_vol = svi_vol / cont
    else:
        svi_vol = 0.1
        print(evaluation.evalDate,' no svi vol ')

    if not const_vol > 0.0:
        print('const vol : ',const_vol)
        const_vol = 0.1

    if optionType == ql.Option.Call and barrier_type == ql.Barrier.UpOut:
        # if barrier - spot < 0.01 * barrier and ttm < 7.0 / 365:
        if spot < barrier and spot > barrier * 0.99 and ttm < 7.0 / 365:
            spot = barrier * 0.99
            # print('spot ~ ',spot)
    # elif barrier_type == ql.Barrier.DownOut:
    #     if spot < barrier*1.01 and spot > barrier:
    #         spot = barrier*1.01
    #         print('spot ~ ',spot)
    # elif optionType == ql.Option.Call and barrier_type == ql.Barrier.UpIn:
    #     if spot < barrier and spot > barrier * 0.99 and ttm < 7.0 / 365:
    #         spot = barrier * 0.99
            # print('spot ~ ',spot)
    elif optionType == ql.Option.Put and barrier_type == ql.Barrier.DownOut:
        if spot > barrier and spot < barrier * 1.01 and ttm < 7.0 / 365:
            spot = barrier * 1.01
            # print('spot ~ ',spot)
    # elif optionType == ql.Option.Put and barrier_type == ql.Barrier.DownIn:
    #     if spot > barrier and spot < barrier * 1.01 and ttm < 7.0 / 365:
    #         spot = barrier * 1.01
            # print('spot ~ ',spot)
    price_svi, delta_svi = calculate_barrier_price_vol(
        evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
        svi_vol, engineType)
    price_bs, delta_bs = calculate_barrier_price_vol(
        evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
        const_vol, engineType)
    # delta_svi = max(delta_svi,0.3)
    # delta_svi = max(delta_svi,0.25)
    # print('m')
    # delta_svi = max(0.0,delta_svi)
    # delta_bs = max(0.0,delta_bs)

    return price_svi, delta_svi, price_bs, delta_bs, svi_vol



def calculate_matrics(evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
                      black_var_surface, const_vol, engineType, ttm):
    optionType = optionBarrierEuropean.optionType
    barrier = optionBarrierEuropean.barrier
    # strike = optionBarrierEuropean.strike
    barrier_type = optionBarrierEuropean.barrierType
    svi_vol = black_var_surface.blackVol(ttm, spot)
    if not svi_vol > 0.0:
        # print(evaluation.evalDate,svi_vol)
        svi_vol = const_vol
    if not const_vol > 0.0:
        print('const vol : ',const_vol)
        const_vol = 0.05

    if optionType == ql.Option.Call and barrier_type == ql.Barrier.UpOut:
        # if barrier - spot < 0.01 * barrier and ttm < 7.0 / 365:
        if spot < barrier and spot > barrier * 0.99 and ttm < 7.0 / 365:
            spot = barrier * 0.99
            # print('spot ~ ',spot)
    # elif barrier_type == ql.Barrier.DownOut:
    #     if spot < barrier*1.01 and spot > barrier:
    #         spot = barrier*1.01
    #         print('spot ~ ',spot)
    # elif optionType == ql.Option.Call and barrier_type == ql.Barrier.UpIn:
    #     if spot < barrier and spot > barrier * 0.99 and ttm < 7.0 / 365:
    #         spot = barrier * 0.99
            # print('spot ~ ',spot)
    elif optionType == ql.Option.Put and barrier_type == ql.Barrier.DownOut:
        if spot > barrier and spot < barrier * 1.01 and ttm < 7.0 / 365:
            spot = barrier * 1.01
            # print('spot ~ ',spot)
    # elif optionType == ql.Option.Put and barrier_type == ql.Barrier.DownIn:
    #     if spot > barrier and spot < barrier * 1.01 and ttm < 7.0 / 365:
    #         spot = barrier * 1.01
            # print('spot ~ ',spot)
    price_svi, delta_svi = calculate_barrier_price_vol(
        evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
        svi_vol, engineType)
    price_bs, delta_bs = calculate_barrier_price_vol(
        evaluation, daycounter, calendar, optionBarrierEuropean, hist_spots, spot,
        const_vol, engineType)
    # delta_svi = max(delta_svi,0.3)
    # delta_svi = max(delta_svi,0.25)
    # print('m')
    # delta_svi = max(0.0,delta_svi)
    # delta_bs = max(0.0,delta_bs)

    return price_svi, delta_svi, price_bs, delta_bs, svi_vol


def calculate_matrics_plain(evaluation, daycounter, calendar, option, hist_spots, spot,
                            black_var_surface, const_vol, engineType, ttm):
    svi_vol = black_var_surface.blackVol(ttm, spot)
    if not svi_vol > 0.0:
        svi_vol = const_vol
    # print(svi_vol,const_vol)
    price_svi, delta_svi = calculate_plain_price_vol(evaluation, daycounter, calendar, option, hist_spots,
                                                     spot, svi_vol, engineType)
    price_bs, delta_bs = calculate_plain_price_vol(evaluation, daycounter, calendar, option, hist_spots,
                                                     spot, const_vol, engineType)
    return price_svi, delta_svi, price_bs, delta_bs, svi_vol


def calculate_hedging_positions(spot, option_price, delta, cash, fee,traded_amt,
                                last_delta=0.0, total_fees=0.0
                                ):
    tradingcost = abs(delta - last_delta) * spot * fee
    cash += - (delta - last_delta) * spot - tradingcost
    replicate = delta * spot + cash
    portfolio_net = replicate - option_price
    total_fees += -tradingcost
    # rebalance_cont += 1
    traded_amt += abs(delta - last_delta)
    # if delta < 0:
    #     if last_delta < 0:
    #         margin = (abs(delta)-abs(last_delta))*spot*0.2
    #     else:
    #         margin = abs(delta)*spot*0.2
    #     cash -= margin
    # if delta < 0: interest = abs(delta*spot)*0.2*(math.exp(r * dt)-1)
    # cash = cash * math.exp(r * dt)
    return tradingcost, cash, portfolio_net, total_fees, traded_amt


def calculate_plain_price_vol(evaluation, daycounter, calendar, option, hist_spots,
                              spot, vol, engineType):
    underlying = ql.SimpleQuote(spot)
    option_ql = option.option_ql
    process = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, vol)

    if engineType == 'BinomialEngine':
        engine = ql.BinomialVanillaEngine(process, 'crr', 400)
    else:
        engine = ql.AnalyticEuropeanEngine(process)
    option_ql.setPricingEngine(engine)
    option_price = option_ql.NPV()
    option_delta = option_ql.delta()
    return option_price, option_delta


def calculate_barrier_price_vol(evaluation, daycounter, calendar, barrier_option, hist_spots,
                                spot, vol, engineType):

    evalDate = evaluation.evalDate
    ql.Settings.instance().evaluationDate = evalDate
    maturitydt = barrier_option.maturitydt
    optiontype = barrier_option.optionType
    strike = barrier_option.strike
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
            if min(hist_spots) <= barrier or spot <= barrier:
                barrier_engine = None
                european_engine = None
                return 0.0, 0.0
            else:
                if evalDate < maturitydt:
                    option_price = barrier_ql.NPV()
                    # option_delta = barrier_ql.delta()
                    option_delta = calculate_effective_delta(
                        evaluation, daycounter, calendar, barrier_option, spot, vol)
                else:
                    if optiontype == ql.Option.Call: option_price = max(0.0,spot-strike)
                    else: option_price = max(0.0,strike-spot)
                    option_delta = 0.0

        elif barrierType == ql.Barrier.UpOut:
            if max(hist_spots) >= barrier or spot >= barrier:
                barrier_engine = None
                european_engine = None
                return 0.0, 0.0
            else:
                if evalDate < maturitydt:
                    option_price = barrier_ql.NPV()
                    # option_delta = barrier_ql.delta()
                    option_delta = calculate_effective_delta(
                        evaluation, daycounter, calendar, barrier_option, spot, vol)
                else:
                    if optiontype == ql.Option.Call: option_price = max(0.0,spot-strike)
                    else: option_price = max(0.0,strike-spot)
                    option_delta = 0.0
        elif barrierType == ql.Barrier.DownIn:
            if min(hist_spots) <= barrier or spot <= barrier:
                # print('touched barrier')
                if evalDate < maturitydt:
                    option_delta = option_ql.delta()
                    option_price = option_ql.NPV()
                else:
                    if optiontype == ql.Option.Call: option_price = max(0.0,spot-strike)
                    else: option_price = max(0.0,strike-spot)
                    option_delta = 0.0
            else:
                option_price = barrier_ql.NPV()
                # option_delta = barrier_ql.delta()
                option_delta = calculate_effective_delta(
                    evaluation, daycounter, calendar, barrier_option, spot, vol)
                # if min(hist_spots) > barrier and spot > barrier:
                #     option_price = barrier_ql.NPV()
                #     # option_delta = barrier_ql.delta()
                #     option_delta = calculate_effective_delta(
                #         evaluation, daycounter, calendar, barrier_option, spot, vol)
                # else:
                #     option_price =  option_ql.NPV()
                #     option_delta = option_ql.delta()
        else:
            if max(hist_spots) >= barrier or spot >= barrier:
                if evalDate < maturitydt:
                    option_delta = option_ql.delta()
                    option_price = option_ql.NPV()
                else:
                    if optiontype == ql.Option.Call: option_price = max(0.0,spot-strike)
                    else: option_price = max(0.0,strike-spot)
                    option_delta = 0.0
            else:
                option_price = barrier_ql.NPV()
                # option_delta = barrier_ql.delta()
                option_delta = calculate_effective_delta(
                    evaluation, daycounter, calendar, barrier_option, spot, vol)
                # if max(hist_spots) < barrier and spot < barrier:
                #     option_price = barrier_ql.NPV()
                #     # option_delta = barrier_ql.delta()
                #     option_delta = calculate_effective_delta(
                #         evaluation, daycounter, calendar, barrier_option, spot, vol)
                # else:
                #     option_price = option_ql.NPV()
                #     option_delta = option_ql.delta()
    barrier_engine = None
    european_engine = None
    barrier_ql = None
    option_ql = None
    if math.isnan(option_price):
        return 0.0, 0.0
    else:
        return option_price, option_delta


def calculate_barrier_price_vol_binomial(evaluation, daycounter, calendar, barrier_option, hist_spots,
                                         spot, vol, engineType):
    ql.Settings.instance().evaluationDate = evaluation.evalDate
    underlying = ql.SimpleQuote(spot)
    barrier = barrier_option.barrier
    barrierType = barrier_option.barrierType
    barrier_ql = barrier_option.option_ql
    exercise = barrier_option.exercise
    payoff = barrier_option.payoff
    process = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, underlying, vol)
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
            if min(hist_spots) <= barrier:
                barrier_engine = None
                european_engine = None
                return 0.0, 0.0
            else:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
        elif barrierType == ql.Barrier.UpOut:
            if max(hist_spots) >= barrier:
                barrier_engine = None
                european_engine = None
                return 0.0, 0.0
            else:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
        elif barrierType == ql.Barrier.DownIn:
            if min(hist_spots) > barrier:
                option_price = barrier_ql.NPV()
                option_delta = barrier_ql.delta()
            else:
                option_price = option_ql.NPV()
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
        return 0.0, 0.0
    else:
        return option_price, option_delta


def calculate_effective_delta(evaluation, daycounter, calendar, barrier_option,
                              spot, vol, dS=0.001):
    barrier_ql = barrier_option.option_ql
    process1 = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, ql.SimpleQuote(spot + dS), vol)
    process2 = evaluation.get_bsmprocess_cnstvol(daycounter, calendar, ql.SimpleQuote(spot - dS), vol)

    barrier_engine1 = ql.AnalyticBarrierEngine(process1)
    barrier_engine2 = ql.AnalyticBarrierEngine(process2)

    barrier_ql.setPricingEngine(barrier_engine1)
    option_price1 = barrier_ql.NPV()
    barrier_ql.setPricingEngine(barrier_engine2)
    option_price2 = barrier_ql.NPV()
    delta_eff = (option_price1 - option_price2) / (2 * dS)
    return delta_eff


def calculate_barrier_price(evaluation, barrier_option, hist_spots, process, engineType):
    barrier = barrier_option.barrier
    barrierType = barrier_option.barrierType
    barrier_ql = barrier_option.option_ql
    exercise = barrier_option.exercise
    payoff = barrier_option.payoff
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
    else:
        if barrierType == ql.Barrier.DownOut:
            if min(hist_spots) <= barrier:
                barrier_engine = None
                european_engine = None
                return 0.0, 0.0
            else:
                option_price = barrier_ql.NPV()
                # option_delta = barrier_ql.delta()
        elif barrierType == ql.Barrier.UpOut:
            if max(hist_spots) >= barrier:
                barrier_engine = None
                european_engine = None
                return 0.0, 0.0
            else:
                option_price = barrier_ql.NPV()
                # option_delta = barrier_ql.delta()
        elif barrierType == ql.Barrier.DownIn:
            if min(hist_spots) > barrier:
                option_price = barrier_ql.NPV()
                # option_delta = barrier_ql.delta()
            else:
                option_price = option_ql.NPV()
                # option_delta = option_ql.delta()
        else:
            if max(hist_spots) < barrier:
                option_price = barrier_ql.NPV()
                # option_delta = barrier_ql.delta()
            else:
                option_price = option_ql.NPV()
                # option_delta = option_ql.delta()
    barrier_engine = None
    european_engine = None
    barrier_ql = None
    option_ql = None
    if math.isnan(option_price):
        return 0.0
    else:
        return option_price

# # down-and-out barrier call is worthless unless its minimum remains above some “low barrier” H.
# def down_out_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
#     a, b, rho, m, sigma = parames
#     npv_paths = []
#     path_container = []
#     knock_out_times = 0
#     for nbr_path in range(simulation_no):
#         npv = 0.0
#         path = []
#         evalDate = begDate
#         St = S0
#         I = True
#         nbr_date = 0
#         while evalDate <= maturityDate:
#             e = noise.item(nbr_path,nbr_date)
#             #print(nbr_path,' : ',noise)
#             ttm = daycounter.yearFraction(evalDate, maturityDate)
#             Ft = St * math.exp(rf*ttm)
#             moneyness = math.log(strike/Ft, math.e)
#             vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
#             St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
#             path.append(St)
#             if St < barrier: I = False # down and our
#             evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
#             nbr_date += 1
#         ttm = daycounter.yearFraction(begDate,maturityDate)
#         if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
#         npv_paths.append(npv)
#         path_container.append(path)
#         if I==False : knock_out_times += 1
#     price = np.sum(npv_paths)/simulation_no
#     #print('Option price is :', price)
#     #print(barrier, ' : ',knock_out_times)
#     return price,path_container,knock_out_times
#
# # down-and-in barrier is a normal European call with strike K, if its minimum went below some “low barrier” H.
# def down_in_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
#     a, b, rho, m, sigma = parames
#     npv_paths = []
#     path_container = []
#     knock_in_times = 0
#     for nbr_path in range(simulation_no):
#         npv = 0.0
#         path = []
#         evalDate = begDate
#         St = S0
#         I = False
#         nbr_date = 0
#         while evalDate <= maturityDate:
#             e = noise.item(nbr_path,nbr_date)
#             ttm = daycounter.yearFraction(evalDate, maturityDate)
#             Ft = St * math.exp(rf*ttm)
#             moneyness = math.log(strike/Ft, math.e)
#             vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
#             St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
#             path.append(St)
#             if St <= barrier: I = True # down and in
#             evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
#             nbr_date += 1
#         ttm = daycounter.yearFraction(begDate,maturityDate)
#         if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
#         npv_paths.append(npv)
#         path_container.append(path)
#         if I==True : knock_in_times += 1
#     price = np.sum(npv_paths)/simulation_no
#     print('Option price is :', price)
#     print(barrier, ' : ',knock_in_times)
#     return price,path_container,knock_in_times
#
# # up-and-in barrier is worthless unless its maximum crossed some “high barrier” H
# def up_in_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
#     a, b, rho, m, sigma = parames
#     npv_paths = []
#     path_container = []
#     knock_in_times = 0
#     for nbr_path in range(simulation_no):
#         npv = 0.0
#         path = []
#         evalDate = begDate
#         St = S0
#         I = False
#         nbr_date = 0
#         while evalDate <= maturityDate:
#             e = noise.item(nbr_path,nbr_date)
#             ttm = daycounter.yearFraction(evalDate, maturityDate)
#             Ft = St * math.exp(rf*ttm)
#             moneyness = math.log(strike/Ft, math.e)
#             vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
#             St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
#             path.append(St)
#             if St >= barrier: I = True # up and in
#             evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
#             nbr_date += 1
#         ttm = daycounter.yearFraction(begDate,maturityDate)
#         if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
#         npv_paths.append(npv)
#         path_container.append(path)
#         if I==True : knock_in_times += 1
#     price = np.sum(npv_paths)/simulation_no
#     print('Option price is :', price)
#     print(barrier, ' : ',knock_in_times)
#     return price,path_container,knock_in_times
#
# # up-and-out barrier is worthless unless its maximum remains below some “high barrier” H
# def up_out_barrier_npv(begDate,maturityDate,daycounter,calendar,simulation_no,S0,strike,barrier,rf,delta_t,parames,noise):
#     a, b, rho, m, sigma = parames
#     npv_paths = []
#     path_container = []
#     knock_out_times = 0
#     for nbr_path in range(simulation_no):
#         npv = 0.0
#         path = []
#         evalDate = begDate
#         St = S0
#         I = True
#         nbr_date = 0
#         while evalDate <= maturityDate:
#             e = noise.item(nbr_path,nbr_date)
#             ttm = daycounter.yearFraction(evalDate, maturityDate)
#             Ft = St * math.exp(rf*ttm)
#             moneyness = math.log(strike/Ft, math.e)
#             vol_svi = np.sqrt(a+b*(rho*(moneyness-m)+np.sqrt((moneyness-m)**2+sigma**2)))
#             St = St+rf*St*delta_t+vol_svi*St*np.sqrt(delta_t)*e
#             path.append(St)
#             if St > barrier: I = False # down and out
#             evalDate = calendar.advance(evalDate,ql.Period(1,ql.Days))
#             nbr_date += 1
#         ttm = daycounter.yearFraction(begDate,maturityDate)
#         if I : npv = max(0,St-strike)*math.exp(-rf*ttm)
#         npv_paths.append(npv)
#         path_container.append(path)
#         if I==False : knock_out_times += 1
#     price = np.sum(npv_paths)/simulation_no
#     #print('Option price is :', price)
#     #print(barrier, ' : ',knock_out_times)
#     return price,path_container,knock_out_times
#
# def barrier_npv_ql(evalDate,hist_spots,barrierType, barrier, payoff, exercise,process):
#     ql.Settings.instance().evaluationDate = evalDate
#     barrier_engine = ql.AnalyticBarrierEngine(process)
#     european_engine = ql.AnalyticEuropeanEngine(process)
#     # check if hist_spots hit the barrier
#     if len(hist_spots) == 0:
#         option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
#         option.setPricingEngine(barrier_engine)
#         try:
#             option_price = option.NPV()
#         except:
#             return 0.0
#     else:
#         if barrierType == ql.Barrier.DownOut:
#             if min(hist_spots) < barrier :
#                 return 0.0
#             else:
#                 option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
#                 option.setPricingEngine(barrier_engine)
#                 try:
#                     option_price = option.NPV()
#                 except:
#                     return 0.0
#         elif barrierType == ql.Barrier.UpOut:
#             if max(hist_spots) > barrier:
#                 return 0.0
#             else:
#                 option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
#                 option.setPricingEngine(barrier_engine)
#                 try:
#                     option_price = option.NPV()
#                 except:
#                     return 0.0
#         elif barrierType == ql.Barrier.DownIn:
#             if min(hist_spots)>barrier:
#                 option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
#                 option.setPricingEngine(barrier_engine)
#                 try:
#                     option_price = option.NPV()
#                 except:
#                     return 0.0
#             else:
#                 option = ql.EuropeanOption(payoff, exercise)
#                 option.setPricingEngine(european_engine)
#                 option_price =  option.NPV()
#         else:
#             if max(hist_spots) < barrier:
#                 option = ql.BarrierOption(barrierType, barrier, 0.0, payoff, exercise)
#                 option.setPricingEngine(barrier_engine)
#                 try:
#                     option_price = option.NPV()
#                 except:
#                     return 0.0
#             else:
#                 option = ql.EuropeanOption(payoff, exercise)
#                 option.setPricingEngine(european_engine)
#                 option_price = option.NPV()
#     if math.isnan(option_price):
#         return 0.0
#     else:
#         return option_price
