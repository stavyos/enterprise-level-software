"""SQLAlchemy models for economic events data."""

from sqlalchemy import Column, Date, Float, Text
from .stocks import Base


class EconomicEvent(Base):
    """
    Model representing global economic events (Retail Sales, PMI, etc.).
    """

    __tablename__ = "economic_events"

    event_date = Column(Date, primary_key=True)
    country = Column(Text, primary_key=True)
    event_type = Column(Text, primary_key=True)
    
    value = Column(Float)
    previous_value = Column(Float)
    unit = Column(Text)
    comparison = Column(Text)
