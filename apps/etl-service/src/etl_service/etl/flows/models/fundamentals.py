"""Pydantic models for fundamental data flows."""

from datetime import date
from pydantic import BaseModel


class Fundamental(BaseModel):
    """Model representing a single ticker for fundamental data fetching."""
    symbol: str
    exchange: str


class FundamentalSaveRequest(BaseModel):
    """Request model for fundamental data saver flow."""
    tickers: list[Fundamental]
    run_id: str
    updated_at: date
