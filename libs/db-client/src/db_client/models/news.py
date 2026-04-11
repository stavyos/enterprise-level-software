"""SQLAlchemy models for market news data."""

from sqlalchemy import JSON, Column, DateTime, Text

from .stocks import Base


class MarketNews(Base):
    """
    Model representing financial news articles.
    """

    __tablename__ = "market_news"

    date = Column(DateTime, primary_key=True)
    title = Column(Text, primary_key=True)

    content = Column(Text)
    link = Column(Text)
    symbols = Column(JSON)  # List of related ticker symbols
    tags = Column(JSON)  # List of related tags
