"""SQLAlchemy models for macroeconomic indicator data."""

from sqlalchemy import Column, Date, Float, Text
from .stocks import Base


class MacroIndicator(Base):
    """
    Model representing macroeconomic indicators for a specific country.
    """

    __tablename__ = "macro_indicators"

    country = Column(Text, primary_key=True)
    indicator_code = Column(Text, primary_key=True)
    bus_date = Column(Date, primary_key=True)
    
    value = Column(Float)
