import pandas as pd
import hashlib
import datetime

sha = hashlib.sha256()
now = str(datetime.datetime.now()).encode('utf-8')
sha.update(now)
print(sha.hexdigest())

df = pd.DataFrame()
idx = 0
for (idx,row) in df.iterrows():
    print(idx)
print(idx)
df1 = pd.DataFrame(data={'aa':['a','a1'],'bb':['b','b1']})
print(df1)
df = df.append(df1,ignore_index=True)

print(df.aa)
df.loc[df['aa']!='a','bb']='modified'
print(df)
dt = datetime.date(2017,12,8)
print(dt.day)