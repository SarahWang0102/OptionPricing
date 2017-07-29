from WindPy import *
import pandas as pd
import os

def save_optionsinfo(evalDate):
    # 50ETF currently trading contracts
    #datestr     = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    optioncontractbasicinfo = w.wset("optioncontractbasicinfo",
                         "exchange=sse;windcode=510050.SH;status=all;field=wind_code,call_or_put,exercise_price,exercise_date")
    df_option   = pd.DataFrame(data = optioncontractbasicinfo.Data,index=optioncontractbasicinfo.Fields)
    df_option.to_pickle(os.getcwd()+'\marketdata\optioncontractbasicinfo' + '.pkl')
    df_option.to_json(os.getcwd() + '\marketdata\optioncontractbasicinfo' + '.json')
    return optioncontractbasicinfo.ErrorCode
def save_optionmkt(evalDate):
    # 50ETF market price data
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    query       = "startdate="+ datestr +";enddate="+datestr+";exchange=sse;windcode=510050.SH;field=date,option_code,option_name,amount,pre_settle,open,highest,lowest,close,settlement_price"
    optionmkt   = w.wset("optiondailyquotationstastics",query)
    df          = pd.DataFrame(data = optionmkt.Data,index=optionmkt.Fields)
    df.to_pickle(os.getcwd()+'\marketdata\optionmkt_' + datestr+'.pkl')
    df.to_json(os.getcwd() + '\marketdata\optionmkt_' + datestr + '.json')
    return optionmkt.ErrorCode

def save_curve_treasuryBond(evalDate,daycounter):
    datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    curvedata = w.wsd("DR001.IB,CGB1M.WI,CGB3M.WI,CGB6M.WI,CGB9M.WI,CGB1Y.WI",
                     "ytm_b", datestr, datestr, "returnType=1")
    df          = pd.DataFrame(data = curvedata.Data,index=curvedata.Fields)
    df.to_pickle(os.getcwd()+'\marketdata\curvedata_tb_' + datestr+'.pkl')
    df.to_json(os.getcwd() + '\marketdata\curvedata_tb_' + datestr + '.json')
    return curvedata.ErrorCode

def save_underlying_ts(evalDate,endDate):
    evalDate_str    = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
    endDate_str     = str(endDate.year()) + "-" + str(endDate.month()) + "-" + str(endDate.dayOfMonth())
    underlyingdata  = w.wsd("510050.SH", "close", evalDate_str, endDate_str, "Fill=Previous;PriceAdj=F")
    df              = pd.DataFrame(data = underlyingdata.Data[0],index=underlyingdata.Times)
    df.to_pickle(os.getcwd()+'\marketdata\spotclose' +'.pkl')
    df.to_json(os.getcwd() + '\marketdata\spotclose' + '.json')
    return underlyingdata.ErrorCode


'''
w.start()
save_underlying_ts(ql.Date(1,1,2015),ql.Date(20,7,2017))
spot = pd.read_pickle(os.getcwd()+'\marketdata\spotclose' +'.pkl')
print(spot)



evalDate = ql.Date(18,7,2017)
daycounter = ql.ActualActual()
datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
print(os.getcwd())

try:
    optionmkt = pd.read_pickle(os.getcwd()+'\marketdata\optionmkt_' + datestr+'.pkl')
except FileNotFoundError:
    save_optionmkt(evalDate)
    optionmkt = pd.read_pickle(os.getcwd()+'\marketdata\optionmkt_' + datestr + '.pkl')

print(optionmkt.index)
print(optionmkt.values)


try:
    optioncontractbasicinfo = pd.read_pickle('optioncontractbasicinfo' + '.pkl')
except:
    save_optionsinfo(evalDate)
    optioncontractbasicinfo = pd.read_pickle('optioncontractbasicinfo' + '.pkl')

try:
    curvedata = pd.read_pickle('curvedata_tb_' + datestr + '.pkl')
except FileNotFoundError:
    save_curve_treasuryBond(evalDate,daycounter)
    curvedata = pd.read_pickle('curvedata_tb_' + datestr + '.pkl')
rates = curvedata.values[0]
print(rates)
krates = np.divide(rates, 100)
print(krates)
'''