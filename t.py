import pandas as pd
import os
import QuantLib as ql
import datetime
from Utilities import svi_prepare_vol_data as vol_data

calendar = ql.China()
evalDate = ql.Date(19,7,2017)
datestr = str(evalDate.year()) + "-" + str(evalDate.month()) + "-" + str(evalDate.dayOfMonth())
optionmkt = pd.read_json('marketdata\m_mkt_' + datestr + '.json')
mktFlds = optionmkt.index.tolist()
mktData = optionmkt.values.tolist()

optionids = mktData[mktFlds.index('合约名称')]
underlyingIds = []
for i, id in enumerate(optionids):
    index = id.index('-')
    id_sh = id[1:index]
    if id_sh not in underlyingIds:
        underlyingIds.append(id_sh)
spotmkt = pd.read_json('marketdata\m_future_mkt_' + datestr + '.json')
spotFlds = spotmkt.index.tolist()
spotData = spotmkt.values.tolist()
spot_ids = spotData[spotFlds.index('交割月份')]
close_prices = spotData[spotFlds.index('收盘价')]
underlying_prices = {}
for spotId in underlyingIds:
    p =  close_prices[spot_ids.index(spotId)]
    p = float(p.replace(',',''))
    underlying_prices.update({spotId:p})
contract_months = underlying_prices.keys()

maturity_dates = []
for c in contract_months:
    year = '20' + c[0: 2]
    month = c[2:4]
    date = ql.Date(1,int(month),int(year))
    maturity_date = calendar.advance(calendar.advance(date,ql.Period(-1,ql.Months)), ql.Period(4, ql.Days))
    maturity_dates.append(maturity_date)

orgnised_data = {}
for idx in range(len(mktData[0])):
    data = []
    id = mktData[mktFlds.index('合约名称')][idx]
    close = mktData[mktFlds.index('收盘价')][idx]
    volume = mktData[mktFlds.index('成交额')][idx]
    strike = id[-4:len(id)]
    data.append(int(strike))
    data.append(float(close))
    data.append(float(volume))
    data.append(id[id.index('-')+1])

    orgnised_data.update({id:data})

results_call = {}
results_put = {}
for idx,key in enumerate(orgnised_data):
    data = orgnised_data.get(key)
    c = key[1:key.index('-')]
    year = '20' + c[0: 2]
    month = c[2:4]
    date = ql.Date(1, int(month), int(year))
    mdate = calendar.advance(calendar.advance(date, ql.Period(-1, ql.Months)), ql.Period(4, ql.Days))
    print(mdate)
    if data[3] == 'C':
        if mdate not in results_call:
            results_call.update({mdate:[{key:data}]})
        else:
            results_call.get(mdate).append({key:data})
    else:
        if mdate not in results_put:
            results_put.update({mdate:[{key:data}]})
        else:
            results_put.get(mdate).append({key:data})
print('results_call')
print(results_call)

print(mktFlds)
print(underlying_prices)











