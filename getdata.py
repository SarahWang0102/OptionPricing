from WindPy import *
w.start()
options = w.wset("optioncontractbasicinfo", "exchange=sse;windcode=510050.SH;status=all")
optionFlds = options.Fields
optionData = options.Data
# 50ETF market price data
mkt = w.wset("optiondailyquotationstastics",
             "startdate=2017-06-12;enddate=2017-06-12;exchange=sse;windcode=510050.SH;field=date,option_code,option_name,amount,pre_settle,open,highest,lowest,close,settlement_price")
mktFlds = mkt.Fields
mktData = mkt.Data

underlying = w.wsd("510050.SH", "close,settle", "2017-06-12", "2017-06-12", "")
spot = underlying.Data[0][0]

curve = w.wsd("SHIBORON.IR,DR001.IB,DR007.IB,DR014.IB,DR021.IB,DR1M.IB,DR2M.IB,DR3M.IB,DR4M.IB,DR6M.IB,DR9M.IB,DR1Y.IB",
             "ytm_b", "2017-06-12", "2017-06-12", "returnType=1")

print('options : ',options)
print('optionFlds : ',optionFlds)
print('optionData : ',optionData )
print('mktFlds : ',mktFlds)
print('mktData : ' , mktData)
print('curveData : ' ,curve.Data[0])
print('spot : ',spot)
