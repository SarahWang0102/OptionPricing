#!/usr/bin/env python
# encoding: utf-8
"""
@Auther: simon
@Filename: get_data.py
@Creation Time: 2017/05/18 10:23
@Version : Python 3.5.3
"""

from WindPy import *
import pandas as pd
import numpy as np
import pickle


class GetTwoData(object):

    def __init__(self):
        self.price_t = pd.DataFrame()
        self.price_tf = pd.DataFrame()
        try:
            with open('data_price.pickle', 'rb') as f1:
                data = pickle.load(f1)
                self.data_t = data[0]
                self.data_tf = data[1]
                self.t_hiscode = data[2]
                self.tf_hiscode = data[3]
        except FileNotFoundError:
            self.get_price()

    def get_price(self):
        w.start()
        data_t = dict()
        data_tf = dict()
        tmp = w.wsd("T.CFE,", "trade_hiscode", "2015-05-15", "", "")
        t_hiscode = pd.DataFrame(np.array(tmp.Data).T, index=pd.Series(tmp.Times).dt.strftime('%Y-%m-%d'),
                                 columns=pd.Series(tmp.Fields).str.lower()).dropna()
        tf_hiscode = t_hiscode.copy()
        tf_hiscode.trade_hiscode = [x[0]+'F'+x[1:] for x in list(t_hiscode.trade_hiscode)]
        for t_code, tf_code in zip(sorted(list(set(t_hiscode.trade_hiscode))),
                                   sorted(list(set(tf_hiscode.trade_hiscode)))):
            # t_duration, tf_duration = [], []
            tmp_t = w.wsd(t_code, "open,high,low,close,vwap,settle,pre_settle,tbf_CTD", '2015-05-15',
                          "", "exchangeType=NIB")
            tmp_tf = w.wsd(tf_code, "open,high,low,close,vwap,settle,pre_settle,tbf_CTD", '2015-05-15',
                           "", "exchangeType=NIB")
            t_price = pd.DataFrame(np.array(tmp_t.Data).T, index=pd.Series(tmp_t.Times).dt.strftime(
                '%Y-%m-%d'), columns=pd.Series(tmp_t.Fields).str.lower()).dropna(how='all').fillna(
                method='ffill')
            print(t_code, tf_code)
            # for i in range(len(t_price)):
            #     t_duration.append(w.wsd(t_price.ix[i, 'tbf_ctd'], "duration",
            #                             list(t_price.index)[i], list(t_price.index)[i], "").Data[0][0])
            # t_price['duration'] = t_duration
            tf_price = pd.DataFrame(np.array(tmp_tf.Data).T, index=pd.Series(tmp_tf.Times).dt.strftime('%Y-%m-%d'),
                                    columns=pd.Series(tmp_tf.Fields).str.lower()).dropna(how='all').fillna(
                method='ffill')
            # for i in range(len(tf_price)):
            #     tf_duration.append(w.wsd(tf_price.ix[i, 'tbf_ctd'], "duration", list(tf_price.index)[i],
            #                              list(tf_price.index)[i], "").Data[0][0])
            # tf_price['duration'] = tf_duration
            data_t[t_code[:-4]] = t_price
            data_tf[tf_code[:-4]] = tf_price
            data_price = [data_t, data_tf, t_hiscode, tf_hiscode]
        with open('data_price.pickle', 'wb') as f0:
            pickle.dump(data_price, f0, pickle.HIGHEST_PROTOCOL)

        self.data_t = data_t
        self.data_tf = data_tf
        self.t_hiscode = t_hiscode
        self.tf_hiscode = tf_hiscode

    def get_p0(self, data1, data2):
        data1['p0'] = np.array(list(data1.vwap)[10:25]).mean()
        data2['p0'] = np.array(list(data2.vwap)[10:25]).mean()
        return [data1, data2]

    def spread1(self, data1, data2, col='close'):
        data1['spread1'] = data2[col]*7.7/4.6-data1[col]
        return data1

    def spread2(self, data1, data2, col='close'):
        data1['spread2'] = data1[col]-data2[col]
        return data1

    def donchian(self, data, n):
        if type(n) is int:
            data['high_'+str(n)] = data['high'].rolling(window=n+1).apply(lambda x: np.array(x[0:-1]).max())
            data['low_' + str(n)] = data['low'].rolling(window=n+1).apply(lambda x: np.array(x[0:-1]).min())
        elif type(n) is list:
            for i in n:
                data['high_' + str(i)] = data['high'].rolling(window=i + 1).apply(lambda x: np.array(x[0:-1]).max())
                data['low_' + str(i)] = data['low'].rolling(window=i + 1).apply(lambda x: np.array(x[0:-1]).min())
        return data


    def boll(self, data, n, m, col='spread1'):

        n_mean = data[col].rolling(window=n).apply(lambda x: np.array(x[:-1]).mean())
        n_std = data[col].rolling(window=10).apply(lambda x: np.array(x[:-1]).std())
        data['mean'] = n_mean
        data['up'] = n_mean+m*n_std
        data['down'] = n_mean-m*n_std

        return data

    def extract(self, cycle, code):

        pass

    def addfunc(self, minute=False):
        main_start1 = self.t_hiscode.drop_duplicates(subset='trade_hiscode', keep='first')
        main_start2 = self.tf_hiscode.drop_duplicates(subset='trade_hiscode', keep='first')
        main_end = self.t_hiscode.drop_duplicates(subset='trade_hiscode', keep='last')
        main_start_end = zip(main_start1.index, main_end.index)
        data_t_list = []
        data_tf_list = []
        for i, j in main_start_end:
            data_t = self.data_t[main_start1.at[i, 'trade_hiscode'][:-4]]
            data_tf = self.data_tf[main_start2.at[i, 'trade_hiscode'][:-4]]
            data_t, data_tf = self.get_p0(data_t, data_tf)
            self.data_t[main_start1.ix[i, 'trade_hiscode'][:-4]] = data_t
            self.data_tf[main_start2.ix[i, 'trade_hiscode'][:-4]] = data_tf

            data_t = self.spread1(data_t, data_tf)
            price_t = self.spread2(data_t, data_tf)
            # price_t = self.boll(price_t, 1, 1)
            price_t = price_t.ix[i:j, :].copy()
            price_tf = data_tf.ix[i:j, :].copy()
            if minute is False:
                pass
            else:
                price_t_minute = pd.read_excel(
                    'E:\\data\\15分钟K线数据\\' + main_start1.at[i, 'trade_hiscode'][:-4] + '.xlsx')
                price_t_minute.index = price_t_minute['日期']
                price_t_minute = price_t_minute.ix[i:j, :]
                price_t = pd.merge(price_t_minute, price_t, how='outer', left_on='日期', right_index=True)
                price_tf_minute = pd.read_excel(
                    'E:\\data\\15分钟K线数据\\' + main_start2.at[i, 'trade_hiscode'][:-4] + '.xlsx')
                price_tf_minute.index = price_tf_minute['日期']
                price_tf_minute = price_tf_minute.ix[i:j, :]
                price_tf = pd.merge(price_tf_minute, price_tf, how='outer', left_on='日期', right_index=True)
            data_t_list.append(price_t)
            data_tf_list.append(price_tf)
        if minute is False:

            self.price_t = pd.concat([pd.concat(data_t_list), self.t_hiscode], axis=1)
            self.price_tf = pd.concat([pd.concat(data_tf_list), self.tf_hiscode], axis=1)
            self.price_t['date'] = self.price_t.index
            self.price_tf['date'] = self.price_tf.index
        else:
            self.price_t = pd.merge(pd.concat(data_t_list), self.t_hiscode, how='outer', left_on='日期', right_index=True)
            self.price_t['date'] = self.price_t.index
            self.price_tf = pd.merge(pd.concat(data_tf_list), self.tf_hiscode, how='outer', left_on='日期', right_index=True)
            self.price_tf['date'] = self.price_tf.index
            self.price_t = self.spread(self.price_t, self.price_tf, col='开盘')


