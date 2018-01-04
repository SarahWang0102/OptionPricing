#!/usr/bin/env python
# encoding: utf-8
"""
@Auther: Simon
@Software: PyCharm Community Edition
@File: bkt1.py
@Time: 2016/10/23 16:40
"""
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import datetime


class BktArbitrage(object):

    def __init__(self, bkt):

        self.bkt = bkt
        self.riskfree = 0.024
        self.traderecord = pd.DataFrame()
        self.r = pd.Series()
        self.account = pd.DataFrame()

    def converge(self):
        self.account['日期'] = self.bkt[0].account['日期']
        self.account['交易次数'] = self.bkt[0].account['交易次数']
        for i in range(len(self.bkt)):
            try:
                self.account['总资产'] += self.bkt[i].account['总资产']
                self.account['当日收益'] += self.bkt[i].account['当日收益']
                self.account['累计收益'] += self.bkt[i].account['累计收益']
                self.traderecord['净利'] += self.bkt[i].traderecord['净利']
                self.traderecord['累计净利'] += self.bkt[i].traderecord['累计净利']
                self.traderecord['总资产'] += self.bkt[i].traderecord['总资产']
            except KeyError:
                self.account['总资产'] = self.bkt[i].account['总资产']
                self.account['当日收益'] = self.bkt[i].account['当日收益']
                self.account['累计收益'] = self.bkt[i].account['累计收益']
                self.traderecord['净利'] = self.bkt[i].traderecord['净利']
                self.traderecord['累计净利'] = self.bkt[i].traderecord['累计净利']
                self.traderecord['总资产'] = self.bkt[i].traderecord['总资产']
        self.traderecord['持仓天数'] = self.bkt[0].traderecord['持仓天数']
        self.account['净值'] = self.account['总资产'] / self.account.loc[0, '总资产']
        trade_net_value = self.traderecord['总资产']/self.account.loc[0, '总资产']
        trade_returns = trade_net_value.rolling(window=2).apply(lambda x: x[1]/x[0] - 1).fillna(0)
        trade_returns[0] = trade_net_value[0]/1-1
        self.traderecord['单笔收益率'] = trade_returns

    def describe(self):   # 生成描述回测de各种指标到self.r变量中，方便单独调用
        self.converge()
        netvalue = self.account['净值']
        returns = netvalue.rolling(window=2).apply(lambda x: x[1]/x[0] - 1).fillna(0)
        countdays = (pd.to_datetime(self.account.loc[len(self.account) - 1, '日期']) - pd.to_datetime(
            self.account.loc[0, '日期'])).days
        accuratio = self.account.at[len(self.account) - 1, '总资产'] / self.account.loc[0, '总资产'] - 1
        yearratio = (accuratio+1) ** (365 / countdays)-1
        volatility_yr = np.std(returns, ddof=0) * np.sqrt(252)
        sharpe = (yearratio - self.riskfree) / volatility_yr
        startdate = datetime.datetime.strptime(str(self.account.loc[0, '日期']), '%Y-%m-%d')
        enddate = datetime.datetime.strptime(str(self.account.loc[len(self.account) - 1, '日期']), '%Y-%m-%d')
        # print(len(self.account) - 1)

        maxdrawdowns = pd.Series(index=netvalue.index)
        for i in np.arange(len(netvalue.index)):
            maxnetvalue = max(netvalue.iloc[0:(i+1)])
            if maxnetvalue == netvalue.iloc[i]:
                maxdrawdowns.iloc[i] = 0
            else:
                maxdrawdowns.iloc[i] = (netvalue.iloc[i] - maxnetvalue) / maxnetvalue
        maxdrawdown = maxdrawdowns.min()
        maxdrawdown_day_pandas = self.account.loc[list(maxdrawdowns).index(maxdrawdown), '日期']
        maxdrawdown_day_date = datetime.datetime.strptime(str(maxdrawdown_day_pandas), '%Y-%m-%d').date()

        gain = self.traderecord[self.traderecord['单笔收益率'] > 0]
        gaincount = gain['单笔收益率'].count()
        gainaverage = gain['单笔收益率'].mean()
        gainmax = gain['单笔收益率'].max()

        loss = self.traderecord[self.traderecord['单笔收益率'] < 0]
        losscount = loss['单笔收益率'].count()
        lossaverage = loss['单笔收益率'].mean()
        lossmax = loss['单笔收益率'].min()
        gain_loss_ratio = -1*gainaverage/lossaverage
        tradecount = self.account['交易次数'].sum()
        win_ratio = gaincount/(gaincount+losscount)
        self.r['开始时间'] = startdate.date()
        self.r['结束时间'] = enddate.date()
        self.r['持续时间'] = countdays
        self.r['累计收益率'] = accuratio
        self.r['年化收益率'] = yearratio
        self.r['夏普率'] = sharpe
        self.r['最大回撤'] = maxdrawdown
        self.r['最大回撤发生日'] = maxdrawdown_day_date
        self.r['交易次数'] = tradecount
        self.r['胜率'] = win_ratio
        self.r['盈利次数'] = gaincount
        self.r['盈利交易最大单笔收益'] = gainmax
        self.r['盈利交易平均每笔收益'] = gainaverage
        self.r['亏损次数'] = losscount
        self.r['亏损交易最大单笔亏损'] = lossmax
        self.r['亏损交易平均每笔收益'] = lossaverage
        self.r['盈亏比'] = gain_loss_ratio
        return self.r

    def net_value_plot(self, grid=True):

        fig, ax1 = plt.subplots()
        p1, =ax1.plot(np.array(pd.to_datetime(self.account['日期'])), np.array(self.account['净值']), color='mediumblue',label='net_value')
        ax1.set_ylabel('net_value', color='mediumblue')
        plt.setp(plt.gca().get_xticklabels(), rotation=30, horizontalalignment='right')
        titlename = 'net_value'
        plt.title(titlename)
        ax1.legend([p1], [p1.get_label()])
        if grid is True:
            ax1.xaxis.grid(True, which='major', linestyle='--', linewidth=1)  # x坐标轴的网格使用主刻度
            ax1.yaxis.grid(True, which='major', linestyle='--')
        else:
            pass
        plt.savefig(titlename + '.png', dpi=200)
        plt.show()

    def every_mouth_profit(self):
        account = self.account.copy()
        account['ym'] = pd.to_datetime(account['日期']).dt.strftime('%Y-%m')
        mouth_group = pd.concat([account.groupby('ym')['净值'].first(), account.groupby('ym')['净值'].last()],
                                axis=1)
        mouth_group.columns = ['value_start', 'value_end']
        mouth_group['profit_ratio'] = (mouth_group.value_end - mouth_group.value_start) / mouth_group.value_start

        plt.bar(np.array(pd.to_datetime(mouth_group.index)), np.array(mouth_group.profit_ratio))
        plt.title('每月收益图')
        plt.setp(plt.gca().get_xticklabels(), rotation=45, horizontalalignment='right')
        plt.show()

    def printresult(self):  # 把self.r按合适的格式打印出来

        result = self.describe()
        self.writetoexcel()
        print('开始时间：           ', result['开始时间'])
        print('结束时间：           ', result['结束时间'])
        print('持续时间：           ', result['持续时间'], '天')
        print('累计收益率：          %.2f' % (result['累计收益率']*100), '%')
        print('年化收益率：          %.2f' % (result['年化收益率']*100), '%')
        print('夏普率：              %.2f' % result['夏普率'])
        print('最大回撤：            %.2f' % (result['最大回撤']*100), '%')
        print('最大回撤发生日：     ', result['最大回撤发生日'])
        print('交易次数：           ', result['交易次数'])
        print('胜率：                %.2f' % (result['胜率']*100), '%')
        print('盈利次数：           ', result['盈利次数'])
        print('盈利交易最大单笔收益：%.2f' % (result['盈利交易最大单笔收益'] * 100), '%')
        print('盈利交易平均每笔收益：%.2f' % (result['盈利交易平均每笔收益']*100), '%')
        print('亏损次数：           ', result['亏损次数'])
        print('亏损交易最大单笔亏损：%.2f' % (result['亏损交易最大单笔亏损'] * 100), '%')
        print('亏损交易平均每笔收益：%.2f' % (result['亏损交易平均每笔收益']*100), '%')
        print('盈亏比：              %.2f' % result['盈亏比'])

    def writetoexcel(self):  # 交易记录写入到excel中，只有运行printresult()函数才会运行 文件名为traderecord+月天时分
        traderecord = self.traderecord.copy()
        account = self.account.copy()
        if len(traderecord) == 0:
            print('traderecord为空,请检查是否未开仓或者开了一笔未平')
            exit(1)
        filename2 = 'account' + datetime.datetime.now().strftime('_%m_%d_%H_%M') + '.xlsx'
        try:
            account.to_excel('account'+ '.xlsx', sheet_name='Account')
        except PermissionError:
            account.to_excel(filename2, sheet_name='Account')


