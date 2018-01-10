import pandas as pd
import datetime
from sqlalchemy import *
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


def table_factory(name, tablename, schemaname):
    table_class = type(
        name,
        (Base,),
        dict(
            __tablename__=tablename,
            __table_args__={'schema': schemaname}
        )
    )
    return table_class


start_date = datetime.date(2017, 12, 1)
end_date = datetime.date(2017, 12, 31)
evalDate = datetime.date(2017, 6, 21)

Base = declarative_base()
engine = create_engine('mysql+pymysql://guest:passw0rd@101.132.148.152/', echo=True)

options_intd = table_factory(name="options_intd",
                             tablename="option_mktdata_intraday",
                             schemaname='mktdata_intraday')
options = table_factory(name="option_contracts",
                        tablename="option_mktdata",
                        schemaname='mktdata')

Base.prepare(engine)
Session = sessionmaker(bind=engine)
conn = engine.connect()
metadata = MetaData(engine)
sess = Session()
print(options_intd)
query_option = sess.query(options_intd.id_instrument).join(options,
                                                           options_intd.id_instrument == options.id_instrument)
df_option = pd.read_sql(query_option.statement, query_option.session.bind)
