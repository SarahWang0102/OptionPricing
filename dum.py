from sqlalchemy import create_engine, MetaData,\
        Table, Column, Integer, String, ForeignKey

engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)

user_table = Table('test_db',metadata,autoload=True)
print(user_table.columns)
ins = user_table.insert()
d = [[930,930],[1,2]]

conn.execute(ins,
             [{'pk1':'20170103','pk2':'stock','data':0.5}

])

print(ins)