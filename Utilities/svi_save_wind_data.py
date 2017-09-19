from WindPy import w
import pandas as pd
import os
import QuantLib as ql
import numpy as np

def save_optionsinfo(evalDate):
    # 50ETF currently trading contracts
    optioncontractbasicinfo = w.wset("optioncontractbasicinfo",
                                     "exchange=sse;windcode=510050.SH;status=all;field=wind_"
                                     "code,call_or_put,exercise_price,exercise_date")
    df_option   = pd.DataFrame(data=optioncontractbasicinfo.Data, index=optioncontractbasicinfo.Fields)
    df_option.to_json(os.path.abspath('..') + '\marketdata\optioncontractbasicinfo' + '.json')
    return optioncontractbasicinfo.ErrorCode

def save_optionsinfo_m(evalDate):
    # 豆粕
    optioncontractbasicinfo = w.wset("optionfuturescontractbasicinfo",
                                     "exchange=DCE;productcode=M;contract=all;"
                                     "field=wind_code,call_or_put,expire_date")
    df_option   = pd.DataFrame(data=optioncontractbasicinfo.Data, index=optioncontractbasicinfo.Fields)
    df_option.to_json(os.path.abspath('..') + '\marketdata\optioncontractbasicinfo_m' + '.json')
    return optioncontractbasicinfo.ErrorCode


def save_optionmkt(evalDate):
    # 50ETF market price data
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    query       = "startdate="+datestr+";enddate="+datestr+\
                  ";exchange=sse;windcode=510050.SH;field=date,option_code," \
                  "option_name,amount,pre_settle,open,highest,lowest,close,settlement_price"
    optionmkt   = w.wset("optiondailyquotationstastics",query)
    df          = pd.DataFrame(data=optionmkt.Data,index=optionmkt.Fields)
    df.to_json(os.path.abspath('..') + '\marketdata\optionmkt_' + datestr + '.json')
    return optionmkt.ErrorCode

def save_optionmkt_m(evalDate):
    # 50ETF market price data
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    query       = "startdate="+datestr+";enddate="+datestr+\
                  ";exchange=sse;windcode=510050.SH;field=date,option_code," \
                  "option_name,amount,pre_settle,open,highest,lowest,close,settlement_price"
    optionmkt   = w.wset("optiondailyquotationstastics",query)
    df          = pd.DataFrame(data=optionmkt.Data,index=optionmkt.Fields)
    df.to_json(os.path.abspath('..') + '\marketdata\optionmkt_' + datestr + '.json')
    return optionmkt.ErrorCode

def save_curve_treasury_bond(evalDate,daycounter):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    curvedata = w.wsd("DR001.IB,CGB1M.WI,CGB3M.WI,CGB6M.WI,CGB9M.WI,CGB1Y.WI",
                     "ytm_b", datestr, datestr, "returnType=1")
    df          = pd.DataFrame(data = curvedata.Data,index=curvedata.Fields)
    df.to_json(os.path.abspath('..') + '\marketdata\curvedata_tb_' + datestr + '.json')
    return curvedata.ErrorCode


def save_underlying_ts(evalDate,endDate):
    evalDate_str    = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    endDate_str     = str(endDate.year()) + "-" + str(endDate.month()) + "-" + str(endDate.dayOfMonth())
    underlyingdata  = w.wsd("510050.SH", "close", evalDate_str, endDate_str, "Fill=Previous;PriceAdj=F")
    df              = pd.DataFrame(data=underlyingdata.Data[0], index=underlyingdata.Times)
    df.to_json(os.path.abspath('..') + '\marketdata\spotclose' + '.json')
    return underlyingdata.ErrorCode

def save_ts_data(evalDate,endDate,daycounter,calendar):
    while(evalDate < endDate):
        evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
        datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
        try:
            optioncontractbasicinfo = pd.read_json(os.path.abspath('..') + '\marketdata\optioncontractbasicinfo' + '.json')
        except:
            save_optionsinfo(evalDate)
        try:
            optionmkt = pd.read_json(os.path.abspath('..')+ '\marketdata\optionmkt_' + datestr + '.json')
        except:
            save_optionmkt(evalDate)
        try:
            curvedata = pd.read_json(os.path.abspath('..') + '\marketdata\curvedata_tb_' + datestr + '.json')
        except:
            save_curve_treasury_bond(evalDate,daycounter)

'''
w.start()
#save_underlying_ts(ql.Date(1,1,2015),ql.Date(20,7,2017))
#spot = pd.read_pickle(os.getcwd()+'\marketdata\spotclose' +'.pkl')
#print(spot)
begDate = ql.Date(1, 1, 2015)
#begDate = ql.Date(10, 7, 2017)
endDate = ql.Date(20, 7, 2017)
calendar = ql.China()
daycounter = ql.ActualActual()
evalDate = begDate

while evalDate <= endDate:
    evalDate = calendar.advance(evalDate, ql.Period(1, ql.Days))
    print(evalDate)
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    #print(os.getcwd())

    try:
        optionmkt = pd.read_json(os.getcwd() + '\marketdata\optionmkt_' + datestr + '.json')
    except :
        save_optionmkt(evalDate)
        optionmkt = pd.read_json(os.getcwd() + '\marketdata\optionmkt_' + datestr + '.json')

    #print(optionmkt.index)
    #print(optionmkt.values)


    try:
        optioncontractbasicinfo = pd.read_json(os.getcwd() +'\marketdata\optioncontractbasicinfo' + '.json')
    except:
        save_optionsinfo(evalDate)
        optioncontractbasicinfo = pd.read_json(os.getcwd() +'\marketdata\optioncontractbasicinfo' + '.json')

    try:
        curvedata = pd.read_json(os.getcwd() +'\marketdata\curvedata_tb_' + datestr + '.json')
    except :
        save_curve_treasury_bond(evalDate,daycounter)
        curvedata = pd.read_json(os.getcwd() +'\marketdata\curvedata_tb_' + datestr + '.json')
    #rates = curvedata.values[0]
    #print(rates)
    #krates = np.divide(rates, 100)
    #print(krates)
'''