if __name__ == '__main__':

    d = GetTwoData()
    d.addfunc()
    d.price_t.to_excel('ddd1.xlsx')
    d.price_tf.to_excel('ddd2.xlsx')


class GetData(object):

    def __init__(self, update=False, species='T'):
        self.data = pd.DataFrame()
        self.species = species
        self.filename = 'data_'+self.species+'.pickle'
        if update is True:
            self.data_prime = self.get_price()
        else:
            try:
                with open(self.filename, 'rb') as f1:
                    self.data_prime = pickle.load(f1)
            except FileNotFoundError:
                self.data_prime = self.get_price()
        self.main_code, self.data_source = self.data_prime

    def get_price(self):  # 从WIND获取数据并保存
        w.start()
        dataT = dict()
        code_list0 = w.wsd(self.species+".CFE,"+self.species+"01.CFE,"+self.species+"02.CFE", "trade_hiscode", "2010-03-20", "", "").Data
        code_list1 = [x for x in code_list0[0] if x is not None]
        code_list2 = [x for x in code_list0[1] if x is not None]
        code_list3 = [x for x in code_list0[2] if x is not None]

        code_list = sorted(list(map(lambda x: x[:-4], list(set(code_list1 + code_list2 + code_list3)))))
        for code in code_list:
            tmp = w.wsd(code + '.CFE', "open,high,low,close,vwap,settle,pre_settle,volume", '2010-03-20', "")
            dataT[code] = pd.DataFrame(np.array(tmp.Data).T, index=pd.Series(tmp.Times).dt.strftime('%Y-%m-%d'),
                                       columns=pd.Series(tmp.Fields).str.lower()).dropna()
        tmp = w.wsd(self.species+'.CFE', 'trade_hiscode', '2010-03-20')
        main_code = pd.DataFrame(np.array(tmp.Data).T, index=pd.Series(tmp.Times).dt.strftime('%Y-%m-%d'),
                                 columns=pd.Series(tmp.Fields).str.lower()).dropna()
        data_T = [main_code, dataT]
        with open(self.filename, 'wb') as f0:
            pickle.dump(data_T, f0, pickle.HIGHEST_PROTOCOL)
        return data_T

    def double_moving(self, data, n1, n2, col='close'):  # 双重均线函数
        n1_mean = data[col].rolling(window=n1 + 1).apply(lambda x: np.array(x[0:-1]).mean())
        n2_mean = data[col].rolling(window=n2 + 1).apply(lambda x: np.array(x[0:-1]).mean())
        data['dm1'] = n1_mean
        data['dm2'] = n2_mean
        return data

    def three_moving(self, data, n1, n2, n3, col='close'):  # 三重均线函数
        n1_mean = data[col].rolling(window=n1 + 1).apply(lambda x: np.array(x[0:-1]).mean())
        n2_mean = data[col].rolling(window=n2 + 1).apply(lambda x: np.array(x[0:-1]).mean())
        n3_mean = data[col].rolling(window=n3 + 1).apply(lambda x: np.array(x[0:-1]).mean())
        data['dm1'] = n1_mean
        data['dm2'] = n2_mean
        data['dm3'] = n3_mean
        return data

    def hl_level(self, data, n1, n2):
        data['high_1'] = data['high'].rolling(window=n1).apply(lambda x: np.array(x).max())
        data['low_1'] = data['low'].rolling(window=n1).apply(lambda x: np.array(x).min())
        data['high_2'] = data['high'].rolling(window=n2).apply(lambda x: np.array(x).max())
        data['low_2'] = data['low'].rolling(window=n2).apply(lambda x: np.array(x).min())
        return data

    def atr(self, data, n, m):
        tr = pd.DataFrame()
        cl, high, low = data.close.rolling(window=2).apply(lambda x: x[0:-1]), data.high, data.low
        tr['h_l'] = np.abs(high - low)
        tr['h-c'] = np.abs(high - cl)
        tr['c-l'] = np.abs(cl - low)
        data['tr'] = tr.max(axis=1)
        data['atr_up'] = data.close.rolling(window=10).apply(lambda x: np.array(x[0:-1]).mean())+n*data.\
            tr.rolling(window=2).apply(lambda x: np.array(x[0:-1]).mean())
        data['atr_down'] = data.close.rolling(window=10).apply(lambda x: np.array(x[0:-1]).mean())-m*data.\
            tr.rolling(window=2).apply(lambda x: np.array(x[0:-1]).mean())
        return data

    def extreme(self, data):
        high = data.high.rolling(window=7, center=True).apply(lambda x: np.array(x).max())
        low = data.low.rolling(window=7, center=True).apply(lambda x: np.array(x).min())
        is_ex_high = [1 if x == y else 0 for x, y in zip(list(data.high), list(high))]
        is_ex_low = [-1 if x == y else 0 for x, y in zip(list(data.low), list(low))]
        data['is_ex_high'] = is_ex_high
        data['is_ex_low'] = is_ex_low
        return data

    def adx(self, data, n):
        hd = data.high - data.high.rolling(window=2).apply(lambda x: x[0:-1])
        ld = data.low.rolling(window=2).apply(lambda x: x[0:-1]) - data.low
        dmp = list(pd.Series([x if (x > 0 and x > y) else 0 for x, y in zip(hd, ld)]).rolling(window=n).apply(
            lambda x: np.array(x).sum()))
        dmm = list(pd.Series([x if (x > 0 and x > y) else 0 for x, y in zip(ld, hd)]).rolling(window=n).apply(
            lambda x: np.array(x).sum()))
        hc = np.abs(data.high - data.close.rolling(window=2).apply(lambda x: x[0:-1]))
        lc = np.abs(data.low - data.close.rolling(window=2).apply(lambda x: x[0:-1]))
        hl = data.high - data.low
        tr = list(pd.Series([max(x, y, z) for x, y, z in zip(hc, lc, hl)]).rolling(window=n).apply(
            lambda x: np.array(x).sum()))
        pdi = pd.Series(dmp) * 100 / pd.Series(tr)
        mdi = pd.Series(dmm) * 100 / pd.Series(tr)
        adx_final = list(pd.Series(np.abs(pdi - mdi) / (pdi + mdi) * 100).rolling(window=n).apply(lambda x:
                                                                                                  np.array(x).mean()))
        data['hd'] = hd
        data['ld'] = ld
        data['dmp'] = dmp
        data['dmm'] = dmm
        data['adx'] = adx_final
        return data

    def boll(self, data, n, k1, col='close'):

        mean = data[col].rolling(window=n + 1).apply(lambda x: np.array(x[0:-1]).mean())
        std = data[col].rolling(window=n + 1).apply(lambda x: np.array(x[0:-1]).std())
        data['boll_mean'] = mean
        data['boll_std'] = std
        data['boll_up'] = mean+k1*std
        data['boll_down'] = mean-k1*std
        return data

    def sar(self, data, n):
        flag = []

        for i in range(len(data)):
            if i < n:
                flag.append(0)
            else:
                if data.ix[i-1, 'close']-data.ix[i-n, 'open'] > 0:
                    flag.append(1)
                else:
                    flag.append(-1)
        data['flag'] = flag

        return data

    def macd(self, data, n1=12, n2=26):
        ema12 = [data.ix[0, 'close']]
        ema26 = [data.ix[0, 'close']]
        for i in range(1, len(data)):
            ema12.append((n1-1)/(n1+1)*ema12[-1]+2/(n1+1)*data.ix[i, 'close'])
            ema26.append((n2-1)/(n2+1) * ema26[-1] + 2 / (n2+1) * data.ix[i, 'close'])
        data['ema12'] = ema12
        data['ema26'] = ema26
        data['dif'] = data['ema12']-data['ema26']
        dea = [data.ix[0, 'dif']]
        for i in range(1, len(data)):
            dea.append(8/10*dea[-1]+2/10*data.ix[i, 'dif'])
        data['dea'] = dea
        return data

    def double_moving_llkr(self, data, h1, h2):
        data1 = self.ksr(data, h=h1)
        data1['ksr1'] = data1['ksr']
        data2 = self.ksr(data, h=h2)
        data2['ksr2'] = data1['ksr']
        del data2['ksr']
        return data2

    def llmacd(self, data, h1, h2):
        data1 = self.ksr(data, h=h1)
        data1['ksr1'] = data1['ksr']
        data2 = self.ksr(data, h=h2)

        data2['dif'] = data2['ksr1']-data2['ksr']
        dea = [data2.ix[0, 'dif']]
        for i in range(1, len(data2)):
            dea.append(8/10*dea[-1]+2/10*data2.ix[i, 'dif'])
        data2['dea'] = dea
        return data2

    def vr(self):
        pass

    # def kdj(self, data, n1, n2):
    #     ln = data.low.rolling(window=n1).apply(lambda x: np.array(x.min()))
    #     hn = data.high.rolling(window=n1).apply(lambda x: np.array(x.max()))
    #     rsv = ((data.close-ln)/(hn-ln)*100).fillna(50)
    #     kdj_k = [50]
    #     kdj_d = [50]
    #     for i in range(1, len(data)):
    #         kdj_k.append((n2-1)/n2*kdj_k[-1]+1/n2*rsv[i])
    #         kdj_d.append((n2-1)/n2*kdj_d[-1]+1/n2*kdj_k[-1])
    #     data['kdj_k'] = kdj_k
    #     data['kdj_d'] = kdj_d
    #     data['kdj_j'] = 3*data['kdj_k']-2*data['kdj_d']
    #     return data
    def kdj(self, data, n1, n2):
        ln = data.low.rolling(window=n1).apply(lambda x: np.array(x.min()))
        hn = data.high.rolling(window=n1).apply(lambda x: np.array(x.max()))
        rsv = ((data.close-ln)/(hn-ln)*100).fillna(50)
        data['rsv'] = rsv
        data['kdj_k'] = data.rsv.rolling(window=n2).apply(lambda x: np.array(x.mean()))
        data['kdj_d'] = data.kdj_k.rolling(window=n2).apply(lambda x: np.array(x.mean()))
        data['kdj_j'] = 3*data['kdj_k']-2*data['kdj_d']
        return data

    def chaikin(self, data,n1=10,n2=30):
        mid1=data.volume*(2*data.close-data.high-data.low)/(data.high+data.low)
        mid=[]
        for i in range(len(mid1)):
            mid.append(sum(mid1[0:i+1]))
        data['mid1'] = mid1
        data['mid'] = mid
        midn1 = data.mid.rolling(window=n1).apply(lambda x: np.array(x.mean()))
        midn2 = data.mid.rolling(window=n2).apply(lambda x: np.array(x.mean()))
        data['midn1'] = midn1
        data['midn2'] = midn2
        data['chinkin'] = midn1-midn2
        return data

    def indicator(self, data, limit, t='F'):
        indica = np.zeros(data.shape)
        if t == 'F':  # 平滑的话包括t0时候之后的数据，滤波则只有t0和t0之前的数据
            indica[(- limit < data) & (data <= 0)] = 1
        elif t == 'S':
            indica[(- limit < data) & (data <= limit)] = 1
        return indica

    def kernelfun(self, data, type='gau', t='F'):
        if type == 'gau':  # 高斯核
            K = lambda u: np.exp(- u * u / 2) / np.sqrt(2 * np.pi)
            return K(data) * self.indicator(data, np.inf, t)

    def ksr(self, data, h, type='gau', t='F'):
        # 局域线性核回归:f为核函数，t为平滑(S)或滤波(F)

        x = np.arange(len(data))
        ksr=[0]*(h-1)
        for i in range(h-1, len(x)):
            x0=x[i]
            xx = x-x0
            s0=np.sum(self.kernelfun(xx/h, type, t))
            s1 = np.sum(xx * self.kernelfun(xx / h, type, t))
            s2 = np.sum(xx ** 2 * self.kernelfun(xx / h, type, t))
            w = (s2 - s1 * xx) * self.kernelfun(xx / h, type, t) / (s2 * s0 - s1 ** 2)
            ksr.append(np.sum(w * data.open))
        data['ksr'] = ksr
        return data

    def trend(self, data, h=10, type='LLKR'):
        if type is 'LLKR':
            data = self.ksr(data, h, 'gau', 'F')
        else:
            pass
        diff = data.ksr.rolling(window=2).apply(lambda x: (x[1]-x[0])/x[0])
        data['diff'] = diff
        return data

    def trend_ma(self, data, n=10, col='close'):
        ma = data[col].rolling(window=n + 1).apply(lambda x: np.array(x[0:-1]).mean())

        data['trend_ma'] = ma
        data['diff'] = data.trend_ma.rolling(window=2).apply(lambda x: (x[1] - x[0]) / x[0])
        return data

    def trend_ema(self, data, n=10, col='close'):
        ema = [data.ix[0, col]]
        for i in range(1, len(data)):
            ema.append((n-1)/(n+1)*ema[-1]+2/(n+1)*data.ix[i, col])
        data['trend_ema'] = ema
        data['diff_ema'] = data.trend_ema.rolling(window=2).apply(lambda x: (x[1] - x[0]) / x[0])
        return data

    def add_func(self, func='double_moving', k1=3, k2=15, k3=3):  # 添加指标线，如双重均线等
        main_start = self.main_code.drop_duplicates(subset='trade_hiscode', keep='first')
        main_end = self.main_code.drop_duplicates(subset='trade_hiscode', keep='last')
        main_start_end = zip(main_start.index, main_end.index)
        data_list = []
        for i, j in main_start_end:
            future_total = self.data_source[main_start.at[i, 'trade_hiscode'][:-4]]
            if func == 'double_moving':
                future_total = self.double_moving(future_total, k1, k2)
            elif func == 'three_moving':
                future_total = self.three_moving(future_total, k1, k2, k3)
            elif func == 'double_moving_llkr':
                future_total = self.double_moving_llkr(future_total, k1, k2)
            elif func == 'adx':
                future_total = self.adx(future_total, k1)
            elif func == 'extreme':
                future_total = self.extreme(future_total)
            elif func == 'boll':
                future_total = self.boll(future_total, k1, k2)
            elif func == 'hl_level':
                future_total = self.hl_level(future_total, k1, k2)
            elif func == 'atr':
                future_total = self.atr(future_total, k1, k2)
            elif func == 'macd':
                future_total = self.macd(future_total,k1,k2)
            elif func == 'kdj':
                future_total = self.kdj(future_total, k1, k2)
            elif func == 'trend':
                future_total = self.trend(future_total, k1, type = 'LLKR')
            elif func == 'trend_ma':
                future_total = self.trend_ma(future_total, k1)
            elif func == 'trend_ema':
                future_total = self.trend_ema(future_total, k1)


            elif func == 'llmacd':
                future_total = self.llmacd(future_total, k1, k2)
            elif func == 'sar':
                future_total = self.sar(future_total, k1)
            # elif func == 'chaikin':
            #     future_total = self.chaikin(future_total, k1, k2)
            else:
                print('无此函数')
                exit(0)
            self.data_source[main_start.at[i, 'trade_hiscode'][:-4]] = future_total
            future = future_total.ix[i:j, :]
            data_list.append(future)
        self.data = pd.concat([pd.concat(data_list), self.main_code], axis=1).dropna(axis=0, how='any')
        # self.data = self.chaikin(self.data,n1=8,n2=30)

if __name__ == '__main__':

    d = GetData()
    d.add_func(func='sar', k1=3)
    print(d.data)
    d.data.to_excel('ddd.xlsx')