class Bkt(object):
    def __init__(self, leverage=0.5, marginrate=0.10, capital=1000000, unit_value=10, unit=1):

        self.position = 0
        self.data_day = pd.DataFrame()
        self.data_day_dict = dict()
        self.n = 0
        self.N = len(self.data_day)
        self.open_index = 0  # 记录开仓位置
        self.bar = dict()
        self.costprice = 0  # 记录开仓成本价

        self.unit_value = unit_value  # 1点价值多少
        self.capital = capital  # 起始资金
        self.tradefee1 = 0.000  # 开仓手续费
        self.tradefee2 = 0.000  # 平仓手续费
        self.marginrate = marginrate  # 保证金
        self.leverage = leverage  # 持仓比例
        self.unit = unit  # 价格最小变动单位
        self.riskfree = 0.024  # 无风险收益率 用来计算夏普率
        self.tradedaylist = pd.DataFrame()   # 交易结果按天整合 不包括没有成交记录的交易日
        self.tradeprofit = pd.DataFrame()    # 收益情况 包括没有成交记录的交易日
        self.tradedayprofit = pd.DataFrame()
        self.r = pd.Series()  # 记录评价指标
        self.traderecord_col = ['开仓日期', '方向', '开仓时间', '开仓价', '开仓成本',
                                '手数', '保证金占用', '平仓日期', '平仓时间', '持仓天数', '平仓价',
                                '平仓成本', '净利', '累计净利', '收益率', '总资产']
        self.traderecord = pd.DataFrame(columns=self.traderecord_col)  # 每笔交易 结算账户的交易信息
        self.trade_list = []   # 每次交易字典型记录集合
        self.trade_temp = []  # 每日里临时记录
        self.tradeaccount_col = ['日期', '交易次数', '账户状态', '开仓价格', '开仓成本', '手数', '保证金占用', '累计浮盈', '当日浮盈',
                                 '当日净利', '当日收益', '累计收益', '当日收益率', '总资产']
        self.account = pd.DataFrame(columns=self.tradeaccount_col)
        self.lastbar = dict()
        self.nextbar = dict()

    def usable_capital(self):
        return self.account.at[len(self.account)-1, '总资产']

    def start(self, data_day):

        self.data_day = data_day
        if self.data_day.isnull().any() is True:
            print('数据存在空值，请检查')
        else:
            pass
        self.data_day_dict = data_day.to_dict('index')
        self.N = len(self.data_day)
        self.current_bar()
        self.ini_acc()
        self.last_bar()
        self.next_bar()

    def ini_acc(self):
        account = {'日期': self.bar['date'], '交易次数': 0,
                   '账户状态': 0, '开仓价格': 0, '开仓成本': 0, '手数': 0,
                   '保证金占用': 0, '累计浮盈': 0, '当日浮盈': 0, '当日净利': 0,
                   '当日收益': 0, '累计收益': 0, '当日收益率': 0, '总资产': self.capital}
        account = pd.DataFrame([account], columns=self.tradeaccount_col)
        self.account = self.account.append(account, ignore_index=True)

    def current_bar(self):

        try:
            self.bar = self.data_day_dict[self.n]
        except KeyError:
            pass

    def open_price(self):
        return self.trade_list[-1]['开仓价']

    def high_price(self,col='high'):
        return self.data_day.ix[self.open_index:self.n,:][col].max()

    def low_price(self,col='low'):
        return self.data_day.ix[self.open_index:self.n,:][col].min()

    def last_bar(self):
        try:
            self.lastbar = self.data_day_dict[self.n-1]
        except KeyError:
            pass

    def next_bar(self):
        try:
            self.nextbar = self.data_day_dict[self.n+1]
        except KeyError:
            pass

    def next(self):
        self.n += 1
        self.current_bar()
        self.last_bar()
        self.next_bar()

    def tradelot(self, openprice):  # 计算当前可交易手数
        if len(self.traderecord) == 0:
            total_capital = self.capital
        else:
            total_capital = self.usable_capital()
        available_lot = np.floor(total_capital * self.leverage/(self.marginrate * openprice * self.unit_value))
        return available_lot

    def buy(self, tradeprice, lot=None):  # 做多操作 暂时记录到临时列表self.trade_list中

        buy_dict = dict()
        buy_dict['开仓日期'] = self.bar['date']
        buy_dict['方向'] = 1
        try:
            buy_dict['开仓时间'] = self.bar['time']
        except KeyError:
            buy_dict['开仓时间'] = np.nan
        buy_dict['开仓价'] = tradeprice  # np.ceil(tradeprice*(1/self.unit))*self.unit*(1+0.0005)
        if lot is None:
            buy_dict['手数'] = self.tradelot(tradeprice)
        else:
            buy_dict['手数'] = lot
        buy_dict['保证金占用'] = tradeprice * buy_dict['手数'] * self.unit_value * self.marginrate
        buy_dict['开仓成本'] = tradeprice * buy_dict['手数'] * self.unit_value * self.tradefee1
        self.position=1
        self.costprice = tradeprice
        self.trade_list.append(buy_dict)
        self.trade_temp.append(buy_dict)
        self.open_index = self.n

    def short(self, tradeprice, lot=None):   # 做空操作 暂时记录到临时列表self.trade_list中

        short_dict = dict()
        short_dict['开仓日期'] = self.bar['date']
        short_dict['方向'] = -1
        try:
            short_dict['开仓时间'] = self.bar['time']
        except KeyError:
            short_dict['开仓时间'] = np.nan
        short_dict['开仓价'] = tradeprice  # np.floor(tradeprice*(1/self.unit))*self.unit*(1+0.0005)
        if lot is None:
            short_dict['手数'] = self.tradelot(tradeprice)
        else:
            short_dict['手数'] = lot
        short_dict['保证金占用'] = tradeprice * short_dict['手数'] * self.unit_value * self.marginrate
        short_dict['开仓成本'] = tradeprice * short_dict['手数'] * self.unit_value * self.tradefee1
        self.position = -1
        self.costprice = tradeprice
        self.trade_list.append(short_dict)
        self.trade_temp.append(short_dict)
        self.open_index = self.n

    def sell(self, tradeprice):  # 平多仓操作，暂时记录到self.trade_list中，并记录到总的交易记录中
        self.trade_list[-1]['平仓日期'] = self.bar['date']
        self.trade_list[-1]['持仓天数'] = (pd.to_datetime(self.trade_list[-1]['平仓日期'])-pd.to_datetime(
            self.trade_list[-1]['开仓日期'])).days
        try:
            self.trade_list[-1]['平仓时间'] = self.bar['time']
        except KeyError:
            self.trade_list[-1]['平仓时间'] = np.nan
        self.trade_list[-1]['平仓价'] = tradeprice  # np.floor(tradeprice*(1/self.unit))*self.unit*(1+0.0005)
        self.trade_list[-1]['平仓成本'] = tradeprice * self.trade_list[-1]['手数'] * self.unit_value * self.tradefee2
        self.trade_list[-1]['净利'] = (tradeprice - self.trade_list[-1]['开仓价']) * self.trade_list[-1]['手数'] * self.\
            unit_value * self.trade_list[-1]['方向'] - self.trade_list[-1]['开仓成本'] - self.trade_list[-1]['平仓成本']
        if len(self.trade_list) == 1:
            self.trade_list[0]['累计净利'] = self.trade_list[-1]['净利']
            self.trade_list[0]['总资产'] = self.capital + self.trade_list[-1]['净利']
            self.trade_list[-1]['收益率'] = self.trade_list[-1]['净利'] / self.capital
        else:
            self.trade_list[-1]['累计净利'] = self.trade_list[-2]['累计净利'] + self.trade_list[-1]['净利']
            self.trade_list[-1]['总资产'] = self.trade_list[-2]['总资产'] + self.trade_list[-1]['净利']
            self.trade_list[-1]['收益率'] = self.trade_list[-1]['净利'] / self.trade_list[-2]['总资产']
        if len(self.trade_temp) > 0:
            self.trade_temp.pop()
            self.trade_temp.append(self.trade_list[-1])
        self.position = 0
        self.costprice = 0
        self.trade_temp.append(self.trade_list[-1])
        traderecord = pd.DataFrame([self.trade_list[-1]], columns=self.traderecord_col)
        self.traderecord = self.traderecord.append(traderecord, ignore_index=True)

    def cover(self, tradeprice):  # 平空仓操作，暂时记录到self.trade_list中，并记录到总的交易记录中
        self.trade_list[-1]['平仓日期'] = self.bar['date']
        self.trade_list[-1]['持仓天数'] = (pd.to_datetime(self.trade_list[-1]['平仓日期'])-pd.to_datetime(
            self.trade_list[-1]['开仓日期'])).days
        try:
            self.trade_list[-1]['平仓时间'] = self.bar['time']
        except KeyError:
            self.trade_list[-1]['平仓时间'] = np.nan
        self.trade_list[-1]['平仓价'] = tradeprice  # np.ceil(tradeprice*(1/self.unit))*self.unit*(1+0.0005)
        self.trade_list[-1]['平仓成本'] = tradeprice * self.trade_list[-1]['手数'] * self.unit_value * self.tradefee2
        self.trade_list[-1]['净利'] = (tradeprice - self.trade_list[-1]['开仓价']) * \
            self.trade_list[-1]['手数'] * self.unit_value * self.trade_list[-1]['方向'] - \
            self.trade_list[-1]['开仓成本'] - self.trade_list[-1]['平仓成本']
        if len(self.trade_list) == 1:
            self.trade_list[0]['累计净利'] = self.trade_list[-1]['净利']
            self.trade_list[0]['总资产'] = self.capital + self.trade_list[-1]['净利']
            self.trade_list[-1]['收益率'] = self.trade_list[-1]['净利'] / self.capital
        else:
            self.trade_list[-1]['累计净利'] = self.trade_list[-2]['累计净利'] + self.trade_list[-1]['净利']
            self.trade_list[-1]['总资产'] = self.trade_list[-2]['总资产'] + self.trade_list[-1]['净利']
            self.trade_list[-1]['收益率'] = self.trade_list[-1]['净利'] / self.trade_list[-2]['总资产']  # 可以统一计算
        if len(self.trade_temp) > 0:  # 只开不平的
            self.trade_temp.pop()
            self.trade_temp.append(self.trade_list[-1])
        self.position = 0
        self.costprice = 0
        self.trade_temp.append(self.trade_list[-1])
        traderecord = pd.DataFrame([self.trade_list[-1]], columns=self.traderecord_col)
        self.traderecord = self.traderecord.append(traderecord, ignore_index=True)

    def trade_profit(self):  # 交易记录按天汇总，得到有成交的交易日的结果
        traderecord = self.traderecord.copy()
        self.tradeprofit = pd.concat([traderecord.groupby('平仓日期')['平仓日期'].count(),
                                      traderecord.groupby('平仓日期')['开仓成本'].sum(),
                                      traderecord.groupby('平仓日期')['平仓成本'].sum(),
                                      traderecord.groupby('平仓日期')['净利'].sum(),
                                      traderecord.groupby('平仓日期')['累计净利'].last(),
                                      traderecord.groupby('平仓日期')['总资产'].last()], axis=1)
        self.tradeprofit.columns = ['交易次数', '开仓成本', '交易成本', '净利', '累计净利', '总资产']
        return self.tradeprofit

    def clear(self):  # 每日清算账户信息

        if len(self.trade_temp) > 1:  # 日内交易，一天多次
            acc_float1 = self.unit_value * self.trade_temp[0]['方向'] * self.trade_temp[0]['手数'] * (
                self.trade_temp[0]['平仓价'] - self.trade_temp[0]['开仓价']) - self.trade_temp[0]['开仓成本'] - \
                        self.trade_temp[0]['平仓成本']
            today_float1 = acc_float1 - self.account.at[len(self.account) - 1, '累计浮盈'] * abs(
                self.account.at[len(self.account) - 1, '账户状态'])
            today_profit1 = 0
            today_gain1 = today_float1 + today_profit1
            acc_float2 = self.unit_value * self.trade_temp[1]['方向'] * self.trade_temp[1]['手数'] * (
                self.bar['close'] - self.trade_temp[1]['开仓价']) - self.trade_temp[1]['开仓成本']  # 累计浮盈，从开仓开始算
            today_float2 = acc_float2  # 今日浮盈，今日累计减昨日累计
            today_profit2 = 0  # 今日净利，为当天开平获得的利润
            today_gain2 = today_float2 + today_profit2  # 今天收益，为今日浮盈和今日净利之和

            today_profit = today_profit1+today_profit2
            today_gain = today_gain2+today_gain1
            acc_gain = today_gain + self.account.at[len(self.account) - 1, '累计收益']
            today_gain_ratio = today_gain/self.account.at[len(self.account)-1, '总资产']  # 今日收益率
            capital = today_gain+self.account.at[len(self.account)-1, '总资产']  # 总资产为今日收益和昨日总资产之和

            account = {'日期': self.bar['date'], '交易次数': len(self.trade_temp)-1, '账户状态': self.trade_temp[1]['方向'],
                       '开仓价格': self.trade_temp[1]['开仓价'], '开仓成本': self.trade_temp[1]['开仓成本'],
                       '手数': self.trade_temp[1]['手数'], '保证金占用': self.trade_temp[1]['保证金占用'],
                       '累计浮盈': acc_float2, '当日浮盈': today_float2, '当日净利': today_profit, '当日收益': today_gain,
                       '累计收益': acc_gain, '当日收益率': today_gain_ratio,
                       '总资产': capital}
            account = pd.DataFrame([account], columns=self.tradeaccount_col)
            self.account = self.account.append(account, ignore_index=True)  # ignore_index=True使得得到的DataFrame的index按顺序

        elif len(self.trade_temp) == 1 and '开仓日期' in self.trade_temp[0] and not('平仓日期' in self.trade_temp[0]):  # 今日只开不平

            acc_float = self.unit_value*self.trade_temp[0]['方向']\
                        * self.trade_temp[0]['手数']\
                        * (self.bar['close']-self.trade_temp[0]['开仓价'])-self.trade_temp[0]['开仓成本']  # 累计浮盈，从开仓开始算
            today_float = acc_float-self.account.at[len(self.account)-1, '累计浮盈'] * abs(
                self.account.at[len(self.account)-1, '账户状态'])  # 今日浮盈，今日累计减昨日累计
            today_profit = 0  # 今日净利，为当天开平获得的利润
            today_gain = today_float+today_profit  # 今天收益，为今日浮盈和今日净利之和
            acc_gain = today_gain+self.account.at[len(self.account)-1, '累计收益']  # 累计收益
            today_gain_ratio = today_gain/self.account.at[len(self.account)-1, '总资产']  # 今日收益率
            capital = today_gain+self.account.at[len(self.account)-1, '总资产']  # 总资产为今日收益和昨日总资产之和
            account = {'日期': self.bar['date'], '交易次数': 0, '账户状态': self.trade_temp[0]['方向'],
                       '开仓价格': self.trade_temp[0]['开仓价'], '开仓成本': self.trade_temp[0]['开仓成本'],
                       '手数': self.trade_temp[0]['手数'], '保证金占用': self.trade_temp[0]['保证金占用'],
                       '累计浮盈': acc_float, '当日浮盈': today_float, '当日净利': today_profit, '当日收益': today_gain,
                       '累计收益': acc_gain, '当日收益率': today_gain_ratio,
                       '总资产': capital}
            account = pd.DataFrame([account], columns=self.tradeaccount_col)
            self.account = self.account.append(account, ignore_index=True)  # ignore_index=True使得得到的DataFrame的index按顺序

        elif len(self.trade_temp) == 1 and '开仓日期' in self.trade_temp[0] and '平仓日期' in self.trade_temp[0]:
            if '开仓日期' == '平仓日期':  # 说明先平后开，即做反手或者 先开后平 在日内的情况
                pass
            elif '开仓日期' != '平仓日期':  # 不相等说明是前面开的仓，今日平掉
                acc_float = self.unit_value*self.trade_temp[0]['方向'] * self.trade_temp[0]['手数'] * \
                            (self.trade_temp[0]['平仓价'] - self.trade_temp[0]['开仓价']) - \
                            self.trade_temp[0]['开仓成本']-self.trade_temp[0]['平仓成本']
                today_float = acc_float - self.account.at[len(self.account) - 1, '累计浮盈'] * abs(
                    self.account.at[len(self.account)-1, '账户状态'])
                today_profit = 0
                today_gain = today_float + today_profit
                acc_gain = today_gain + self.account.at[len(self.account) - 1, '累计收益']
                today_gain_ratio = today_gain / self.account.at[len(self.account)-1, '总资产']
                capital = today_gain + self.account.at[len(self.account) - 1, '总资产']
                account = {'日期': self.bar['date'], '交易次数': 1, '账户状态': 0,
                           '开仓价格': 0, '开仓成本': 0, '手数': 0, '保证金占用': 0,
                           '累计浮盈': acc_float, '当日浮盈': today_float, '当日净利': today_profit, '当日收益': today_gain,
                           '累计收益': acc_gain, '当日收益率': today_gain_ratio,
                           '总资产': capital}
                account = pd.DataFrame([account], columns=self.tradeaccount_col)
                self.account = self.account.append(account, ignore_index=True)

        elif len(self.trade_temp) == 0:  # 说明今日无交易

            if self.account.at[len(self.account)-1, '账户状态'] == 0:  # 无交易 并且没有持仓，不需要净值更新
                account = {'日期': self.bar['date'], '交易次数': len(self.trade_temp), '账户状态': 0,
                           '开仓价格': 0, '开仓成本': 0, '手数': 0, '保证金占用': 0,
                           '累计浮盈': 0, '当日浮盈': 0, '当日净利': 0, '当日收益': 0,
                           '累计收益': self.account.at[len(self.account) - 1, '累计收益'],
                           '当日收益率': 0, '总资产': self.account.at[len(self.account)-1, '总资产']}
                account = pd.DataFrame([account], columns=self.tradeaccount_col)
                self.account = self.account.append(account, ignore_index=True)

            elif self.account.at[len(self.account)-1, '账户状态'] != 0:  # 无交易，但有持仓，净值会变化

                acc_float = self.unit_value*self.account.at[len(self.account)-1, '账户状态'] *\
                            self.account.at[len(self.account)-1, '手数'] * \
                            (self.bar['close'] - self.account.at[len(self.account)-1, '开仓价格']) - \
                            self.account.at[len(self.account)-1, '开仓成本']
                today_float = acc_float - self.account.at[len(self.account) - 1, '累计浮盈'] * abs(
                    self.account.at[len(self.account)-1, '账户状态'])
                today_profit = 0
                today_gain = today_float + today_profit
                acc_gain = today_gain + self.account.at[len(self.account) - 1, '累计收益']
                today_gain_ratio = today_gain / self.account.at[len(self.account)-1, '总资产']
                capital = today_gain + self.account.at[len(self.account) - 1, '总资产']
                account = {'日期': self.bar['date'], '交易次数': 0, '账户状态': self.account.at[len(self.account)-1, '账户状态'],
                           '开仓价格': self.account.at[len(self.account)-1, '开仓价格'],
                           '开仓成本': self.account.at[len(self.account)-1, '开仓成本'],
                           '手数': self.account.at[len(self.account)-1, '手数'],
                           '保证金占用': self.account.at[len(self.account)-1, '保证金占用'],
                           '累计浮盈': acc_float, '当日浮盈': today_float,
                           '当日净利': today_profit, '当日收益': today_gain,
                           '累计收益': acc_gain, '当日收益率': today_gain_ratio,
                           '总资产': capital}
                account = pd.DataFrame([account], columns=self.tradeaccount_col)
                self.account = self.account.append(account, ignore_index=True)
        self.trade_temp = []  # 每日清算后，将临时记录清空
        self.next()

    def writetoexcel(self):  # 交易记录写入到excel中，只有运行printresult()函数才会运行 文件名为traderecord+月天时分
        traderecord = self.traderecord.copy()
        account = self.account.copy()

        if len(traderecord) == 0:
            print('traderecord为空,请检查是否未开仓或者开了一笔未平')
            exit(1)
        # traderecord['平仓日期'] = traderecord['平仓日期'].dt.strftime('%Y-%m-%d')
        filename1 = 'traderecord'+datetime.datetime.now().strftime('_%m_%d_%H_%M')+'.xlsx'
        try:
            traderecord.to_excel('traderecord_single'+'.xlsx', sheet_name='TradeRecord')
        except PermissionError:
            traderecord.to_excel(filename1, sheet_name='TradeRecord')
        filename2 = 'account_single' + datetime.datetime.now().strftime('_%m_%d_%H_%M') + '.xlsx'
        try:
            account.to_excel('account_single' + '.xlsx', sheet_name='Account')
        except PermissionError:
            account.to_excel(filename2, sheet_name='Account')

    def select(self, date):
        return self.account[self.account['日期'] == date].to_dict('index')

    def describe(self):   # 生成描述回测de各种指标到self.r变量中，方便单独调用

        netvalue = self.account['总资产']/self.capital
        returns = netvalue.rolling(window=2).apply(lambda x: x[1]/x[0] - 1).fillna(0)
        self.account['净值'] = netvalue
        self.account = self.account.drop(0)
        self.account.index = range(len(self.account))
        countdays = (pd.to_datetime(self.account.at[len(self.account) - 1, '日期']) -
                     pd.to_datetime(self.account.at[0, '日期'])).days
        accuratio = self.account.at[len(self.account) - 1, '总资产'] / self.capital - 1
        yearratio = (accuratio+1) ** (365 / countdays)-1
        volatility_yr = np.std(returns, ddof=0) * np.sqrt(252)
        sharpe = (yearratio - self.riskfree) / volatility_yr
        try:

            startdate = datetime.datetime.strptime(str(self.account.at[0, '日期'])[:10], '%Y-%m-%d')
        except ValueError:
            startdate = datetime.datetime.strptime(str(self.account.at[0, '日期']), '%Y/%m/%d')
        try:
            enddate = datetime.datetime.strptime(str(self.account.at[len(self.account) - 1, '日期']), '%Y-%m-%d')
        except ValueError:
            enddate = datetime.datetime.strptime(str(self.account.at[len(self.account) - 1, '日期']), '%Y/%m/%d')

        maxdrawdowns = pd.Series(index=netvalue.index)
        for i in np.arange(len(netvalue.index)):
            maxnetvalue = max(netvalue[0:(i+1)])
            if maxnetvalue == netvalue[i]:
                maxdrawdowns[i] = 0
            else:
                maxdrawdowns[i] = (netvalue[i] - maxnetvalue) / maxnetvalue
        maxdrawdown = maxdrawdowns.min()
        maxdrawdown_day_pandas = self.account.loc[list(maxdrawdowns).index(maxdrawdown)-1, '日期']
        maxdrawdown_day_date = datetime.datetime.strptime(str(maxdrawdown_day_pandas), '%Y-%m-%d').date()

        trade_net_value = self.traderecord['总资产']/self.capital
        trade_returns = trade_net_value.rolling(window=2).apply(lambda x: x[1]/x[0] - 1).fillna(0)
        trade_returns[0] = trade_net_value[0]/1-1
        self.traderecord['单笔收益率'] = trade_returns

        gain = self.traderecord[self.traderecord['单笔收益率'] > 0]
        gaincount = gain['单笔收益率'].count()
        gainaverage = gain['单笔收益率'].mean()
        gainmax = gain['单笔收益率'].max()

        loss = self.traderecord[self.traderecord['单笔收益率'] < 0]
        losscount = loss['单笔收益率'].count()
        lossaverage = loss['单笔收益率'].mean()
        lossmax = loss['单笔收益率'].min()
        gain_loss_ratio = -1*gainaverage/lossaverage
        tradecount = self.account['交易次数'].sum()
        win_ratio = gaincount/tradecount
        self.r['开始时间'] = startdate.date()
        self.r['结束时间'] = enddate.date()
        self.r['持续时间'] = countdays
        self.r['累计收益率'] = accuratio
        self.r['年化收益率'] = yearratio
        self.r['夏普率'] = sharpe
        self.r['最大回撤'] = maxdrawdown
        self.r['最大回撤发生日'] = maxdrawdown_day_date
        self.r['交易次数'] = tradecount
        self.r['胜率'] = win_ratio
        self.r['盈利次数'] = gaincount
        self.r['盈利交易最大单笔收益'] = gainmax
        self.r['盈利交易平均每笔收益'] = gainaverage
        self.r['亏损次数'] = losscount
        self.r['亏损交易最大单笔亏损'] = lossmax
        self.r['亏损交易平均每笔收益'] = lossaverage
        self.r['盈亏比'] = gain_loss_ratio
        return self.r

    def printresult(self):  # 把self.r按合适的格式打印出来
        self.writetoexcel()
        result = self.describe()
        result.to_excel('result.xlsx')
        print('开始时间：           ', result['开始时间'])
        print('结束时间：           ', result['结束时间'])
        print('持续时间：           ', result['持续时间'], '天')
        print('累计收益率：          %.2f' % (result['累计收益率']*100), '%')
        print('年化收益率：          %.2f' % (result['年化收益率']*100), '%')
        print('夏普率：              %.2f' % result['夏普率'])
        print('最大回撤：            %.2f' % (result['最大回撤']*100), '%')
        print('最大回撤发生日：     ', result['最大回撤发生日'])
        print('交易次数：           ', result['交易次数'])
        print('胜率：                %.2f' % (result['胜率']*100), '%')
        print('盈利次数：           ', result['盈利次数'])
        print('盈利交易最大单笔收益：%.2f' % (result['盈利交易最大单笔收益'] * 100), '%')
        print('盈利交易平均每笔收益：%.2f' % (result['盈利交易平均每笔收益']*100), '%')
        print('亏损次数：           ', result['亏损次数'])
        print('亏损交易最大单笔亏损：%.2f' % (result['亏损交易最大单笔亏损'] * 100), '%')
        print('亏损交易平均每笔收益：%.2f' % (result['亏损交易平均每笔收益']*100), '%')
        print('盈亏比：              %.2f' % result['盈亏比'])

    def net_value_plot(self,grid=True):

        fig, ax1 = plt.subplots()
        p1, =ax1.plot(np.array(pd.to_datetime(self.account['日期'])), np.array(self.account['总资产']/self.capital),color='mediumblue',label='net_value')
        ax1.set_ylabel('net_value', color='mediumblue')
        plt.setp(plt.gca().get_xticklabels(), rotation=30, horizontalalignment='right')
        # ax2 = ax1.twinx()
        # p2, =ax2.plot(np.array(pd.to_datetime(self.account['日期'])), self.data_day.close, color='crimson', label='close')
        # ax2.set_ylabel('colse', color='crimson')
        titlename = 'net_value'
        plt.title(titlename)
        # ax1.legend([p1, p2], [p1.get_label(), p2.get_label()])
        if grid is True:
            ax1.xaxis.grid(True, which='major',linestyle='--',linewidth=1)  # x坐标轴的网格使用主刻度
            ax1.yaxis.grid(True, which='major',linestyle='--')
        else:
            pass
        plt.savefig(titlename + '.png', dpi=200)
        plt.show()

    def most_gain(self, n=5):
        traderecord = self.traderecord.copy()
        traderecord = traderecord.sort_values(by='单笔收益率', ascending=0)
        return traderecord.head(n)

    def most_loss(self, n=5):
        traderecord = self.traderecord.copy()
        traderecord = traderecord.sort_values(by='单笔收益率', ascending=1)
        return traderecord.head(n)

    def every_profit_plot(self):
        plt.bar(np.arange(1, len(self.traderecord['净利'])+1, 1), np.array(self.traderecord['净利']/self.traderecord['手数']))
        plt.title('单笔交易盈亏')
        plt.show()
