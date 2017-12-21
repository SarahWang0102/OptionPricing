# -*- coding: utf-8 -*-

from sqlalchemy import create_engine, MetaData, Table, Column, TIMESTAMP
import datetime
import pandas as pd
import os
from data_access import db_utilities as du
from data_access import spider_api_dce as dce
from data_access import spider_api_sfe as sfe

def dce_data(dt, name_code, data_list):
    db_data = []
    types = ['trading_volume', 'holding_volume_buy', 'holding_volume_sell']
    type_index = ['成交量', '持买单量', '持卖单量']
    for i, data in enumerate(data_list):
        for column in data.columns.values:
            product = data[column]
            dt_date = dt
            id_instrument = name_code+'_all'
            cd_positions_type = types[i]
            nbr_rank = int(product.loc['名次'])
            name_company = product.loc['会员简称'].replace(' ', '').encode('utf-8')
            amt_volume = product.loc[type_index[i]].replace(',', '')
            amt_difference = product.loc['增减'].replace(',', '')
            db_row = {'dt_date': dt_date,
                      'cd_positions_type': cd_positions_type,
                      'id_instrument': id_instrument,
                      'nbr_rank': nbr_rank,
                      'name_company': name_company,
                      'amt_volume': amt_volume,
                      'amt_difference': amt_difference,
                      'cd_exchange': 'dce',
                      'timestamp': datetime.datetime.today()
                      }
            db_data.append(db_row)
    return db_data


def sfe_data(dt, data):
    #types = ['trading_volume', 'holding_volume_buy', 'holding_volume_sell']
    data_dict = data['o_cursor']
    db_data = []
    for dict in data_dict:
        instrumentid = dict['INSTRUMENTID'].replace(' ', '')
        try:
            if instrumentid[-3:] == 'all':
                id_instrument = instrumentid[0:-3] + '_' + 'all'
            else:
                name_code = instrumentid[0:instrumentid.index('1')]
                contractmonth = instrumentid[-4:]
                id_instrument = name_code + '_' + contractmonth
        except:
            print(instrumentid)
            continue
        dt_date = dt

        cd_positions_type = 'trading_volume'
        nbr_rank = dict['RANK']
        name_company = dict['PARTICIPANTABBR1'].encode('utf-8')
        amt_volume = dict['CJ1']
        amt_difference = dict['CJ1_CHG']
        if amt_volume == '': amt_volume = 0.0
        if amt_difference == '': amt_difference = 0.0
        db_row = {'dt_date': dt_date,
                  'cd_positions_type': cd_positions_type,
                  'id_instrument': id_instrument,
                  'nbr_rank': nbr_rank,
                  'name_company': name_company,
                  'amt_volume': amt_volume,
                  'amt_difference': amt_difference,
                  'cd_exchange': 'sfe',
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
        cd_positions_type = 'holding_volume_buy'
        #nbr_rank = dict['RANK']
        name_company = dict['PARTICIPANTABBR2'].encode('utf-8')
        amt_volume = dict['CJ2']
        amt_difference = dict['CJ2_CHG']
        if amt_volume == '': amt_volume = 0.0
        if amt_difference == '': amt_difference = 0.0
        db_row = {'dt_date': dt_date,
                  'cd_positions_type': cd_positions_type,
                  'id_instrument': id_instrument,
                  'nbr_rank': nbr_rank,
                  'name_company': name_company,
                  'amt_volume': amt_volume,
                  'amt_difference': amt_difference,
                  'cd_exchange': 'sfe',
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
        cd_positions_type = 'holding_volume_sell'
        #nbr_rank = dict['RANK']
        name_company = dict['PARTICIPANTABBR3'].encode('utf-8')
        amt_volume = dict['CJ3']
        amt_difference = dict['CJ3_CHG']
        if amt_volume == '': amt_volume = 0.0
        if amt_difference == '': amt_difference = 0.0
        db_row = {'dt_date': dt_date,
                  'cd_positions_type': cd_positions_type,
                  'id_instrument': id_instrument.lower(),
                  'nbr_rank': nbr_rank,
                  'name_company': name_company,
                  'amt_volume': amt_volume,
                  'amt_difference': amt_difference,
                  'cd_exchange': 'sfe',
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data
