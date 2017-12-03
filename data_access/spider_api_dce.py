#!/usr/bin/env python
# encoding: utf-8


from bs4 import BeautifulSoup
from WindPy import *
import requests
import random
import pandas as pd
import time

w.start()


def randheader():  # 随机生成User-Agent

    head_user_agent = ['Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',
                       'Opera/9.27 (Windows NT 5.2; U; zh-cn)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Win64; x64; Trident/4.0)',
                       'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.1; Trident/4.0)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0;'
                       ' SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; '
                       'Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0;'
                       ' SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; '
                       'Media Center PC 6.0; InfoPath.2; .NET4.0C; .NET4.0E; QQBrowser/7.3.9825.400)',
                       'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0; BIDUBrowser 2.x)',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070309 Firefox/2.0.0.3',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1) Gecko/20070803 Firefox/1.5.0.12',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.2) Gecko/2008070208 Firefox/3.0.1',
                       'Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.12) Gecko/20080219'
                       ' Firefox/2.0.0.12 Navigator/9.0.0.6',
                       'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) '
                       'Chrome/28.0.1500.95 Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729;'
                       ' .NET CLR 3.0.30729; Media Center PC 6.0; .NET4.0C; rv:11.0) like Gecko)',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:21.0) Gecko/20100101 Firefox/21.0 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Maxthon/4.0.6.2000'
                       ' Chrome/26.0.1410.43 Safari/537.1 ',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/21.0.1180.92'
                       ' Safari/537.1 LBBROWSER',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75'
                       ' Safari/537.36',
                       'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.11 '
                       'TaoBrowser/3.0 Safari/536.11',
                       'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
                       'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0']
    return {'Host': 'www.dce.com.cn',
            'Connection': 'keep - alive',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept - Language': 'zh - CN, zh;q = 0.8',
            'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))]}


def geturl(url, header, tries_num=20, sleep_time=0.1, time_out=10, max_retry=20):
    sleep_time_p = sleep_time
    time_out_p = time_out
    tries_num_p = tries_num
    try:
        res = requests.get(url, headers=header, timeout=time_out)
        res.raise_for_status()
    except requests.RequestException as e:
        sleep_time_p += 5
        time_out_p += 5
        tries_num_p += - 1
        if tries_num_p > 0:
            time.sleep(sleep_time_p)
            print(url, 'URL Connection Error: 第', max_retry - tries_num_p, u'次 Retry Connection', e)
        res = geturl(url, header, tries_num_p, sleep_time_p, time_out_p, max_retry)
    return res


def spider_mktdata_day(firstdate, enddate,tradetype):
    date_range = w.tdays(firstdate, enddate, "").Data[0]
    dataset = {}
    for i in range(len(date_range)):
        time.sleep(3)
        date = date_range[i]
        year, month, day = date.year, date.month, date.day
        url = 'http://www.dce.com.cn/publicweb/quotesdata/exportDayQuotesChData.html?dayQuotes.variety=all' \
              '&dayQuotes.trade_type='+str(tradetype)+'&year='+str(year)+'&month='+str(month-1)+'&day='+str(day)
        result = geturl(url, header=randheader())
        rows = result.text.split('\n')
        if len(rows) == 0:
            pass
        else:
            index = rows[0].split()
            data = pd.DataFrame(index=index)
            index_length = len(index)
            for nbrRow in range(1, len(rows)):
                row = rows[nbrRow]
                colums_of_row = row.split()
                if len(colums_of_row) != index_length:
                    continue
                data[nbrRow] = colums_of_row
            dt_date = datetime.date(date)
            dataset.update({dt_date:data})
            # datestr = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
            # data.to_json(os.path.abspath('..')+ '\marketdata\\' + codename + '_mkt_' + datestr + '.json')
    return dataset

def spider_mktdata_night(firstdate, enddate,tradetype):
    date_range = w.tdays(firstdate, enddate, "").Data[0]
    dataset = {}
    for i in range(len(date_range)):
        time.sleep(3)
        date = date_range[i]
        year, month, day = date.year, date.month, date.day
        url = 'http://www.dce.com.cn/publicweb/quotesdata/exportTiNight.html?tiNightQuotes.variety=all' \
              '&tiNightQuotes.trade_type='+str(tradetype)+'&year='+str(year)+'&month='+str(month-1)+'&day='+str(day)
        result = geturl(url, header=randheader())
        rows = result.text.split('\n')
        if len(rows) == 0:
            pass
        else:
            index = rows[0].split()
            data = pd.DataFrame(index=index)
            index_length = len(index)
            for nbrRow in range(1, len(rows)):
                row = rows[nbrRow]
                colums_of_row = row.split()
                if len(colums_of_row) != index_length:
                    continue
                data[nbrRow] = colums_of_row
            dt_date = datetime.date(date)
            dataset.update({dt_date:data})
            # datestr = str(date.year) + "-" + str(date.month) + "-" + str(date.day)
            # data.to_json(os.path.abspath('..')+ '\marketdata\\' + codename + '_mkt_' + datestr + '.json')
    return dataset

def spider_positions(codename,firstdate, enddate,tradetype):
    date_range = w.tdays(firstdate, enddate, "").Data[0]
    dataset = {}
    for i in range(len(date_range)):
        time.sleep(3)
        date = date_range[i]
        year, month, day = date.year, date.month, date.day
        url = 'http://www.dce.com.cn/publicweb/quotesdata/exportMemberDealPosiQuotesData.html?' \
            'memberDealPosiQuotes.variety='+str(codename)+\
            '&memberDealPosiQuotes.trade_type='+str(tradetype)+'&year='+str(year)+'&month='+str(month-1)+'&day='+str(day)+\
            '&contract.contract_id=all&contract.variety_id='+str(codename)+'&exportFlag=txt'

        result = geturl(url, header=randheader())
        rows = result.text.split('\n')
        result_final = []
        df = pd.DataFrame()
        flag_first = True
        if len(rows) == 0:
            pass
        else:
            index_length = 100
            for nbrRow in range(1,len(rows)):
                row = rows[nbrRow]
                if row.startswith(u'名次'):
                    if not flag_first:
                        result_final.append(df)
                        #print(df)
                    columns = row.split()
                    index_length = len(columns)
                    #print(columns)
                    df = pd.DataFrame(index=columns)
                    flag_first = False
                    #print(df)
                else:
                    colums_of_row = row.split()
                    if len(colums_of_row) != index_length: continue
                    df[nbrRow] = colums_of_row
        result_final.append(df)
        #print( [r for r in result_final ] )
        dataset.update({date:result_final})
    return dataset



# codename = 'm'
# begdate=date(2017,11,1)
# enddate=date(2017,11,1)
# #
# tradetype = 1 # 0:期货，1：期权
# ds = spider_mktdata_night(begdate, enddate,1)
# print(ds[begdate])
#
