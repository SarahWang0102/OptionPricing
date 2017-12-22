import pandas as pd
import datetime
import numpy as np

from dateutil.relativedelta import relativedelta

evalDate = datetime.date(2017,12,1)
strikes = [2.0,2.1,2.2,2.3]
maturity_dates = [datetime.date(2017,12,8),
                  datetime.date(2017,12,8),
                  datetime.date(2017,12,10),
                  datetime.date(2017,12,10),
                  ]
underlying_prices = [2.8,2.8,2.8,2.8]
option_prices = [1.5,1.4,1.3,1.2]
rfs = [0.03,0.03,0.03,0.03]
df = pd.DataFrame({'strikes':strikes,
                           'maturity_dates':maturity_dates,
                           'underlying_prices':underlying_prices,
                           'option_prices':option_prices,
                            'risk_free_rates':rfs})




ttms = []
for mdt in maturity_dates:
    ttm = (mdt - evalDate).days/365.0
    ttms.append(ttm)
df['ttm'] = ttms

df['logmoneyness'] = np.log(df['strikes']/(df['underlying_prices']*np.exp(df['risk_free_rates'])))
print(df)

print(df['maturity_dates'].unique())
for mdate in df['maturity_dates'].unique():
    # print(mdate-evalDate)
    c1 = df['maturity_dates'] == mdate
    # print(df[c1])
    t = df[c1]['ttm'].iloc[0]
    print(t,type(t))