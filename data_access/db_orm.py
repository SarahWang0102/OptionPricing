from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


############ Declare ORM mapping of WindCodes class
Base = declarative_base()
class WindCodes(Base):
    __tablename__ = 'wind_codes'
    windcode = Column(VARCHAR(45), primary_key=True)
    id_instrument = Column(VARCHAR(45))

    def __repr__(self):
        return "<WindCodes(winde_codes='%s', id_instrument='%s')" % (self.windcode, self.id_instrument)


# define database engine
db = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata',echo=True)

# Get a database session
Session = sessionmaker(bind=db)
sess = Session()

# Insert data into database
wc = WindCodes(windcode="10000001.HH",id_instrument="houhou")
sess.add(wc)
sess.commit()

# Update data
wcUpdate = sess.query(WindCodes).filter_by(windcode='10000001.HH').first()
wcUpdate.id_instrument = 'miaomiao'
sess.commit()

# Query data

wcs = sess.query(WindCodes).all()

for wc in wcs:
    print(wc)

# Delete data
wcDelete = sess.query(WindCodes).filter_by(windcode='10000001.HH').first()
sess.delete(wcDelete)
sess.commit()