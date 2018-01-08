from sqlalchemy import *
from sqlalchemy.ext.declarative import declarative_base

class DataBaseTables():
    Base = declarative_base()

    class OptionMkt(Base):
        __tablename__ = 'options_mktdata'
        dt_date = Column(Date, nullable=True ,primary_key=True)
        id_instrument = Column(VARCHAR(45), nullable=True , primary_key=True)
        flag_night = Column(INT, nullable=True, primary_key=True)
        datasource = Column(VARCHAR(45), nullable=True , primary_key=True)
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
            return "<OptionMktdata(dt_date='%s', id_instrument='%s',flag_night='%s',datasource='%s',code_instrument='%s',name_code='%s',id_underlying='%s'," \
                   "amt_strike='%s',cd_option_type='%s',amt_last_close='%s',amt_last_settlement='%s',amt_open='%s',amt_high='%s',amt_low='%s',amt_close='%s'," \
                   "amt_bid='%s',amt_ask='%s',amt_delta='%s',amt_gamma='%s',amt_vega='%s',amt_theta='%s',amt_rho='%s',pct_implied_vol='%s',amt_settlement='%s'," \
                   "amt_trading_volume='%s',amt_trading_value='%s',amt_holding_volume='%s',amt_exercised='%s',cd_exchange='%s',timestamp='%s')" % \
                   (self.dt_date,self.id_instrument,self.flag_night,self.datasource,self.code_instrument,self.name_code,self.id_underlying,
                    self.amt_strike,self.cd_option_type,self.amt_last_close,self.amt_last_settlement,self.amt_open, self.amt_high,self.amt_low,self.amt_close,
                    self.amt_bid,self.amt_ask,self.amt_delta,self.amt_gamma,self.amt_vega,self.amt_theta,self.amt_rho,self.pct_implied_vol,self.amt_settlement,
                    self.amt_trading_volume,self.amt_trading_value,self.amt_holding_volume,self.amt_exercised,self.cd_exchange,self.timestamp)

    class FutureMkt(Base):
        __tablename__ = 'futures_mktdata'
        dt_date = Column(Date, nullable=False , primary_key=True)
        id_instrument = Column(VARCHAR(45), nullable=False , primary_key=True)
        flag_night = Column(INT, nullable=False , primary_key=True)
        datasource = Column(VARCHAR(45), nullable=False , primary_key=True)
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
            return "<FutureMktdata(dt_date='%s',id_instrument='%s',flag_night='%s',name_code='%s',amt_last_close='%s',amt_last_settlement='%s',amt_open='%s'," \
                   "amt_high='%s',amt_low='%s',amt_close='%s',amt_settlement='%s',amt_trading_volume='%s',amt_trading_value='%s',amt_holding_volume='%s'," \
                   "cd_exchange='%s',timestamp='%s')" % \
                   (self.dt_date,self.id_instrument,self.flag_night,self.name_code,self.amt_last_close,self.amt_last_settlement,self.amt_open,
                    self.amt_high,self.amt_low,self.amt_close,self.amt_settlement,self.amt_trading_volume,self.amt_trading_value,self.amt_holding_volume,
                    self.cd_exchange,self.timestamp)

    class IndexMkt(Base):
        __tablename__ = 'indexes_mktdata'
        dt_date = Column(Date, nullable=False , primary_key=True)
        id_instrument = Column(VARCHAR(45), nullable=False , primary_key=True)
        datasource = Column(VARCHAR(45), nullable=False , primary_key=True)
        code_instrument = Column(VARCHAR(45))
        amt_open = Column(DECIMAL(18, 4))
        amt_high = Column(DECIMAL(18, 4))
        amt_low = Column(DECIMAL(18, 4))
        amt_close = Column(DECIMAL(18, 4))
        amt_trading_volume = Column(DECIMAL(18, 4))
        amt_trading_value = Column(DECIMAL(18, 4))
        timestamp = Column(TIMESTAMP)

        def __repr__(self):
            return "<IndexMktdata(dt_date='%s',id_instrument='%s',datasource='%s',amt_open='%s'," \
                   "amt_high='%s',amt_low='%s',amt_close='%s',amt_trading_volume='%s',amt_trading_value='%s'" \
                   ",amt_holding_volume='%s',timestamp='%s')" % \
                   (self.dt_date,self.id_instrument,self.datasource,self.code_instrument,
                    self.amt_open,self.amt_high,self.amt_low,self.amt_close,
                    self.amt_trading_volume,self.amt_trading_value,self.timestamp)


    class Options(Base):
        __tablename__ = 'option_contracts'
        id_instrument = Column(VARCHAR(45), nullable=True , primary_key=True)
        windcode = Column(VARCHAR(20), nullable=True, primary_key=True)
        name_option = Column(VARCHAR(45), nullable=True , primary_key=True)
        id_underlying = Column(VARCHAR(20))
        windcode_underlying = Column(VARCHAR(20))
        cd_option_type = Column(VARCHAR(20))
        cd_exercise_type = Column(VARCHAR(20))
        amt_strike = Column(DECIMAL(10, 4))
        name_contract_month = Column(VARCHAR(20))
        dt_listed = Column(DATE)
        dt_maturity = Column(DATE)
        dt_exercise = Column(DATE)
        dt_settlement = Column(DATE)
        cd_settle_method = Column(VARCHAR(20))
        nbr_multiplier = Column(INT)
        cd_exchange = Column(VARCHAR(20))
        timestamp = Column(TIMESTAMP)

        def __repr__(self):
            return "<Options(id_instrument='%s', windcode='%s',name_option='%s'," \
                   "id_underlying='%s',windcode_underlying='%s',cd_option_type='%s'," \
                   "cd_exercise_type='%s'," \
                   "amt_strike='%s',name_contract_month='%s',dt_listed='%s'," \
                   "dt_maturity='%s',dt_exercise='%s',dt_settlement='%s',cd_settle_method='%s'," \
                   "nbr_multiplier='%s',cd_exchange='%s',timestamp='%s')" % \
                   (self.id_instrument,self.windcode,self.name_option,self.id_underlying,
                    self.windcode_underlying,self.cd_option_type,self.cd_exercise_type,
                    self.amt_strike,self.name_contract_month, self.dt_listed,self.dt_maturity,
                    self.dt_exercise,self.dt_settlement,self.cd_settle_method,self.nbr_multiplier,
                    self.cd_exchange,self.timestamp)

    class Futures(Base):
        __tablename__ = 'future_contracts'
        id_instrument = Column(VARCHAR(45), nullable=True , primary_key=True)
        windcode = Column(VARCHAR(20))
        name_instrument = Column(VARCHAR(45))
        name_code = Column(VARCHAR(20))
        name_contract_month = Column(VARCHAR(20))
        pct_margin = Column(DECIMAL(5, 2))
        pct_change_limit = Column(DECIMAL(5, 2))
        dt_listed = Column(DATE)
        dt_maturity = Column(DATE)
        dt_settlement = Column(DATE)
        nbr_multiplier = Column(INT)
        cd_exchange = Column(VARCHAR(20))
        timestamp = Column(TIMESTAMP)

        def __repr__(self):
            return "<Futures(id_instrument='%s', windcode='%s',name_instrument='%s'," \
                   "name_code='%s',name_contract_month='%s',pct_margin='%s',pct_change_limit='%s'," \
                   "dt_listed='%s',dt_maturity='%s',dt_settlement='%s'," \
                   "nbr_multiplier='%s',cd_exchange='%s',timestamp='%s')" % \
                   (self.id_instrument,self.windcode,self.name_instrument,self.name_code,
                    self.name_contract_month, self.pct_margin,self.pct_change_limit,
                    self.dt_listed,self.dt_maturity,self.dt_settlement,self.nbr_multiplier,
                    self.cd_exchange,self.timestamp)

    class EquityIndexIntraday(Base):
        __tablename__ = 'equity_index_mktdata_intraday'
        dt_datetime = Column(DATETIME, nullable=False , primary_key=True)
        id_instrument = Column(VARCHAR(45), nullable=True , primary_key=True)
        datasource = Column(VARCHAR(45), nullable=True, primary_key=True)
        code_instrument = Column(VARCHAR(45))
        amt_close = Column(DECIMAL(18, 4))
        amt_trading_volume = Column(DECIMAL(18, 4))
        amt_trading_value = Column(DECIMAL(18, 4))
        timestamp = Column(TIMESTAMP)

        def __repr__(self):
            return "<EquityIndexIntraday(dt_datetime='%s', id_instrument='%s',datasource='%s'," \
                   "code_instrument='%s',amt_close='%s',amt_trading_volume='%s',amt_trading_value='%s'," \
                   "timestamp='%s')" % \
                   (self.dt_datetime,self.id_instrument,self.datasource,self.code_instrument,
                    self.amt_close, self.amt_trading_volume,self.amt_trading_value,
                    self.timestamp)

    class FutureMktIntraday(Base):
        __tablename__ = 'future_mktdata_intraday'
        dt_datetime = Column(DATETIME, nullable=False , primary_key=True)
        id_instrument = Column(VARCHAR(45), nullable=True , primary_key=True)
        datasource = Column(VARCHAR(45), nullable=True, primary_key=True)
        code_instrument = Column(VARCHAR(45))
        amt_close = Column(DECIMAL(18, 4))
        amt_trading_volume = Column(DECIMAL(18, 4))
        amt_trading_value = Column(DECIMAL(18, 4))
        timestamp = Column(TIMESTAMP)

        def __repr__(self):
            return "<FutureMktIntraday(dt_datetime='%s', id_instrument='%s',datasource='%s'," \
                   "code_instrument='%s',amt_close='%s',amt_trading_volume='%s',amt_trading_value='%s'," \
                   "timestamp='%s')" % \
                   (self.dt_datetime,self.id_instrument,self.datasource,self.code_instrument,
                    self.amt_close, self.amt_trading_volume,self.amt_trading_value,
                    self.timestamp)

    class OptionMktIntraday(Base):
        __tablename__ = 'option_mktdata_intraday'
        dt_datetime = Column(DATETIME, nullable=False , primary_key=True)
        id_instrument = Column(VARCHAR(45), nullable=True , primary_key=True)
        datasource = Column(VARCHAR(45), nullable=True, primary_key=True)
        code_instrument = Column(VARCHAR(45))
        amt_close = Column(DECIMAL(18, 4))
        amt_trading_volume = Column(DECIMAL(18, 4))
        amt_trading_value = Column(DECIMAL(18, 4))
        timestamp = Column(TIMESTAMP)

        def __repr__(self):
            return "<OptionMktIntraday(dt_datetime='%s', id_instrument='%s',datasource='%s'," \
                   "code_instrument='%s',amt_close='%s',amt_trading_volume='%s',amt_trading_value='%s'," \
                   "timestamp='%s')" % \
                   (self.dt_datetime,self.id_instrument,self.datasource,self.code_instrument,
                    self.amt_close, self.amt_trading_volume,self.amt_trading_value,
                    self.timestamp)
