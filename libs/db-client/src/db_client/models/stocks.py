from sqlalchemy import Column, Date, Float, Integer, Text
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class StockEOD(Base):
    """
    Model representing End-Of-Day (EOD) historical stock data.
    """

    __tablename__ = "stock_eod"

    bus_date = Column(Date, primary_key=True)
    symbol = Column(Text, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(Integer)


class StockAdjusted(Base):
    """
    Model representing adjusted historical stock data.
    """

    __tablename__ = "stock_adjusted"

    bus_date = Column(Date, primary_key=True)
    symbol = Column(Text, primary_key=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    adjusted_close = Column(Float)
    volume = Column(Integer)


class StockDividends(Base):
    """
    Model representing stock dividend history.
    """

    __tablename__ = "stock_dividends"

    bus_date = Column(Date, primary_key=True)
    symbol = Column(Text, primary_key=True)
    declaration_bus_date = Column(Date)
    record_bus_date = Column(Date)
    payment_bus_date = Column(Date)
    period = Column(Text)
    value = Column(Float)
    unadjusted_value = Column(Float)
    currency = Column(Text)


class StockSplits(Base):
    """
    Model representing stock split history.
    """

    __tablename__ = "stock_splits"

    bus_date = Column(Date, primary_key=True)
    symbol = Column(Text, primary_key=True)
    split = Column(Text)


class Exchange(Base):
    """
    Model representing a stock exchange.
    """

    __tablename__ = "exchanges"

    code = Column(Text, primary_key=True)
    name = Column(Text)
    country = Column(Text)
    currency = Column(Text)
    operating_mic = Column(Text)
    country_iso2 = Column(Text)
    country_iso3 = Column(Text)


class Ticker(Base):
    """
    Model representing a stock ticker.
    """

    __tablename__ = "tickers"

    code = Column(Text, primary_key=True)
    exchange_code = Column(Text, primary_key=True)
    name = Column(Text)
    country = Column(Text)
    currency = Column(Text)
    type = Column(Text)
    isin = Column(Text)


class VirginTicker(Base):
    """
    Model representing a newly discovered ticker that requires historical EOD data backfill.
    """

    __tablename__ = "virgin_tickers"

    ticker = Column(Text, primary_key=True)
    exchange = Column(Text, primary_key=True)
    first_eod_bus_date = Column(Date, nullable=True)
