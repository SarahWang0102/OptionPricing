import requests
import json

# dailiy data
dailydata_url = url="http://www.shfe.com.cn/data/dailydata/kx/kx20171101.dat"
dailydata_res = requests.get(dailydata_url)
dailydata_kx = dailydata_res.text
# print dailydata_kx
dailydata_kx_dict = json.loads(dailydata_kx)
# print dailydata_kx_dict.keys()

# daily holding pm
pm_url = "http://www.shfe.com.cn/data/dailydata/kx/pm20171101.dat"
print(dailydata_kx_dict.get('o_curinstrument')[0].keys())
pm_res = requests.get(pm_url)
pm_kx = pm_res.text
# print dailydata_kx
pm_kx_dict = json.loads(pm_kx)
print(pm_kx_dict.keys())
# Rank data is located in  pm.kx_dict['o_cursor']
