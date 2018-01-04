#!/usr/bin/env python
# encoding: utf-8
"""
@Auther: simon
@Filename: 做空1.py
@Creation Time: 2017/05/15 17:00
@Version : Python 3.5.3
"""
"""
☆更新数据在 datasource = GetData(update=False, species='T') 中把 False 换为 True
☆双均线策略3日线上穿15日线做多，下穿做空
☆添加ADX指标进行行情过滤
☆保证金率 0.02，仓位 0.02 即无杠杆
"""

from back_test.get_data import GetData
from back_test.bkt import Bkt
import matplotlib.pyplot as plt
import datetime
import pandas as pd
import numpy as np

def strategy_boll(b1): # 策略主体

    datasource = GetData(update = False)
    datasource.add_func(func='double_moving',k1=3,k2=15) # 添加双均线
    datasource.add_func(func='adx',k1=15) # 添加adx指标
    data = datasource.data # 获取数据
    data['date'] = data.index
    data.index = range(len(data))
    # data.to_excel('data.xlsx')
    b1.start(data)
    adx = 20
    stay = 5
    while b1.n < b1.N:
        try:
            if stay == 0:
                # 如果空仓且快均线下穿慢均线，并且没更换主力合约，且ADX大于一定值，开空
                if b1.position == 0 and b1.bar['dm1'] < b1.bar['dm2'] and b1.bar['trade_hiscode'] == b1.nextbar[
                    'trade_hiscode'] and b1.lastbar['adx'] > adx:  # and b1.bar['dm2']<b1.bar['dm3']:
                    b1.short(b1.bar['vwap'])
                # 如果空仓且快均线上穿慢均线，并且没更换主力合约，且ADX大于一定值，开多
                if b1.position == 0 and b1.bar['dm1'] > b1.bar['dm2'] and b1.bar['trade_hiscode'] == b1.nextbar[
                    'trade_hiscode'] and b1.lastbar['adx'] > adx:  # and b1.bar['dm2']<b1.bar['dm3']:
                    b1.buy(b1.bar['vwap'])
                # 如果有空单，且快均线上穿慢均线，且ADX大于一定值，平空单并开多
                elif b1.position == -1 and b1.bar['dm1'] > b1.bar['dm2'] and b1.lastbar['adx'] > adx and b1.bar[
                    'trade_hiscode'] == b1.nextbar['trade_hiscode']:
                    b1.cover(b1.bar['vwap'])
                    b1.buy(b1.bar['vwap'])
                # 如果有多单，且快均线下穿慢均线，且ADX大于一定值，平多单并开空
                elif b1.position == 1 and b1.bar['dm1'] < b1.bar['dm2'] and b1.lastbar['adx'] > adx and b1.bar[
                    'trade_hiscode'] == b1.nextbar['trade_hiscode']:
                    b1.sell(b1.bar['vwap'])
                    b1.short(b1.bar['vwap'])
                # 如果有空单，且快均线上穿慢均线，但ADX小于一定值，平空单 不继续开多
                elif b1.position == -1 and b1.bar['dm1'] > b1.bar['dm2'] and b1.lastbar['adx'] < adx:
                    b1.cover(b1.bar['vwap'])
                # 如果有多单，且快均线下穿慢均线，但ADX小于一定值，平多单 不继续开空
                elif b1.position == 1 and b1.bar['dm1'] < b1.bar['dm2'] and b1.lastbar['adx'] < adx:
                    b1.sell(b1.bar['vwap'])
                elif b1.position == -1 and b1.bar['dm1'] > b1.bar['dm2'] and b1.lastbar['adx'] < adx:
                    b1.cover(b1.bar['vwap'])
                # 如果有多单，且快均线下穿慢均线，但ADX小于一定值，平多单 不继续开空
                elif b1.position == 1 and b1.bar['dm1'] < b1.bar['dm2'] and b1.lastbar['adx'] < adx:
                    b1.sell(b1.bar['vwap'])
                # 如果有空单，且更换主力合约，平仓
                elif b1.position == -1 and b1.bar['trade_hiscode'] != b1.nextbar['trade_hiscode']:
                    b1.cover(b1.bar['vwap'])
                # 如果有空单，且更换主力合约，平仓
                elif b1.position == 1 and b1.bar['trade_hiscode'] != b1.nextbar['trade_hiscode']:
                    b1.sell(b1.bar['vwap'])
                else:
                    pass
            else:
                stay-=1

        except KeyError:
            pass
        b1.clear()
    return b1

if __name__ == '__main__':
    starttime = datetime.datetime.now()
    print(' 程序运行开始! '.center(38, '*'))
    print((' 开始时间:'+str(starttime.strftime("%Y-%m-%d %H:%M:%S"))).center(40,'*'))
    # 无杠杆
    bkt = Bkt(leverage=0.02, marginrate=0.02, capital=10000000, unit_value=10000, unit=1)
    b = strategy_boll(bkt)
    b.printresult()
    b.net_value_plot(grid=True)

    endtime = datetime.datetime.now()
    print(' 程序运行结束! '.center(38,'*'))
    print((' 结束时间:'+str(endtime.strftime("%Y-%m-%d %H:%M:%S"))).center(40, '*'))
    print((' 程序运行时间：'+str((endtime - starttime).seconds)+' s ').center(37, '*'))

