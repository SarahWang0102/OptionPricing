from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import datetime
from decimal import Decimal
import pandas as pd
from WindPy import w
from data_access.db_tables import DataBaseTables as dbt

w.start()
engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
options_mkt = Table('options_mktdata', metadata, autoload=True)
futures_mkt = Table('futures_mktdata', metadata, autoload=True)
options = Table('option_contracts', metadata, autoload=True)
Future_mkt = dbt.FutureMkt
Option_mkt = dbt.OptionMkt
Options_c = dbt.Options

# Eval Settings
start_date = datetime.date(2017, 3, 31)
end_date = datetime.date(2017, 6, 5)
flagNight = 0
nameCode = 'm'
exchange = 'dce'
core_contracts = ['m_1709', 'm_1801', 'm_1805','m_1809','m_1901']
contract_maturities = {'m_1709': datetime.date(2017,7,25),
                   'm_1801': datetime.date(2017,11,24),
                   'm_1805': datetime.date(2018,3,26)}

results_list = []

for d_k_plus in [50,100,150]:
    d_k_minus = d_k_plus-200

    eval_dates = w.tdays(start_date.strftime('%Y-%m-%d'),end_date.strftime('%Y-%m-%d'),"").Data[0]
    for evalDate in eval_dates:
        evalDate = evalDate.date()
        # evalDate = start_date
        maturity_date = w.tdaysoffset(6,evalDate,"Period=M").Data[0][0].date()
        evalDate_str = evalDate.strftime("%Y-%m-%d")
        optiondata_df = pd.DataFrame()
        optiondata_atm_df = pd.DataFrame()
        optiondataset = sess.query(Option_mkt, Future_mkt) \
            .outerjoin(Future_mkt, Option_mkt.id_underlying == Future_mkt.id_instrument) \
            .filter(Option_mkt.dt_date == evalDate_str) \
            .filter(Future_mkt.dt_date == evalDate_str) \
            .filter(Option_mkt.datasource == exchange) \
            .filter(Option_mkt.flag_night == flagNight) \
            .filter(Future_mkt.flag_night == flagNight) \
            .filter(or_(Option_mkt.id_underlying == core_contracts[0],
                        Option_mkt.id_underlying == core_contracts[1],
                        Option_mkt.id_underlying == core_contracts[2],
                        )) \
            .all()

        idx_o = 0
        for optiondata in optiondataset:
            # if optiondata.Options.cd_option_type == 'put': continue
            # if optiondata.Options.name_contract_month not in contracts: continue
            optiondata_df.loc[idx_o, 'date'] = evalDate_str
            optiondata_df.loc[idx_o, 'id_instrument'] = optiondata.OptionMkt.id_instrument
            optiondata_df.loc[idx_o, 'id_underlying'] = optiondata.OptionMkt.id_underlying
            optiondata_df.loc[idx_o, 'option_type'] = optiondata.OptionMkt.cd_option_type
            optiondata_df.loc[idx_o, 'option_close'] = float(optiondata.OptionMkt.amt_close)
            optiondata_df.loc[idx_o, 'strike'] = float(optiondata.OptionMkt.amt_strike)
            optiondata_df.loc[idx_o, 'underlying_price'] = float(optiondata.FutureMkt.amt_close)
            optiondata_df.loc[idx_o, 'atm_dif'] = abs(
                optiondata.OptionMkt.amt_strike - optiondata.FutureMkt.amt_close)
            idx_o += 1

        # Construct Bull Spread Strategy [Call Option]
        option_type = 'call'
        # core_id = 'm_1709'
        # if evalDate > datetime.date(2017,6,25) : core_id = 'm_1801'
        # elif evalDate > datetime.date(2017,10,24) : core_id = 'm_1805'
        core_id = 'm_1801'
        if maturity_date > datetime.date(2017,11,24) :core_id = 'm_1805'

        id_underlying = core_id
        contract_maturity = contract_maturities[core_id]

        c_1 = optiondata_df['id_underlying'].map(lambda x:x==core_id)
        c_2 = optiondata_df['option_type'].map(lambda x:x==option_type)
        criterion = c_1 & c_2
        coredata_df = optiondata_df[criterion]
        idx = coredata_df['atm_dif'].idxmin()
        strike_atm = coredata_df.loc[idx]['strike']
        future_price = coredata_df.loc[idx]['underlying_price']
        # print(strike_atm)

        strike_otm2 = strike_atm + d_k_plus
        strike_itm2 = strike_atm + d_k_minus

        # print(strike_otm2,strike_itm2)

        price_otm2 = coredata_df.ix[coredata_df['strike']==strike_otm2,'option_close'].values[0]

        price_itm2 = coredata_df.ix[coredata_df['strike']==strike_itm2,'option_close'].values[0]
        # print(price_otm2,price_itm2)
        portfolio_cost = price_itm2 - price_otm2
        init_cost = portfolio_cost
        # print('portfolio_cost',portfolio_cost)
        # print('contract_maturity:',contract_maturity)
        date_range = w.tdays(evalDate.strftime('%Y-%m-%d'),maturity_date.strftime('%Y-%m-%d')).Data[0]
        week_b_cmdt = w.tdaysoffset(-1, contract_maturity, "Period=W").Data[0][0]
        # print(date_range)
        for date in date_range:
            date = date.date()
            date_str = date.strftime('%Y-%m-%d')
            # if date == week_b_cmdt:
            if date == contract_maturity and date != maturity_date:
                # 移仓换月
                # print('change portfolio contract month',date,contract_maturity,maturity_date)
                core_id2 = core_contracts[core_contracts.index(core_id)+1]
                id_underlying = core_id2
                query = sess.query(Option_mkt.id_underlying,Option_mkt.amt_strike,Option_mkt.amt_close) \
                    .filter(Option_mkt.dt_date == date_str) \
                    .filter(Option_mkt.datasource == exchange) \
                    .filter(or_(Option_mkt.id_underlying == core_id,
                                Option_mkt.id_underlying == core_id2)) \
                    .filter(Option_mkt.flag_night == flagNight) \
                    .filter(Option_mkt.cd_option_type == option_type) \
                    .filter(or_(Option_mkt.amt_strike == Decimal(strike_otm2),
                                Option_mkt.amt_strike == Decimal(strike_itm2)))

                df = pd.read_sql(query.statement, query.session.bind)
                # print('change contracts')
                # print(df)
                price_otm2_old = df.ix[df['id_underlying']==core_id].ix[df['amt_strike'] == Decimal(strike_otm2)]['amt_close'].values[0]
                price_itm2_old = df.ix[df['id_underlying']==core_id].ix[df['amt_strike'] == Decimal(strike_itm2)]['amt_close'].values[0]
                price_otm2_new = df.ix[df['id_underlying'] == core_id2].ix[df['amt_strike'] == Decimal(strike_otm2)]['amt_close'].values[0]
                price_itm2_new = df.ix[df['id_underlying'] == core_id2].ix[df['amt_strike'] == Decimal(strike_itm2)]['amt_close'].values[0]

                # print(price_otm2_old,price_itm2_old)
                rebalancing_cost = price_itm2_new - price_otm2_new - (price_itm2_old - price_otm2_old)
                portfolio_cost += rebalancing_cost
                # print(rebalancing_cost)
                # print(portfolio_cost)

            if date == maturity_date:
                query = sess.query(Option_mkt.id_underlying,Option_mkt.amt_strike,Option_mkt.amt_close) \
                    .filter(Option_mkt.dt_date == date_str) \
                    .filter(Option_mkt.datasource == exchange) \
                    .filter(Option_mkt.id_underlying == id_underlying) \
                    .filter(Option_mkt.flag_night == flagNight) \
                    .filter(Option_mkt.cd_option_type == option_type) \
                    .filter(or_(Option_mkt.amt_strike == Decimal(strike_otm2),
                                Option_mkt.amt_strike == Decimal(strike_itm2)))

                df = pd.read_sql(query.statement, query.session.bind)
                # print('change contracts')
                # print(df)
                price_otm2_m = df.ix[df['id_underlying'] == id_underlying].ix[df['amt_strike'] == Decimal(strike_otm2)]['amt_close'].values[0]
                price_itm2_m = df.ix[df['id_underlying'] == id_underlying].ix[df['amt_strike'] == Decimal(strike_itm2)]['amt_close'].values[0]
                # print(price_otm2_m,price_itm2_m)
                v = price_itm2_m - price_otm2_m
                earning = v-portfolio_cost
                r = (earning-portfolio_cost)*100.0/init_cost
                # print(evalDate,maturity_date,init_cost,'earning',earning,r,'%')
                results_list.append({'date':evalDate,
                                'strikes1':'+'+str(d_k_plus),
                                'strikes2':'-'+str(d_k_minus),
                                'init_cost':init_cost,
                                'earning':earning,
                                'future_price':future_price,
                                'yields':r}
                                )
                # print(results)
results = pd.DataFrame(results_list)
# results.append(results_list,ignore_index=True)
print(results)
results.to_csv('bull_spread_results.csv')
