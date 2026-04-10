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


class StockIntraday(Base):
    """
    Model representing intraday historical stock data.
    """

    __tablename__ = "stock_intraday"

    timestamp = Column(Integer, primary_key=True)
    symbol = Column(Text, primary_key=True)
    bus_date = Column(Date)
    gmt_offset = Column(Integer)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Integer)


class StockSplits(Base):
    """
    Model representing stock split history.
    """

    __tablename__ = "stock_splits"

    bus_date = Column(Date, primary_key=True)
    symbol = Column(Text, primary_key=True)
    split = Column(Text)
