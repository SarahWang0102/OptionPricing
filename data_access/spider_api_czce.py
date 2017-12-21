#!/usr/bin/env python
# encoding: utf-8

from WindPy import *
import requests
import pandas as pd
import os
import time

w.start()



def spider_option(firstdate,enddate):
    dataset = {}
    date_range = w.tdays(firstdate, enddate, "").Data[0]
    for i in range(len(date_range)):
        time.sleep(0.5)
        date = date_range[i]
        # print('spider : ',date)
        year, month, day = date.year, date.month, date.day
        #url = 'http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html?dayQuotes.variety='\
        #      + codename+'&dayQuotes.trade_type=1&year='+str(year)+'&month='+str(month-1)+'&day='+str(day)
        if month < 10: str_month = '0'+str(month)
        else: str_month = str(month)
        if day < 10: str_day = '0' + str(day)
        else: str_day = str(day)
        url = 'http://www.czce.com.cn/portal/DFSStaticFiles/Option/'\
              +str(year)+'/'+str(year)+str_month+str_day+'/OptionDataDaily.txt'
        #http://www.czce.com.cn/portal/DFSStaticFiles/Future/2017/20170919/FutureDataDailyMA.htm
        #http://www.czce.com.cn/portal/DFSStaticFiles/Future/2017/20170915/FutureDataDailySR.txt
        #http://www.czce.com.cn/portal/DFSStaticFiles/Option/2017/20171208/OptionDataDaily.txt
        res = requests.get(url)
        content = res.content
        # print(res)
        result = content.decode(encoding='GB18030')
        rows = result.split('\n')
        if len(rows) == 0:
            pass
        else:
            index = []
            index_row =  rows[1].split("|")
            for item in index_row:
                index.extend(item.split())
            data = pd.DataFrame(index=index)
            for nbrRow in range(2,len(rows)):
                row = rows[nbrRow]
                colums_of_row = row.split('|')
                if len(colums_of_row) != len(index):
                    continue
                if colums_of_row[0][0:2] == '小计' or colums_of_row[0][0:2] == '总计' \
                        or colums_of_row[0][0:4] == 'SR合计' :
                    continue
                data[nbrRow] = colums_of_row
            # datestr = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
            # data.to_json(os.path.abspath('..')+ '\marketdata\\' + codename + '_mkt_' + datestr + '.json')
            dt_date = datetime.date(date)
            dataset.update({dt_date: data})
    return dataset

def spider_future(firstdate,enddate):
    dataset = {}
    date_range = w.tdays(firstdate, enddate, "").Data[0]
    for i in range(len(date_range)):
        time.sleep(0.5)
        date = date_range[i]
        # print(date)
        year, month, day = date.year, date.month, date.day
        if month < 10: str_month = '0'+str(month)
        else: str_month = str(month)
        if day < 10: str_day = '0' + str(day)
        else: str_day = str(day)
        url = 'http://www.czce.com.cn/portal/DFSStaticFiles/Future/'\
              +str(year)+'/'+str(year)+str_month+str_day+'/FutureDataDaily.txt'
        #http://www.czce.com.cn/portal/DFSStaticFiles/Future/2017/20170919/FutureDataDailyMA.htm
        #http://www.czce.com.cn/portal/DFSStaticFiles/Future/2017/20170915/FutureDataDailySR.txt
        #http://www.czce.com.cn/portal/DFSStaticFiles/Option/2017/20170915/OptionDataDaily.txt
        res = requests.get(url)
        content = res.content
        # print(res)
        result = content.decode(encoding='GB18030')
        rows = result.split('\n')
        if len(rows) == 0:
            pass
        else:
            index = []
            index_row =  rows[1].split("|")
            for item in index_row:
                index.extend(item.split())
            data = pd.DataFrame(index=index)
            for nbrRow in range(2,len(rows)):
                row = rows[nbrRow]
                colums_of_row = row.split('|')
                if len(colums_of_row) != len(index):
                    continue
                if colums_of_row[0][0:2] == '小计' or colums_of_row[0][0:2] == '总计':
                    continue
                data[nbrRow] = colums_of_row
            # datestr = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
            # data.to_json(os.path.abspath('..')+ '\marketdata\\' + codename + '_future_mkt_' + datestr + '.json')
            dt_date = datetime.date(date)
            dataset.update({dt_date: data})
    return dataset

            # def get_data():
#
#     # fd = {'i': '2013/10/18', 'jm': '2013/03/22', 'j': '2011/04/15'}
#     fd = { 'sr': '2017-09-10'}
#
#     # fd = {'v': '2009/05/25', 'b': '2004/12/22', 'm': '	2000/07/17', 'a': '1999/01/04', 'y': '2006/01/09',
#     #       'jd': '2013/11/08', 'bb': '2013/12/06', 'jm': '2013/03/22', 'j': '2011/04/15', 'pp': '2014/02/28',
#     #       'l': '2007/07/31', 'i': '2013/10/18', 'fb': '2013/12/06', 'c': '2004/09/22', 'cs': '2014/12/19',
#     #       'p': '2007/10/29'}
#
#     for code in fd.keys():
#         print("正在爬取 "+code+' 数据……')
#         spider_option(code, fd[code])


# get_data()

# codename = 'sr'
# datestr = '2017-8-21'
# df = pd.read_json(os.path.abspath('..')+ '\marketdata\\' + codename + '_mkt_' + datestr + '.json')
# print(df)