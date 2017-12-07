from sqlalchemy import create_engine, MetaData, Table, Column
from WindPy import w
import datetime

def wind_codes():
    db_data = []
    data = w.wset("optioncontractbasicinfo", "exchange=sse;windcode=510050.SH;status=all")
    optionData = data.Data
    optionFlds = data.Fields
    wind_code = optionData[optionFlds.index('wind_code')]
    sec_name = optionData[optionFlds.index('sec_name')]
    call_or_put = optionData[optionFlds.index('call_or_put')]
    exercise_price = optionData[optionFlds.index('exercise_price')]
    expire_date = optionData[optionFlds.index('expire_date')]
    for idx, windcode in enumerate(wind_code):
        windcode = windcode+'.SH'
        if call_or_put[idx] == '认购' : cd_option_type = 'call'
        elif call_or_put[idx] == '认沽' : cd_option_type = 'put'
        else :
            cd_option_type = 'none'
            print('error in call_or_put')
        dt_maturity = expire_date[idx].date()
        name_contract_month = dt_maturity.strftime("%y%m")
        amt_strike = exercise_price[idx]
        if sec_name[idx][-1] == 'A':
            id_instrument = '50etf_'+name_contract_month+'_'+ cd_option_type[0]+'_'+str(amt_strike)[:6]+'_A'
        else:
            id_instrument = '50etf_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]

        db_row = {'windcode': windcode,
                  'id_instrument': id_instrument,
                  }
        db_data.append(db_row)
    return db_data


