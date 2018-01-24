from back_test.bkt_account import BktUtil,BktAccount
from back_test.bkt_option_set import BktOptionSet
import pandas as pd
import QuantLib as ql
import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from data_access.db_tables import DataBaseTables as dbt
from back_test.bkt_util import BktUtil






class FactorStrategyBkt(object):

    def __init__(self,df_option_metrics,hp,money_utilization=0.2,init_fund=1000000.0,tick_size=0.0001,fee_rate=2.0/10000,
                 nbr_slippage=0,max_money_utilization=0.5,buy_ratio=0.5,sell_ratio=0.5,nbr_top_bottom=5
                 ):
        self.util = BktUtil()
        self.init_fund = init_fund
        self.money_utl = money_utilization
        self.holding_period = hp
        self.df_option_metrics = df_option_metrics
        self.buy_ratio = buy_ratio
        self.sell_ratio = sell_ratio
        self.nbr_top_bottom = nbr_top_bottom
        self.option_type = None
        self.min_ttm = None
        self.max_ttm = None
        self.calendar = ql.China()
        self.bkt_account = BktAccount(fee_rate=fee_rate,init_fund=init_fund)
        self.bkt_optionset = BktOptionSet('daily', df_option_metrics, hp)

    def set_min_ttm(self,min_ttm):
        self.min_ttm = min_ttm

    def set_max_ttm(self,max_ttm):
        self.max_ttm = max_ttm

    def set_option_type(self,option_type):
        self.option_type = option_type


    def get_candidate_set(self,eval_date):
        if self.option_type == None:
            option_list = self.bkt_optionset.bktoption_list
        else:
            if self.option_type == self.util.type_call:
                option_list = self.bkt_optionset.bktoption_list_call
            else:
                option_list = self.bkt_optionset.bktoption_list_put

        if self.min_ttm != None and self.max_ttm != None:
            list = []
            for option in option_list:
                min_maturity = self.util.to_dt_date(self.calendar.advance(self.util.to_ql_date(eval_date),ql.Period(self.min_ttm,ql.Days)))
                max_maturity = self.util.to_dt_date(self.calendar.advance(self.util.to_ql_date(eval_date),ql.Period(self.max_ttm,ql.Days)))
                if option.maturitydt>=min_maturity and option.maturitydt<=max_maturity:
                    list.append(option)
            option_list = list
        return option_list


    def get_carry_tnb(self,option_list,n):
        df_ranked = self.bkt_optionset.rank_by_carry(option_list)
        df_ranked = df_ranked[df_ranked[self.util.col_carry] != -999.0]
        df_buy = df_ranked.loc[0:n-1]
        df_sell = df_ranked.loc[len(df_ranked)-n:]
        return df_buy,df_sell

    def run(self):
        bkt_optionset = self.bkt_optionset
        bkt = self.bkt_account

        while bkt_optionset.index < len(bkt_optionset.dt_list):
            if bkt_optionset.index == 0:
                bkt_optionset.next()
                continue

            evalDate = bkt_optionset.eval_date
            hp_enddate = self.util.to_dt_date(
                self.calendar.advance(self.util.to_ql_date(evalDate), ql.Period(self.holding_period, ql.Days)))

            df_metrics_today = self.df_option_metrics[(self.df_option_metrics[self.util.col_date]==evalDate)]

            """回测期最后一天全部清仓"""
            if evalDate == bkt_optionset.end_date:
                print(' Liquidate all possitions !!! ')
                bkt.liquidate_all(evalDate)
                break

            """清仓到期期权头寸"""
            for bktoption in bkt.holdings:
                if bktoption.maturitydt == evalDate:
                    print('Liquidate position at maturity : ', evalDate, ' , ', bktoption.maturitydt)
                    bkt.close_position(evalDate, bktoption)


            """持有期holding_period满，进行调仓 """
            if (bkt_optionset.index-1)%self.holding_period == 0:
                print('调仓 : ', evalDate)
                option_list = self.get_candidate_set(evalDate)
                df_buy, df_sell = self.get_carry_tnb(option_list, self.nbr_top_bottom)
                """平仓：将手中头寸进行平仓，除非当前头寸在新一轮持有期中仍判断持有相同的方向，则不会先平仓再开仓"""
                for bktoption in bkt.holdings:
                    if bktoption.maturitydt <= hp_enddate:
                        bkt.close_position(evalDate, bktoption)
                    else:
                        if bktoption.trade_long_short == 1 and bktoption in df_buy['bktoption']: continue
                        if bktoption.trade_long_short == -1 and bktoption in df_sell['bktoption']: continue
                        bkt.close_position(evalDate, bktoption)

                """开仓：等金额做多df_buy，等金额做空df_sell"""
                fund_buy = bkt.cash * self.money_utl * self.buy_ratio
                fund_sell = bkt.cash * self.money_utl * self.sell_ratio
                n1 = len(df_buy)
                n2 = len(df_sell)
                for (idx, row) in df_buy.iterrows():
                    bktoption = row['bktoption']
                    if bktoption in bkt.holdings and bktoption.trade_flag_open:
                        bkt.rebalance_position(evalDate, bktoption, fund_buy/n1)
                    else:
                        bkt.open_long(evalDate, bktoption, fund_buy/n1)

                for (idx, row) in df_sell.iterrows():
                    bktoption = row['bktoption']
                    if bktoption in bkt.holdings and bktoption.trade_flag_open:
                        bkt.rebalance_position(evalDate, bktoption, fund_sell/n2)
                    else:
                        bkt.open_short(evalDate, bktoption, fund_sell/n2)
            """按当日价格调整保证金，计算投资组合盯市价值"""
            bkt.mkm_update(evalDate, df_metrics_today, self.util.col_close)
            print(evalDate,' , ' ,bkt.npv) # npv是组合净值，期初为1
            bkt_optionset.next()


