
def code_map_dce():
    map = {'豆一':'a',
           '豆二':'b',
           '胶合板':'bb',
           '玉米':'c',
           '玉米淀粉':'cs',
           '纤维板':'fb',
           '铁矿石': 'i',
           '焦炭': 'j',
           '鸡蛋': 'jd',
           '焦煤': 'jm',
           '聚乙烯': 'l',
           '豆粕': 'm',
           '棕榈油': 'p',
           '聚丙烯': 'pp',
           '聚氯乙烯': 'v',
           '豆油': 'y',
    }
    return map

def get_codename(name):
    map = code_map_dce()

    return map.get(name)

def key_map_sfe():
    map = {
        'codename':u'PRODUCTID',
        'contractmonth':u'DELIVERYMONTH',
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
    return map