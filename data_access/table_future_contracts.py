from sqlalchemy import create_engine, MetaData, Table, Column
from WindPy import w
import datetime
import pandas as pd


def wind_future_contracts(category_code,nbr_multiplier):
    db_data = []

    cd_exchange = 'cfe'
    data = w.wset("futurecc","wind_code="+category_code)
    df_contracts = pd.DataFrame()
    for i1, f1 in enumerate(data.Fields):
        df_contracts[f1] = data.Data[i1]
    df_contracts = df_contracts.fillna(-999.0)
    for (idx,df) in df_contracts.iterrows():

        windcode = df['wind_code']
        name_instrument = df['sec_name'].encode('utf-8')
        name_code = df['code'][0:2]
        name_contract_month = df['code'][2:]
        pct_margin = df['target_margin']
        pct_change_limit = df['change_limit']
        dt_listed = df['contract_issue_date'].date()
        dt_maturity = df['last_trade_date'].date()
        dt_settlement = df['last_delivery_mouth'].date()
        id_instrument = name_code + '_' + name_contract_month

        db_row = {'id_instrument': id_instrument,
                  'windcode': windcode,
                  'name_instrument': name_instrument,
                  'name_code': name_code,
                  'name_contract_month': name_contract_month,
                  'pct_margin': pct_margin,
                  'pct_change_limit': pct_change_limit,
                  'dt_listed': dt_listed,
                  'dt_maturity': dt_maturity,
                  'dt_settlement': dt_settlement,
                  'nbr_multiplier': nbr_multiplier,
                  'cd_exchange': cd_exchange,
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data


#
# w.start()
# data = w.wset("optioncontractbasicinfo", "exchange=sse;windcode=510050.SH;status=all")
# # print(data.Fields)
# for f in data.Fields:
#     print(f)
# optionData = data.Data
# optionFlds = data.Fields
# # print(data)
# wind_code = optionData[optionFlds.index('wind_code')]
# trade_code = optionData[optionFlds.index('trade_code')]
# sec_name = optionData[optionFlds.index('sec_name')]
# option_mark_code = optionData[optionFlds.index('option_mark_code')]
# option_type = optionData[optionFlds.index('option_type')]
# call_or_put = optionData[optionFlds.index('call_or_put')]
# exercise_mode = optionData[optionFlds.index('exercise_mode')]
# exercise_price = optionData[optionFlds.index('exercise_price')]
# contract_unit = optionData[optionFlds.index('contract_unit')]
# limit_month = optionData[optionFlds.index('limit_month')]
# listed_date = optionData[optionFlds.index('listed_date')]
# expire_date = optionData[optionFlds.index('expire_date')]
# exercise_date = optionData[optionFlds.index('exercise_date')]
# settlement_date = optionData[optionFlds.index('settlement_date')]
# settle_mode = optionData[optionFlds.index('settle_mode')]
