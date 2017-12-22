from sqlalchemy import create_engine, MetaData, Table, Column,TIMESTAMP
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from WindPy import w
import datetime
import pandas as pd
from data_access import db_utilities as du
import math


class DataCollection():

    class table_options():

        def czce_daily(self,dt, data):
            db_data = []
            # print(data)
            cd_exchange = 'czce'
            datasource = 'czce'
            flag_night = -1
            for column in data.columns.values:
                product = data[column]
                product_name = product.loc['品种代码'].lower()
                dt_date = dt
                name_code = product_name[0:2]
                underlying = '1' + product_name[2:5]
                option_type = product_name[5]
                strike = product_name[-4:].replace(',', '').replace(' ', '')
                id_instrument = name_code + '_' + underlying + '_' + option_type + '_' + strike
                id_underlying = name_code + '_' + underlying
                amt_strike = float(strike)
                if option_type == 'c':
                    cd_option_type = 'call'
                else:
                    cd_option_type = 'put'
                amt_last_close = 0.0
                amt_last_settlement = product.loc['昨结算'].replace(',', '')
                amt_open = product.loc['今开盘'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['今收盘'].replace(',', '')
                amt_settlement = product.loc['今结算'].replace(',', '')
                amt_trading_volume = product.loc['成交量(手)'].replace(',', '')
                amt_trading_value = product.loc['成交额(万元)'].replace(',', '')
                amt_holding_volume = product.loc['空盘量'].replace(',', '')
                amt_bid = 0.0
                amt_ask = 0.0
                amt_exercised = product.loc['行权量'].replace(',', '')
                amt_implied_vol = product.loc['隐含波动率'].replace(',', '')
                amt_delta = product.loc['DELTA'].replace(',', '')
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument.encode('utf-8'),
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'name_code': name_code,
                          'id_underlying': id_underlying.encode('utf-8'),
                          'amt_strike': amt_strike,
                          'cd_option_type': cd_option_type.encode('utf-8'),
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_bid': amt_bid,
                          'amt_ask': amt_ask,
                          'pct_implied_vol': amt_implied_vol,
                          'amt_delta': amt_delta,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'amt_exercised': amt_exercised,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                # print(db_data)
                db_data.append(db_row)
            return db_data

        def dce_day(self,dt, data):
            db_data = []
            # print(data)
            cd_exchange = 'dce'
            datasource = 'dce'
            flag_night = 0
            for column in data.columns.values:
                product = data[column]
                product_name = product.loc['合约名称'].lower()
                dt_date = dt
                name_code = product_name[0:product_name.index('1')]
                id_underlying = name_code + '_' + product_name[product_name.index('1'):product_name.index('1') + 4]
                option_type = product_name[product_name.index('-') + 1]
                strike = product_name[-4:].replace(',', '').replace(' ', '')
                id_instrument = id_underlying + '_' + option_type + '_' + strike
                amt_strike = float(strike)
                if option_type == 'c':
                    cd_option_type = 'call'
                else:
                    cd_option_type = 'put'
                amt_last_close = 0.0
                amt_last_settlement = product.loc['前结算价'].replace(',', '')
                amt_open = product.loc['开盘价'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['收盘价'].replace(',', '')
                amt_settlement = product.loc['结算价'].replace(',', '')
                amt_trading_volume = product.loc['成交量'].replace(',', '')
                amt_trading_value = product.loc['成交额'].replace(',', '')
                amt_holding_volume = product.loc['持仓量'].replace(',', '')
                amt_bid = 0.0
                amt_ask = 0.0
                amt_exercised = product.loc['行权量'].replace(',', '')
                amt_implied_vol = 0.0
                amt_delta = product.loc['Delta'].replace(',', '')
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument.encode('utf-8'),
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'name_code': name_code,
                          'id_underlying': id_underlying.encode('utf-8'),
                          'amt_strike': amt_strike,
                          'cd_option_type': cd_option_type.encode('utf-8'),
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_bid': amt_bid,
                          'amt_ask': amt_ask,
                          'pct_implied_vol': amt_implied_vol,
                          'amt_delta': amt_delta,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'amt_exercised': amt_exercised,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                # print(db_data)
                db_data.append(db_row)
            return db_data

        def dce_night(self,dt, data):
            db_data = []
            # print(data)
            cd_exchange = 'dce'
            datasource = 'dce'
            flag_night = 1
            for column in data.columns.values:
                product = data[column]
                product_name = product.loc['合约名称'].lower()
                dt_date = dt
                name_code = product_name[0:product_name.index('1')]
                id_underlying = name_code + '_' + product_name[product_name.index('1'):product_name.index('1') + 4]
                option_type = product_name[product_name.index('-') + 1]
                strike = product_name[-4:].replace(',', '').replace(' ', '')
                id_instrument = id_underlying + '_' + option_type + '_' + strike
                amt_strike = float(strike)
                if option_type == 'c':
                    cd_option_type = 'call'
                else:
                    cd_option_type = 'put'
                amt_last_close = 0.0
                amt_last_settlement = product.loc['前结算价'].replace(',', '')
                amt_open = product.loc['开盘价'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['最新价'].replace(',', '')
                amt_settlement = 0.0
                amt_trading_volume = product.loc['成交量'].replace(',', '')
                amt_trading_value = product.loc['成交额'].replace(',', '')
                amt_holding_volume = product.loc['持仓量'].replace(',', '')
                amt_bid = 0.0
                amt_ask = 0.0
                amt_exercised = 0.0
                amt_implied_vol = 0.0
                amt_delta = 0.0
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument.encode('utf-8'),
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'name_code': name_code,
                          'id_underlying': id_underlying.encode('utf-8'),
                          'amt_strike': amt_strike,
                          'cd_option_type': cd_option_type.encode('utf-8'),
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_bid': amt_bid,
                          'amt_ask': amt_ask,
                          'pct_implied_vol': amt_implied_vol,
                          'amt_delta': amt_delta,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'amt_exercised': amt_exercised,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                # print(db_data)
                db_data.append(db_row)
            return db_data

        def wind_data_50etf_option(self,datestr):

            db_data = []
            id_underlying = 'index_50etf'
            name_code = '50etf'
            windcode_underlying = '510050.SH'
            datasource = 'wind'
            cd_exchange = 'sse'
            flag_night = -1

            optionchain = w.wset("optionchain", "date=" + datestr + ";us_code=510050.SH;option_var=全部;call_put=全部")
            df_optionchain = pd.DataFrame()
            for i, f in enumerate(optionchain.Fields):
                df_optionchain[f] = optionchain.Data[i]

            data = w.wset("optiondailyquotationstastics",
                          "startdate=" + datestr + ";enddate=" + datestr + ";exchange=sse;windcode=510050.SH")
            df_mktdatas = pd.DataFrame()
            for i1, f1 in enumerate(data.Fields):
                df_mktdatas[f1] = data.Data[i1]
            df_mktdatas = df_mktdatas.fillna(-999.0)
            for (i2, df_mktdata) in df_mktdatas.iterrows():
                dt_date = datetime.datetime.strptime(datestr, "%Y-%m-%d").date()
                windcode = df_mktdata['option_code'] + '.SH'
                criterion = df_optionchain['option_code'].map(lambda x: x == windcode)
                option_info = df_optionchain[criterion]
                amt_strike = option_info['strike_price'].values[0]
                contract_month = str(option_info['month'].values[0])[-4:]
                sec_name = option_info['option_name'].values[0]
                if option_info['call_put'].values[0] == '认购':
                    cd_option_type = 'call'
                elif option_info['call_put'].values[0] == '认沽':
                    cd_option_type = 'put'
                else:
                    cd_option_type = 'none'
                    print('error in call_or_put')
                if sec_name[-1] == 'A':
                    id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[
                                                                                                :6] + '_A'
                else:
                    id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]

                amt_last_settlement = df_mktdata['pre_settle']
                amt_open = df_mktdata['open']
                amt_high = df_mktdata['highest']
                amt_low = df_mktdata['lowest']
                amt_close = df_mktdata['close']
                amt_settlement = df_mktdata['settlement_price']
                amt_delta = df_mktdata['delta']
                amt_gamma = df_mktdata['gamma']
                amt_vega = df_mktdata['vega']
                amt_theta = df_mktdata['theta']
                amt_rho = df_mktdata['rho']
                amt_trading_volume = df_mktdata['volume']
                amt_trading_value = df_mktdata['amount']
                amt_holding_volume = df_mktdata['position']
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'name_code': name_code,
                          'id_underlying': id_underlying,
                          'amt_strike': float(amt_strike),
                          'cd_option_type': cd_option_type,
                          'amt_last_settlement': float(amt_last_settlement),
                          'amt_open': float(amt_open),
                          'amt_high': float(amt_high),
                          'amt_low': float(amt_low),
                          'amt_close': float(amt_close),
                          'amt_settlement': float(amt_settlement),
                          'amt_delta': float(amt_delta),
                          'amt_gamma': float(amt_gamma),
                          'amt_vega': float(amt_vega),
                          'amt_theta': float(amt_theta),
                          'amt_rho': float(amt_rho),
                          'amt_trading_volume': float(amt_trading_volume),
                          'amt_trading_value': float(amt_trading_value),
                          'amt_holding_volume': float(amt_holding_volume),
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data


    class table_futures():

        def dce_night(self,dt, data):
            db_data = []
            datasource = cd_exchange = 'dce'
            for column in data.columns.values:
                product = data[column]
                code_instrument = du.get_codename(product.loc['商品名称']).replace(',', '').replace(' ', '')
                codename = code_instrument.lower()
                id_instrument = codename + '_' + product.loc['交割月份']
                dt_date = dt
                flag_night = 1
                name_code = codename
                amt_last_close = 0.0
                amt_last_settlement = product.loc['前结算价'].replace(',', '')
                amt_open = product.loc['开盘价'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['最新价'].replace(',', '')
                amt_settlement = 0.0
                amt_trading_volume = product.loc['成交量'].replace(',', '')
                amt_trading_value = product.loc['成交额'].replace(',', '')
                amt_holding_volume = product.loc['持仓量'].replace(',', '')
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': code_instrument,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def dce_day(self,dt, data):
            db_data = []
            datasource = cd_exchange = 'dce'
            for column in data.columns.values:
                product = data[column]
                code_instrument = du.get_codename(product.loc['商品名称']).replace(',', '').replace(' ', '')
                codename = code_instrument.lower()
                id_instrument = codename + '_' + product.loc['交割月份']
                dt_date = dt
                flag_night = 0
                name_code = codename
                amt_last_close = 0.0
                amt_last_settlement = product.loc['前结算价'].replace(',', '')
                amt_open = product.loc['开盘价'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['收盘价'].replace(',', '')
                amt_settlement = product.loc['结算价'].replace(',', '')
                amt_trading_volume = product.loc['成交量'].replace(',', '')
                amt_trading_value = product.loc['成交额'].replace(',', '')
                amt_holding_volume = product.loc['持仓量'].replace(',', '')
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': code_instrument,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def sfe_daily(self,dt, data):
            key_map = du.key_map_sfe()
            data_dict1 = data['o_curinstrument']
            db_data = []
            datasource = cd_exchange = 'sfe'
            for dict in data_dict1:
                name = dict[key_map['codename']].replace(' ', '')
                contractmonth = dict[key_map['contractmonth']].replace(' ', '')
                if name == '总计' or contractmonth == '小计': continue
                try:
                    name_code = name[0:name.index('_')].lower()
                except:
                    print(name)
                    continue
                id_instrument = (name_code + '_' + contractmonth).encode('utf-8')
                dt_date = dt
                flag_night = -1
                amt_last_close = dict[key_map['amt_last_close']]
                amt_last_settlement = dict[key_map['amt_last_settlement']]
                amt_open = dict[key_map['amt_open']]
                amt_high = dict[key_map['amt_high']]
                amt_low = dict[key_map['amt_low']]
                amt_close = dict[key_map['amt_close']]
                amt_settlement = dict[key_map['amt_settlement']]
                amt_trading_volume = dict[key_map['amt_trading_volume']]
                amt_trading_value = 0.0
                amt_holding_volume = dict[key_map['amt_holding_volume']]
                if amt_last_close == '': amt_last_close = 0.0
                if amt_last_settlement == '': amt_last_settlement = 0.0
                if amt_open == '': amt_open = 0.0
                if amt_high == '': amt_high = 0.0
                if amt_low == '': amt_low = 0.0
                if amt_close == '': amt_close = 0.0
                if amt_settlement == '': amt_settlement = 0.0
                if amt_trading_volume == '': amt_trading_volume = 0.0
                if amt_trading_value == '': amt_trading_value = 0.0
                if amt_holding_volume == '': amt_holding_volume = 0.0

                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': name,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

        def czce_daily(self,dt, data):
            db_data = []
            # print(data)
            datasource = cd_exchange = 'czce'
            # datasource = 'czce'
            flag_night = -1
            for column in data.columns.values:
                product = data[column]
                code_instrument = product.loc['品种月份'].replace(',', '').replace(' ', '')
                product_name = product.loc['品种月份'].lower().replace(',', '').replace(' ', '')
                dt_date = dt
                name_code = product_name[:-3]
                underlying = '1' + product_name[-3:]
                id_instrument = name_code + '_' + underlying
                amt_last_close = 0.0
                amt_last_settlement = product.loc['昨结算'].replace(',', '')
                amt_open = product.loc['今开盘'].replace(',', '')
                amt_high = product.loc['最高价'].replace(',', '')
                amt_low = product.loc['最低价'].replace(',', '')
                amt_close = product.loc['今收盘'].replace(',', '')
                amt_settlement = product.loc['今结算'].replace(',', '')
                amt_trading_volume = product.loc['成交量(手)'].replace(',', '')
                amt_trading_value = product.loc['成交额(万元)'].replace(',', '')
                amt_holding_volume = 0.0
                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': code_instrument,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': amt_open,
                          'amt_high': amt_high,
                          'amt_low': amt_low,
                          'amt_close': amt_close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': amt_trading_volume,
                          'amt_trading_value': amt_trading_value,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                # print(db_data)
                db_data.append(db_row)
            return db_data

        def wind_index_future_daily(self,datestr, id_instrument, windcode):
            db_data = []
            datasource = 'wind'
            flag_night = -1
            cd_exchange = 'cfe'
            name_code = id_instrument[0:2]
            tickdata = w.wsd(windcode,
                             "pre_close,open,high,low,close,volume,amt,oi,pre_settle,settle",
                             datestr , datestr , "Fill=Previous")
            if tickdata.ErrorCode != 0:
                print('wind get data error ', datestr, ',errorcode : ', tickdata.ErrorCode)
                return []
            df = pd.DataFrame()
            for i, f in enumerate(tickdata.Fields):
                df[f] = tickdata.Data[i]
            df['dt_datetime'] = tickdata.Times
            for (idx, row) in df.iterrows():
                dt = row['dt_datetime']
                dt_date = datetime.date(dt.year, dt.month, dt.day)
                open_price = row['OPEN']
                high = row['HIGH']
                low = row['LOW']
                close = row['CLOSE']
                volume = row['VOLUME']
                amt = row['AMT']
                amt_holding_volume = row['OI']
                amt_last_close = row['PRE_CLOSE']
                amt_last_settlement = row['PRE_SETTLE']
                amt_settlement = row['SETTLE']

                db_row = {'dt_date': dt_date,
                          'id_instrument': id_instrument,
                          'flag_night': flag_night,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'name_code': name_code,
                          'amt_last_close': amt_last_close,
                          'amt_last_settlement': amt_last_settlement,
                          'amt_open': open_price,
                          'amt_high': high,
                          'amt_low': low,
                          'amt_close': close,
                          'amt_settlement': amt_settlement,
                          'amt_trading_volume': volume,
                          'amt_trading_value': amt,
                          'amt_holding_volume': amt_holding_volume,
                          'cd_exchange': cd_exchange,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data

    class table_future_contracts():

        def get_future_contract_ids(self,datestr):
            engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                                   echo=False)
            FutureContracts = dbt.Futures
            Session = sessionmaker(bind=engine)
            sess = Session()
            query = sess.query(FutureContracts.id_instrument, FutureContracts.windcode) \
                .filter(datestr >= FutureContracts.dt_listed) \
                .filter(datestr <= FutureContracts.dt_maturity)
            df_windcode = pd.read_sql(query.statement, query.session.bind)
            return df_windcode


        def wind_future_contracts(self,category_code, nbr_multiplier):
            db_data = []

            cd_exchange = 'cfe'
            data = w.wset("futurecc", "wind_code=" + category_code)
            df_contracts = pd.DataFrame()
            for i1, f1 in enumerate(data.Fields):
                df_contracts[f1] = data.Data[i1]
            df_contracts = df_contracts.fillna(-999.0)
            for (idx, df) in df_contracts.iterrows():
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


    class table_option_contracts():

        def wind_options_50etf(self):
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
                windcode = windcode + '.SH'
                name_option = sec_name[idx].encode('utf-8')
                if call_or_put[idx] == '认购':
                    cd_option_type = 'call'
                elif call_or_put[idx] == '认沽':
                    cd_option_type = 'put'
                else:
                    cd_option_type = 'none'
                    print('error in call_or_put')
                cd_exercise_type = exercise_mode[idx].encode('utf-8')
                dt_maturity = expire_date[idx].date()
                name_contract_month = dt_maturity.strftime("%y%m")
                amt_strike = exercise_price[idx]
                if sec_name[idx][-1] == 'A':
                    id_instrument = '50etf_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[
                                                                                                     :6] + '_A'
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

        def wind_options_m(self):
            db_data = []
            name_code = 'm'
            cd_exchange = 'dce'
            data = w.wset("optionfuturescontractbasicinfo", "exchange=DCE;productcode=M;contract=all")
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
                windcode = windcode + '.DCE'
                name_option = sec_name[idx].encode('utf-8')
                if call_or_put[idx] == '认购':
                    cd_option_type = 'call'
                elif call_or_put[idx] == '认沽':
                    cd_option_type = 'put'
                else:
                    cd_option_type = 'none'
                    print('error in call_or_put')
                cd_exercise_type = exercise_mode[idx].encode('utf-8')
                name_contract_month = datetime.datetime.strptime(limit_month[idx], "%Y-%m").date().strftime("%y%m")
                amt_strike = exercise_price[idx]
                id_instrument = name_code + '_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(
                    int(amt_strike))
                id_underlying = name_code + '_' + name_contract_month
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

        def wind_options_sr(self):
            db_data = []
            name_code = 'sr'
            cd_exchange = 'czce'
            data = w.wset("optionfuturescontractbasicinfo", "exchange=CZCE;productcode=SR;contract=all")
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
                windcode = windcode + '.CZC'
                name_option = sec_name[idx].encode('utf-8')
                if call_or_put[idx] == '认购':
                    cd_option_type = 'call'
                elif call_or_put[idx] == '认沽':
                    cd_option_type = 'put'
                else:
                    cd_option_type = 'none'
                    print('error in call_or_put')
                cd_exercise_type = exercise_mode[idx].encode('utf-8')
                name_contract_month = datetime.datetime.strptime(limit_month[idx], "%Y-%m").date().strftime("%y%m")
                amt_strike = exercise_price[idx]
                id_instrument = name_code + '_' + name_contract_month + '_' + cd_option_type[0] + '_' + str(
                    int(amt_strike))
                id_underlying = name_code + '_' + name_contract_month
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


    class table_index():

        def wind_data_index(self,windcode, date, id_instrument):
            db_data = []
            datasource = 'wind'
            data = w.wsd(windcode, "open,high,low,close,volume,amt",
                         date, date, "Fill=Previous")
            df = pd.DataFrame()
            for i, f in enumerate(data.Fields):
                df[f] = data.Data[i]
            df['times'] = data.Times
            for (idx, row) in df.iterrows():
                open_price = row['OPEN']
                dt = row['times']
                high = row['HIGH']
                low = row['LOW']
                close = row['CLOSE']
                volume = row['VOLUME']
                amt = row['AMT']
                db_row = {'dt_date': dt,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_close': close,
                          'amt_open': open_price,
                          'amt_high': high,
                          'amt_low': low,
                          'amt_trading_volume': volume,
                          'amt_trading_value': amt,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data


    class table_index_intraday():

        def wind_data_equity_index(self,windcode, date, id_instrument):
            db_data = []
            datasource = 'wind'
            data = w.wsi(windcode, "close,volume,amt", date + " 09:00:00", date + " 15:01:00", "Fill=Previous")
            datetimes = data.Times
            prices = data.Data[0]
            volumes = data.Data[1]
            trading_values = data.Data[2]
            for idx, dt in enumerate(datetimes):
                price = prices[idx]
                volume = volumes[idx]
                trading_value = trading_values[idx]
                db_row = {'dt_datetime': dt,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_price': price,
                          'amt_trading_volume': volume,
                          'amt_trading_value': trading_value,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data


    class table_option_intraday():

        def wind_data_50etf_option_intraday(self,datestr, df_optionchain_row):
            db_data = []
            datasource = 'wind'
            windcode = df_optionchain_row['option_code']
            amt_strike = df_optionchain_row['strike_price']
            contract_month = str(df_optionchain_row['month'])[-4:]
            sec_name = df_optionchain_row['option_name']
            if df_optionchain_row['call_put'] == '认购':
                cd_option_type = 'call'
            elif df_optionchain_row['call_put'] == '认沽':
                cd_option_type = 'put'
            if sec_name[-1] == 'A':
                id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6] + '_A'
            else:
                id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]
            data = w.wsi(windcode, "close,volume,amt", datestr + " 09:00:00", datestr + " 15:01:00", "Fill=Previous")
            datetimes = data.Times
            prices = data.Data[0]
            volumes = data.Data[1]
            trading_values = data.Data[2]
            for idx, dt in enumerate(datetimes):
                price = prices[idx]
                volume = volumes[idx]
                trading_value = trading_values[idx]
                if math.isnan(price): continue
                if math.isnan(volume): volume = 0.0
                if math.isnan(trading_value): trading_value = 0.0
                db_row = {'dt_datetime': dt,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_price': price,
                          'amt_trading_volume': volume,
                          'amt_trading_value': trading_value,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data


    class table_option_tick():

        def wind_option_chain(self,datestr):
            optionchain = w.wset("optionchain", "date=" + datestr + ";us_code=510050.SH;option_var=全部;call_put=全部")
            df_optionchain = pd.DataFrame()
            for i, f in enumerate(optionchain.Fields):
                df_optionchain[f] = optionchain.Data[i]
            return df_optionchain

        def wind_50etf_option_tick(self,datestr, df_optionchain_row):
            db_data = []
            datasource = 'wind'
            windcode = df_optionchain_row['option_code']
            amt_strike = df_optionchain_row['strike_price']
            contract_month = str(df_optionchain_row['month'])[-4:]
            sec_name = df_optionchain_row['option_name']
            if df_optionchain_row['call_put'] == '认购':
                cd_option_type = 'call'
            elif df_optionchain_row['call_put'] == '认沽':
                cd_option_type = 'put'
            if sec_name[-1] == 'A':
                id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6] + '_A'
            else:
                id_instrument = '50etf_' + contract_month + '_' + cd_option_type[0] + '_' + str(amt_strike)[:6]
            tickdata = w.wst(windcode,
                             "last,volume,amt,oi,limit_up,limit_down,ask1,ask2,ask3,ask4,ask5,bid1,bid2,bid3,bid4,bid5",
                             datestr + " 09:25:00", datestr + " 15:01:00", "")
            if tickdata.ErrorCode != 0:
                print('wind get data error ', datestr, ',errorcode : ', tickdata.ErrorCode)
                return []
            df_tickdata = pd.DataFrame()
            for i, f in enumerate(tickdata.Fields):
                df_tickdata[f] = tickdata.Data[i]
            df_tickdata['dt_datetime'] = tickdata.Times
            df_tickdata = df_tickdata.fillna(0.0)
            last_datetime = None
            for (idx, row_tickdata) in df_tickdata.iterrows():
                dt = row_tickdata['dt_datetime']
                dt_datetime = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                if dt_datetime == last_datetime: continue
                last_datetime = dt_datetime
                price = row_tickdata['last']
                volume = row_tickdata['volume']
                trading_value = row_tickdata['amount']
                position = row_tickdata['position']
                amt_bid1 = row_tickdata['bid1']
                amt_ask1 = row_tickdata['ask1']
                amt_bid2 = row_tickdata['bid2']
                amt_ask2 = row_tickdata['ask2']
                amt_bid3 = row_tickdata['bid3']
                amt_ask3 = row_tickdata['ask3']
                amt_bid4 = row_tickdata['bid4']
                amt_ask4 = row_tickdata['ask4']
                amt_bid5 = row_tickdata['bid5']
                amt_ask5 = row_tickdata['ask5']
                db_row = {'dt_datetime': dt_datetime,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_price': price,
                          'amt_trading_volume': volume,
                          'amt_trading_value': trading_value,
                          'amt_holding_volume': position,
                          'amt_bid1': amt_bid1,
                          'amt_ask1': amt_ask1,
                          'amt_bid2': amt_bid2,
                          'amt_ask2': amt_ask2,
                          'amt_bid3': amt_bid3,
                          'amt_ask3': amt_ask3,
                          'amt_bid4': amt_bid4,
                          'amt_ask4': amt_ask4,
                          'amt_bid5': amt_bid5,
                          'amt_ask5': amt_ask5,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data


    class table_future_tick():


        def wind_index_future_tick(self,datestr, id_instrument, windcode):
            db_data = []
            datasource = 'wind'
            tickdata = w.wst(windcode,
                             "last,volume,amt,oi,limit_up,limit_down,ask1,ask2,ask3,ask4,ask5,"
                             "bid1,bid2,bid3,bid4,bid5", datestr + " 09:25:00", datestr + " 15:01:00", "")
            if tickdata.ErrorCode != 0:
                print('wind get data error ', datestr, ',errorcode : ', tickdata.ErrorCode)
                return []
            df_tickdata = pd.DataFrame()
            for i, f in enumerate(tickdata.Fields):
                df_tickdata[f] = tickdata.Data[i]
            df_tickdata['dt_datetime'] = tickdata.Times
            df_tickdata = df_tickdata.fillna(0.0)
            last_datetime = None
            for (idx, row_tickdata) in df_tickdata.iterrows():
                dt = row_tickdata['dt_datetime']
                dt_datetime = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
                if dt_datetime == last_datetime: continue
                last_datetime = dt_datetime
                price = row_tickdata['last']
                volume = row_tickdata['volume']
                trading_value = row_tickdata['amount']
                position = row_tickdata['position']
                amt_bid1 = row_tickdata['bid1']
                amt_ask1 = row_tickdata['ask1']
                amt_bid2 = row_tickdata['bid2']
                amt_ask2 = row_tickdata['ask2']
                amt_bid3 = row_tickdata['bid3']
                amt_ask3 = row_tickdata['ask3']
                amt_bid4 = row_tickdata['bid4']
                amt_ask4 = row_tickdata['ask4']
                amt_bid5 = row_tickdata['bid5']
                amt_ask5 = row_tickdata['ask5']
                db_row = {'dt_datetime': dt_datetime,
                          'id_instrument': id_instrument,
                          'datasource': datasource,
                          'code_instrument': windcode,
                          'amt_price': price,
                          'amt_trading_volume': volume,
                          'amt_trading_value': trading_value,
                          'amt_holding_volume': position,
                          'amt_bid1': amt_bid1,
                          'amt_ask1': amt_ask1,
                          'amt_bid2': amt_bid2,
                          'amt_ask2': amt_ask2,
                          'amt_bid3': amt_bid3,
                          'amt_ask3': amt_ask3,
                          'amt_bid4': amt_bid4,
                          'amt_ask4': amt_ask4,
                          'amt_bid5': amt_bid5,
                          'amt_ask5': amt_ask5,
                          'timestamp': datetime.datetime.today()
                          }
                db_data.append(db_row)
            return db_data


    class table_future_positions():

        def dce_data(self, dt, name_code, data_list):
            db_data = []
            types = ['trading_volume', 'holding_volume_buy', 'holding_volume_sell']
            type_index = ['成交量', '持买单量', '持卖单量']
            for i, data in enumerate(data_list):
                for column in data.columns.values:
                    product = data[column]
                    dt_date = dt
                    id_instrument = name_code + '_all'
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

        def sfe_data(self, dt, data):
            # types = ['trading_volume', 'holding_volume_buy', 'holding_volume_sell']
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
                # nbr_rank = dict['RANK']
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
                # nbr_rank = dict['RANK']
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







