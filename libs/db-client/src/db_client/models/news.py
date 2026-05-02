"""SQLAlchemy models for market news data."""

from sqlalchemy import Column, DateTime, Text
from sqlalchemy.dialects.postgresql import ARRAY

from .stocks import Base


class MarketNews(Base):
    """
    Model representing financial news articles.
    """

    __tablename__ = "market_news"

    date = Column(DateTime(timezone=True), primary_key=True)
    title = Column(Text, primary_key=True)

    content = Column(Text)
    link = Column(Text)
    symbols = Column(ARRAY(Text))  # List of related ticker symbols
    tags = Column(ARRAY(Text))  # List of related tags
