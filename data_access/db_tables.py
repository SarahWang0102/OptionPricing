from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
############ Declare ORM mapping of WindCodes class
Base1 = declarative_base()
Base2 = declarative_base()
Base3 = declarative_base()


class WindCodes(Base1):
    __tablename__ = 'wind_codes'
    windcode = Column(VARCHAR(45), primary_key=True)
    id_instrument = Column(VARCHAR(45))

    def __repr__(self):
        return "<WindCodes(winde_codes='%s', id_instrument='%s')" % (self.windcode, self.id_instrument)


class OptionMkt(Base2):
    __tablename__ = 'options_mktdata'
    dt_date = Column(Date, primary_key=True)
    id_instrument = Column(VARCHAR(45), primary_key=True)
    flag_night = Column(INT, primary_key=True)
    datasource = Column(VARCHAR(45), primary_key=True)
    code_instrument = Column(VARCHAR(45))
    name_code = Column(VARCHAR(45))
    id_underlying = Column(VARCHAR(45))
    amt_strike = Column(DECIMAL(10, 4))
    cd_option_type = Column(VARCHAR(10))
    amt_last_close = Column(DECIMAL(18, 4))
    amt_last_settlement = Column(DECIMAL(18, 4))
    amt_open = Column(DECIMAL(18, 4))
    amt_high = Column(DECIMAL(18, 4))
    amt_low = Column(DECIMAL(18, 4))
    amt_close = Column(DECIMAL(18, 4))
    amt_bid = Column(DECIMAL(18, 4))
    amt_ask = Column(DECIMAL(18, 4))
    amt_delta = Column(DECIMAL(10, 6))
    amt_gamma = Column(DECIMAL(10, 6))
    amt_vega = Column(DECIMAL(10, 6))
    amt_theta = Column(DECIMAL(10, 6))
    amt_rho = Column(DECIMAL(10, 6))
    pct_implied_vol = Column(DECIMAL(10, 6))
    amt_settlement = Column(DECIMAL(18, 4))
    amt_trading_volume = Column(DECIMAL(18, 4))
    amt_trading_value = Column(DECIMAL(18, 4))
    amt_holding_volume = Column(DECIMAL(18, 4))
    amt_exercised = Column(DECIMAL(18, 4))
    cd_exchange = Column(VARCHAR(10))
    timestamp = Column(TIMESTAMP)

    def __repr__(self):
        return "<OptionMktdata(" \
               "dt_date='%s', " \
               "id_instrument='%s'" \
               "flag_night='%s'" \
               "datasource='%s'" \
               "code_instrument='%s'" \
               "name_code='%s'" \
               "id_underlying='%s'" \
               "amt_strike='%s'" \
               "cd_option_type='%s'" \
               "amt_last_close='%s'" \
               "amt_last_settlement='%s'" \
               "amt_open='%s'" \
               "amt_high='%s'" \
               "amt_low='%s'" \
               "amt_close='%s'" \
               "amt_bid='%s'" \
               "amt_ask='%s'" \
               "amt_delta='%s'" \
               "amt_gamma='%s'" \
               "amt_vega='%s'" \
               "amt_theta='%s'" \
               "amt_rho='%s'" \
               "pct_implied_vol='%s'" \
               "amt_settlement='%s'" \
               "amt_trading_volume='%s'" \
               "amt_trading_value='%s'" \
               "amt_holding_volume='%s'" \
               "amt_exercised='%s'" \
               "cd_exchange='%s'" \
               "timestamp='%s'" \
               ")" % \
               (self.dt_date,
                self.id_instrument,
                self.flag_night,
                self.datasource,
                self.code_instrument,
                self.name_code,
                self.id_underlying,
                self.amt_strike,
                self.cd_option_type,
                self.amt_last_close,
                self.amt_last_settlement,
                self.amt_open,
                self.amt_high,
                self.amt_low,
                self.amt_close,
                self.amt_bid,
                self.amt_ask,
                self.amt_delta,
                self.amt_gamma,
                self.amt_vega,
                self.amt_theta,
                self.amt_rho,
                self.pct_implied_vol,
                self.amt_settlement,
                self.amt_trading_volume,
                self.amt_trading_value,
                self.amt_holding_volume,
                self.amt_exercised,
                self.cd_exchange,
                self.timestamp,
                )

class FutureMkt(Base3):
    __tablename__ = 'futures_mktdata'
    dt_date = Column(Date, primary_key=True)
    id_instrument = Column(VARCHAR(45), primary_key=True)
    flag_night = Column(INT, primary_key=True)
    code_instrument = Column(VARCHAR(45))
    name_code = Column(VARCHAR(45))
    amt_last_close = Column(DECIMAL(18, 4))
    amt_last_settlement = Column(DECIMAL(18, 4))
    amt_open = Column(DECIMAL(18, 4))
    amt_high = Column(DECIMAL(18, 4))
    amt_low = Column(DECIMAL(18, 4))
    amt_close = Column(DECIMAL(18, 4))
    amt_settlement = Column(DECIMAL(18, 4))
    amt_trading_volume = Column(DECIMAL(18, 4))
    amt_trading_value = Column(DECIMAL(18, 4))
    amt_holding_volume = Column(DECIMAL(18, 4))
    cd_exchange = Column(VARCHAR(10))
    timestamp = Column(TIMESTAMP)

    def __repr__(self):
        return "<OptionMktdata(" \
               "dt_date='%s', " \
               "id_instrument='%s'" \
               "flag_night='%s'" \
               "name_code='%s'" \
               "amt_last_close='%s'" \
               "amt_last_settlement='%s'" \
               "amt_open='%s'" \
               "amt_high='%s'" \
               "amt_low='%s'" \
               "amt_close='%s'" \
               "amt_settlement='%s'" \
               "amt_trading_volume='%s'" \
               "amt_trading_value='%s'" \
               "amt_holding_volume='%s'" \
               "cd_exchange='%s'" \
               "timestamp='%s'" \
               ")" % \
               (self.dt_date,
                self.id_instrument,
                self.flag_night,
                self.name_code,
                self.amt_last_close,
                self.amt_last_settlement,
                self.amt_open,
                self.amt_high,
                self.amt_low,
                self.amt_close,
                self.amt_settlement,
                self.amt_trading_volume,
                self.amt_trading_value,
                self.amt_holding_volume,
                self.cd_exchange,
                self.timestamp,
                )


engine = create_engine('mysql+pymysql://root:liz1128@101.132.148.152/mktdata', echo=False)

Session = sessionmaker(bind=engine)
sess = Session()
optionmkt = OptionMkt()
futuremkt = FutureMkt()
windcd = WindCodes()
sess.add(optionmkt)
sess.add(futuremkt)
sess.add(windcd)
# res = sess.query(OptionMktdata).join(WindCodes).filter(
#     OptionMktdata.dt_date == '2017-03-31',
#     OptionMktdata.datasource == 'dce',
#     WindCodes.id_instrument == OptionMktdata.id_instrument)

res1 = sess.query(OptionMkt,FutureMkt).select_from(FutureMkt).join(OptionMkt).filter(
    OptionMkt.dt_date == '2017-03-31',
    OptionMkt.datasource == 'dce',
    FutureMkt.id_instrument == OptionMkt.id_underlying)
print(res1)










