import requests
import json


sh_daily_key_map = {
    'product':u'PRODUCTID',
    'delivery':u'DELIVERYMONTH',
    'amt_last_close':u'CLOSEPRICE',
    'amt_last_settlement':u'PRESETTLEMENTPRICE',
    'amt_open':u'OPENPRICE',
    'amt_high':u'HIGHESTPRICE',
    'amt_low':u'LOWESTPRICE',
    'amt_close':u'CLOSEPRICE',
    'amt_settlement':u'SETTLEMENTPRICE',
    'amt_trading_volume': u'VOLUME',
    'amt_holding_volume':  u'OPENINTEREST',
}
# dailiy data
dailydata_url = url="http://www.shfe.com.cn/data/dailydata/kx/kx20171101.dat"
dailydata_res = requests.get(dailydata_url)
dailydata_kx = dailydata_res.text
# print dailydata_kx
dailydata_kx_dict = json.loads(dailydata_kx)
print(dailydata_kx_dict['o_curinstrument'][0][sh_daily_key_map['amt_close']])

# daily holding pm
pm_url = "http://www.shfe.com.cn/data/dailydata/kx/pm20171101.dat"
pm_res = requests.get(pm_url)
pm_kx = pm_res.text
# print dailydata_kx
pm_kx_dict = json.loads(pm_kx)
print(pm_kx_dict.keys())
# Rank data is located in  pm.kx_dict['o_cursor']