def wind_options_50etf():
    db_data = []
    id_underlying = 'index_50etf'
    windcode_underlying = '510050.SH'

    cd_exchange = 'sse'
    data = w.wset("optioncontractbasicinfo", "exchange=sse;windcode=510050.SH;status=all")
    optionData = data.Data
    optionFlds = data.Fields

    wind_code = optionData[optionFlds.index('wind_code')]
    trade_code = optionData[optionFlds.index('trade_code')]
    sec_name = optionData[optionFlds.index('sec_name')]
    option_mark_code = optionData[optionFlds.index('option_mark_code')]
    call_or_put = optionData[optionFlds.index('call_or_put')]
    exercise_mode = optionData[optionFlds.index('exercise_mode')]
    exercise_price = optionData[optionFlds.index('exercise_price')]
    contract_unit = optionData[optionFlds.index('contract_unit')]
    limit_month = optionData[optionFlds.index('limit_month')]
    listed_date = optionData[optionFlds.index('listed_date')]
    expire_date = optionData[optionFlds.index('expire_date')]
    exercise_date = optionData[optionFlds.index('exercise_date')]
    settlement_date = optionData[optionFlds.index('settlement_date')]
    settle_mode = optionData[optionFlds.index('settle_mode')]

    for idx, windcode in enumerate(wind_code):
        windcode = windcode+'.SH'
        name_option = sec_name[idx].encode('utf-8')
        if call_or_put[idx] == '认购' : cd_option_type = 'call'
        elif call_or_put[idx] == '认沽' : cd_option_type = 'put'
        else :
            cd_option_type = 'none'
            print('error in call_or_put')
        cd_exercise_type = exercise_mode[idx].encode('utf-8')
        dt_maturity = expire_date[idx].date()
        name_contract_month = dt_maturity.strftime("%y%m")
        amt_strike = exercise_price[idx]
        if sec_name[idx][-1] == 'A':
            id_instrument = '50etf_'+name_contract_month+'_'+ cd_option_type[0]+'_'+str(amt_strike)[:6]+'_A'
        else:
            id_instrument = '50etf_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]

        dt_listed = listed_date[idx]
        dt_maturity = expire_date[idx]
        dt_exercise = datetime.datetime.strptime(exercise_date[idx], "%Y-%m-%d").date()
        dt_settlement = datetime.datetime.strptime(settlement_date[idx], "%Y-%m-%d").date()
        cd_settle_method = settle_mode[idx].encode('utf-8')
        nbr_multiplier = contract_unit[idx]

        db_row = {'id_instrument': id_instrument,
                  'windcode': windcode,
                  'name_option': name_option,
                  'id_underlying': id_underlying,
                  'windcode_underlying': windcode_underlying,
                  'cd_option_type': cd_option_type,
                  'cd_exercise_type': cd_exercise_type,
                  'amt_strike': amt_strike,
                  'name_contract_month': name_contract_month,
                  'dt_listed': dt_listed,
                  'dt_maturity': dt_maturity,
                  'dt_exercise': dt_exercise,
                  'dt_settlement': dt_settlement,
                  'cd_settle_method': cd_settle_method,
                  'nbr_multiplier': nbr_multiplier,
                  'cd_exchange': cd_exchange,
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data


def wind_options_m():
    db_data = []
    name_code = 'm'
    cd_exchange = 'dce'
    data = w.wset("optionfuturescontractbasicinfo","exchange=DCE;productcode=M;contract=all")
    optionData = data.Data
    optionFlds = data.Fields

    wind_code = optionData[optionFlds.index('wind_code')]
    sec_name = optionData[optionFlds.index('sec_name')]
    option_mark_code = optionData[optionFlds.index('option_mark_code')]
    call_or_put = optionData[optionFlds.index('call_or_put')]
    exercise_mode = optionData[optionFlds.index('exercise_mode')]
    exercise_price = optionData[optionFlds.index('exercise_price')]
    contract_unit = optionData[optionFlds.index('contract_unit')]
    limit_month = optionData[optionFlds.index('limit_month')]
    listed_date = optionData[optionFlds.index('listed_date')]
    expire_date = optionData[optionFlds.index('expire_date')]
    settle_mode = optionData[optionFlds.index('settle_mode')]

    for idx, windcode in enumerate(wind_code):
        windcode = windcode+'.DCE'
        name_option = sec_name[idx].encode('utf-8')
        if call_or_put[idx] == '认购' : cd_option_type = 'call'
        elif call_or_put[idx] == '认沽' : cd_option_type = 'put'
        else :
            cd_option_type = 'none'
            print('error in call_or_put')
        cd_exercise_type = exercise_mode[idx].encode('utf-8')
        name_contract_month = datetime.datetime.strptime(limit_month[idx], "%Y-%m").date().strftime("%y%m")
        amt_strike = exercise_price[idx]
        id_instrument = name_code+'_'+name_contract_month+'_'+cd_option_type[0]+'_'+str(int(amt_strike))
        id_underlying = name_code+'_'+name_contract_month
        windcode_underlying = option_mark_code[idx]
        dt_listed = listed_date[idx]
        dt_maturity = expire_date[idx]
        cd_settle_method = settle_mode[idx].encode('utf-8')
        nbr_multiplier = contract_unit[idx]

        db_row = {'id_instrument': id_instrument,
                  'windcode': windcode,
                  'name_option': name_option,
                  'id_underlying': id_underlying,
                  'windcode_underlying': windcode_underlying,
                  'cd_option_type': cd_option_type,
                  'cd_exercise_type': cd_exercise_type,
                  'amt_strike': amt_strike,
                  'name_contract_month': name_contract_month,
                  'dt_listed': dt_listed,
                  'dt_maturity': dt_maturity,
                  'cd_settle_method': cd_settle_method,
                  'nbr_multiplier': nbr_multiplier,
                  'cd_exchange': cd_exchange,
                  'timestamp': datetime.datetime.today()
                  }
        db_data.append(db_row)
    return db_data

def wind_options_sr():
    db_data = []
    name_code = 'sr'
    cd_exchange = 'czce'
    data = w.wset("optionfuturescontractbasicinfo","exchange=CZCE;productcode=SR;contract=all")
    optionData = data.Data
    optionFlds = data.Fields

    wind_code = optionData[optionFlds.index('wind_code')]
    sec_name = optionData[optionFlds.index('sec_name')]
    option_mark_code = optionData[optionFlds.index('option_mark_code')]
    call_or_put = optionData[optionFlds.index('call_or_put')]
    exercise_mode = optionData[optionFlds.index('exercise_mode')]
    exercise_price = optionData[optionFlds.index('exercise_price')]
    contract_unit = optionData[optionFlds.index('contract_unit')]
    limit_month = optionData[optionFlds.index('limit_month')]
    listed_date = optionData[optionFlds.index('listed_date')]
    expire_date = optionData[optionFlds.index('expire_date')]
    settle_mode = optionData[optionFlds.index('settle_mode')]

    for idx, windcode in enumerate(wind_code):
        windcode = windcode+'.CZC'
        name_option = sec_name[idx].encode('utf-8')
        if call_or_put[idx] == '认购' : cd_option_type = 'call'
        elif call_or_put[idx] == '认沽' : cd_option_type = 'put'
        else :
            cd_option_type = 'none'
            print('error in call_or_put')
        cd_exercise_type = exercise_mode[idx].encode('utf-8')
        name_contract_month = datetime.datetime.strptime(limit_month[idx], "%Y-%m").date().strftime("%y%m")
        amt_strike = exercise_price[idx]
        id_instrument = name_code+'_'+name_contract_month+'_'+cd_option_type[0]+'_'+str(int(amt_strike))
        id_underlying = name_code+'_'+name_contract_month
        windcode_underlying = option_mark_code[idx]
        dt_listed = listed_date[idx]
        dt_maturity = expire_date[idx]
        cd_settle_method = settle_mode[idx].encode('utf-8')
        nbr_multiplier = contract_unit[idx]

        db_row = {'id_instrument': id_instrument,
                  'windcode': windcode,
                  'name_option': name_option,
                  'id_underlying': id_underlying,
                  'windcode_underlying': windcode_underlying,
                  'cd_option_type': cd_option_type,
                  'cd_exercise_type': cd_exercise_type,
                  'amt_strike': amt_strike,
                  'name_contract_month': name_contract_month,
                  'dt_listed': dt_listed,
                  'dt_maturity': dt_maturity,
                  'cd_settle_method': cd_settle_method,
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
