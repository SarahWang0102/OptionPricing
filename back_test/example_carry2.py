import math
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import QuantLib as ql
from WindPy import w
import datetime
import os
import pickle
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from data_access.db_tables import DataBaseTables as dbt
from OptionStrategyLib.calibration import SVICalibration
from OptionStrategyLib.OptionPricing.Evaluation import Evaluation
from OptionStrategyLib.OptionPricing.OptionMetrics import OptionMetrics
from OptionStrategyLib.OptionPricing.Options import OptionPlainEuropean
from back_test.bkt_option import BktOption
from back_test.bkt_option_set import OptionSet


start_date = datetime.date(2015, 12, 31)
# start_date = datetime.date(2016, 4, 27)
# end_date = datetime.date(2016, 5, 31)
end_date = datetime.date(2017, 12, 31)
# evalDate = datetime.date(2017, 6, 21)

rf = 0.03
engineType = 'AnalyticEuropeanEngine'
dt = 1.0 / 12
init_fund = 10000

engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/mktdata', echo=False)
conn = engine.connect()
metadata = MetaData(engine)
Session = sessionmaker(bind=engine)
sess = Session()
engine2 = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/metrics', echo=False)
conn2 = engine2.connect()
metadata2 = MetaData(engine2)
Session2 = sessionmaker(bind=engine2)
sess2 = Session2()
Index_mkt = dbt.IndexMkt
Option_mkt = dbt.OptionMkt
option_intd = dbt.OptionMktIntraday
carry = Table('carry', metadata2, autoload=True)
options = dbt.Options

w.start()
calendar = ql.China()
daycounter = ql.ActualActual()
fund = init_fund



query = sess2.query(carry)
df_carry = pd.read_sql(query.statement,query.session.bind)
# print(df_carry)

df_carry = df_carry[df_carry['amt_carry'] != -999.0].reset_index()

date_range = w.tdays(start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"), "Period=W").Data[0]

for date in date_range:
    evalDate = date.date()
    df_metric = df_carry[df_carry['dt_date']==evalDate]
    df_put = df_metric[df_metric['cd_option_type']=='put']
    df_call = df_metric[df_metric['cd_option_type']=='call']\
                .sort_values(by='amt_carry',ascending=False).reset_index()
    df_call_t5 = df_call.loc[0:4]
    df_call_b5 = df_call.loc[len(df_call)-5:]
    print(df_call_t5)
    print(df_call_b5)





























































