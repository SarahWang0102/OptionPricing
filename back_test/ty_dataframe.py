import pandas as pd
import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

df = pd.DataFrame({'a': [1,2,3],'b': [2,2,4]})

print(df)
df = df.drop_duplicates(subset=['b'])
df = df.reset_index()
print(df)

print(df.columns.tolist())


l = ['a','b','c']
print(l)
l.remove('c')
print(l)