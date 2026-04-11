"""SQLAlchemy models for stock fundamental data."""

from sqlalchemy import Column, Date, Float, JSON, Text
from .stocks import Base


class StockFundamentals(Base):
    """
    Model representing comprehensive fundamental data for a stock.
    We store the bulk of the data as JSON for flexibility, as the EODHD
    fundamentals response is very large and varies by asset type.
    """

    __tablename__ = "stock_fundamentals"

    symbol = Column(Text, primary_key=True)
    exchange = Column(Text, primary_key=True)
    updated_at = Column(Date, primary_key=True)
    
    general = Column(JSON)
    highlights = Column(JSON)
    valuation = Column(JSON)
    shares_stats = Column(JSON)
    technicals = Column(JSON)
    splits_dividends = Column(JSON)
    analyst_ratings = Column(JSON)
    holders = Column(JSON)
    insider_transactions = Column(JSON)
    earnings = Column(JSON)
    financials = Column(JSON)
