from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from mpl_toolkits.axes_grid1 import host_subplot
import matplotlib.pyplot as plt
import datetime
from decimal import Decimal
import pandas as pd
from WindPy import w
import os
from data_access.db_tables import DataBaseTables as dbt
from Utilities.PlotUtil import PlotUtil

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
#################################################################################

term_in_days = 120 # 6M
# term_in_days = 60 # 3M
# term_in_days = 20 # 1M
#################################################################################
start_date = datetime.date(2017, 3, 31)
last_date = '2017-12-08'

end_date = w.tdaysoffset(-term_in_days-1,last_date,"").Data[0][0].date()
flagNight = 0
nameCode = 'm'
exchange = 'dce'
core_contracts = ['m_1709', 'm_1801', 'm_1805','m_1809','m_1901']
contract_maturities = {'m_1709': datetime.date(2017,7,25),
                   'm_1801': datetime.date(2017,11,24),
                   'm_1805': datetime.date(2018,3,26)}
cpi_6m = {9: 0.8,10:0.8,11:0.9}
cpi_3m = {6: -0.2,7:-0.2,8:0.3,9: 1.0,10:1.0,11:0.6}
cpi_1m = {3: -0.3,4:0.1,5:-0.1,6: -0.2,7:0.1,8:0.4,9: 0.5,10:0.1,11:0.0}
if term_in_days == 60 : cpi_container = cpi_3m
elif term_in_days == 120 : cpi_container = cpi_6m
else:cpi_container = cpi_1m
print('=' * 200)
print("%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s" % (
        "maturity date","strike otm","strike itm",
        'init cost','price long','price short',
        'rebalancing earning', 'p long old','p short old', 'p long new','p short new',
        'value at maturity', 'price long','price short',
        'earning','yield'))
print('=' * 200)
pu = PlotUtil()


results_container = []
dks = [100,150,200]
# dks = [100]
r_bond = 4.5*term_in_days/240
# r_cash = 3.0*term_in_days/240
r_cash = 0.0*term_in_days/240
pct_bond = 0.985
pct_cash = 0.01
for d_k_plus in dks:
# for d_k_plus in [50]:
# for d_k_plus in [100]:
    results_list = []
    d_k_minus = d_k_plus-200
    eval_dates = w.tdays(start_date.strftime('%Y-%m-%d'),end_date.strftime('%Y-%m-%d'),"").Data[0]
    for evalDate in eval_dates:
        try:
            evalDate = evalDate.date()
            # evalDate = start_date
            # maturity_date = w.tdaysoffset(term_in_days,evalDate.strftime('%Y-%m-%d'),"").Data[0][0].date()
            maturity_date = w.tdaysoffset(term_in_days,evalDate.strftime('%Y-%m-%d'),"").Data[0][0].date()
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
            if evalDate < w.tdaysoffset(-1,contract_maturities['m_1709'].strftime('%Y-%m-%d'),"Period = W").Data[0][0].date():
                core_id = 'm_1709'
            elif evalDate < w.tdaysoffset(-1,contract_maturities['m_1801'].strftime('%Y-%m-%d'),"Period = W").Data[0][0].date():
                core_id = 'm_1801'
            else:
                core_id = 'm_1805'

            # if maturity_date > datetime.date(2017,11,24) :core_id = 'm_1805'

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
            try :
                price_short = coredata_df.ix[coredata_df['strike']==strike_otm2,'option_close'].values[0]
                price_long = coredata_df.ix[coredata_df['strike']==strike_itm2,'option_close'].values[0]
            except Exception as e:
                print(e)
                continue
            portfolio_cost = price_long - price_short
            init_cost = portfolio_cost
            # print('init_cost : ', price_long, price_short,init_cost)

            date_range = w.tdays(evalDate.strftime('%Y-%m-%d'),maturity_date.strftime('%Y-%m-%d')).Data[0]
            week_b_cmdt = w.tdaysoffset(-1, contract_maturity, "Period=W").Data[0][0]
            # print(date_range)
            rebalancing_cost = 0.0
            rebalance_earning = 0.0
            price_long_old = 0.0
            price_short_old = 0.0
            price_short_new = 0.0
            price_long_new = 0.0
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
                    price_short_old = df.ix[df['id_underlying']==core_id].ix[df['amt_strike'] == Decimal(strike_otm2)]['amt_close'].values[0]
                    price_long_old = df.ix[df['id_underlying']==core_id].ix[df['amt_strike'] == Decimal(strike_itm2)]['amt_close'].values[0]
                    price_short_new = df.ix[df['id_underlying'] == core_id2].ix[df['amt_strike'] == Decimal(strike_otm2)]['amt_close'].values[0]
                    price_long_new = df.ix[df['id_underlying'] == core_id2].ix[df['amt_strike'] == Decimal(strike_itm2)]['amt_close'].values[0]

                    # print(price_otm2_old,price_itm2_old)
                    # rebalancing_cost = price_long_new - price_short_new - (price_long_old - price_short_old)
                    # portfolio_cost += rebalancing_cost
                    rebalance_earning = price_long_old - price_short_old + price_short_new - price_long_new
                    # print(date,'rebalancing_cost : ',rebalancing_cost)
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
                    price_short_m = df.ix[df['id_underlying'] == id_underlying].ix[df['amt_strike'] == Decimal(strike_otm2)]['amt_close'].values[0]
                    price_long_m = df.ix[df['id_underlying'] == id_underlying].ix[df['amt_strike'] == Decimal(strike_itm2)]['amt_close'].values[0]

                    value_at_maturity = price_long_m - price_short_m

                    # earning = v-portfolio_cost
                    earning = value_at_maturity + rebalance_earning - init_cost
                    r = earning*100.0/init_cost
                    portfolio_yield = (pct_cash*r_cash + pct_bond*r_bond +
                                       (1-pct_bond-pct_cash)*r)*(240/term_in_days)
                    # print('maturity value : ', price_long_m, price_short_m, v,r,'%')
                    # print(evalDate,maturity_date,init_cost,'earning',earning,r,'%')
                    # cpi = cpi_container.get(maturity_date.month)
                    cpi = cpi_container.get(maturity_date.month)
                    results_list.append({'date':maturity_date,
                                    'strikes1':str(d_k_plus),
                                    'strikes2':str(d_k_minus),
                                    'init_cost':init_cost,
                                    'earning':earning,
                                    'future_price':future_price,
                                    'yields':r,
                                    'portfolio_annualized_return':portfolio_yield,
                                    'cpi':cpi}
                                    )
                    print("%15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s %15s" % (
                        maturity_date, strike_otm2, strike_itm2,
                        init_cost, price_long, price_short,
                        rebalance_earning, price_long_old, price_short_old, price_long_new, price_short_new,
                        value_at_maturity, price_long_m, price_short_m,
                        earning, str(round(r,2))+'%'))

        except Exception as e:
            print(evalDate,e)
            continue
    results = pd.DataFrame(results_list)
    results_container.append(results)

