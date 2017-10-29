from sqlalchemy import create_engine, MetaData,Table, Column
from sqlalchemy.dialects.mysql import \
        BIGINT, BINARY, BIT, BLOB, BOOLEAN, CHAR, DATE, \
        DATETIME, DECIMAL, DECIMAL, DOUBLE, ENUM, FLOAT, INTEGER, \
        LONGBLOB, LONGTEXT, MEDIUMBLOB, MEDIUMINT, MEDIUMTEXT, NCHAR, \
        NUMERIC, NVARCHAR, REAL, SET, SMALLINT, TEXT, TIME, TIMESTAMP, \
        TINYBLOB, TINYINT, TINYTEXT, VARBINARY, VARCHAR, YEAR

engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',
                       echo=False)
conn = engine.connect()
metadata = MetaData(engine)

stockIndexTable = Table('stock_index_intraday', metadata,
        Column('datetime', DATETIME, primary_key=True,autoincrement=False),
        Column('id_instrument', VARCHAR(50),primary_key=True),
        Column('close', DECIMAL(18,6))
        )

metadata.create_all()