fig1 = plt.figure(1)
host = host_subplot(111)
par = host.twinx()
host.set_ylabel("收益率 (%)")
par.set_ylabel("CPI变化率(%)")
cont = 0
for results in results_container:
    host.plot(results['date'],results['yields'], label="策略 "+str(cont+1),
                        color=pu.colors[cont],linestyle=pu.lines[cont], linewidth=2)
    cont += 1

par.plot(results['date'],results['cpi'], label="CPI(右)",
                           color=pu.colors[cont], linestyle=pu.lines[cont], linewidth=2)
host.spines['top'].set_visible(False)
host.yaxis.set_ticks_position('left')
host.xaxis.set_ticks_position('bottom')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3, ncol=4, mode="expand", borderaxespad=0.)
fig1.savefig(os.path.abspath('..')+ '/save_figure/CPI_6M_1.png', format='png')
# fig1.savefig(os.path.abspath('..')+ '/save_figure/CPI_3M_1.png', format='png')
# fig1.savefig(os.path.abspath('..')+ '/save_figure/CPI_1M_1.png', format='png')

fig2 = plt.figure(2)
host = host_subplot(111)
par = host.twinx()
host.set_ylabel("年化收益率 (%)")
par.set_ylabel("CPI变化率(%)")
cont = 0
for results in results_container:
    print(cont+1,' : ',max(results['portfolio_annualized_return']))
    print(cont+1,' : ',min(results['portfolio_annualized_return']))
    host.plot(results['date'],results['portfolio_annualized_return'], label="策略 "+str(cont+1),
                        color=pu.colors[cont],linestyle=pu.lines[cont], linewidth=2)
    cont += 1

par.plot(results['date'],results['cpi'], label="CPI(右)",
                           color=pu.colors[cont], linestyle=pu.lines[cont], linewidth=2)
host.spines['top'].set_visible(False)
host.yaxis.set_ticks_position('left')
host.xaxis.set_ticks_position('bottom')
plt.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3, ncol=4, mode="expand", borderaxespad=0.)
fig2.savefig(os.path.abspath('..')+ '/save_figure/CPI_6M_2.png', format='png')
# fig2.savefig(os.path.abspath('..')+ '/save_figure/CPI_3M_2.png', format='png')
# fig2.savefig(os.path.abspath('..')+ '/save_figure/CPI_1M_2.png', format='png')



# fig2 = plt.figure(2)
# host1 = host_subplot(111)
# par1 = host.twinx()
# host1.set_ylabel("收益率 (年化，%)")
# par1.set_ylabel("CPI变化率(%)")
# cont = 0
# for results in results_container:
#
#     p11, = host1.plot(results['date'],results['portfolio_annualized_return'], label="策略 "+str(cont+1),
#                         color=pu.colors[cont],linestyle=pu.lines[cont], linewidth=2)
#     cont += 1
#
# p21, = par1.plot(results['date'], results['cpi'], label="CPI(右)",
#                            color=pu.colors[cont], linestyle=pu.lines[cont], linewidth=2)
# host1.spines['top'].set_visible(False)
# host1.yaxis.set_ticks_position('left')
# host1.xaxis.set_ticks_position('bottom')
# plt.legend(bbox_to_anchor=(0., 1.02, 1., .202), loc=3, ncol=4, mode="expand", borderaxespad=0.)

# results.append(results_list,ignore_index=True)
# print(results)
# results.to_csv('bull_spread_results.csv')

# fig = plt.figure
# fig.save(os.path.abspath('..')+ '/save_figure/CPI '+str(term_in_days)+'.png', dpi=300, format='png')

# plt.savefig(os.path.abspath('..')+ '/save_figure/CPI_6M.png', format='png')

# fig1 = plt.gcf()



# fig1.savefig(os.path.abspath('..')+ '/save_figure/CPI_6M_1.png', format='png')
# fig2.savefig(os.path.abspath('..')+ '/save_figure/CPI_6M_2.png', format='png')
plt.show()



























