"""Pydantic models for bulk data flows."""

from datetime import date
from pydantic import BaseModel


class BulkDataSaveRequest(BaseModel):
    """Request model for bulk data saver flow."""
    country: str
    bus_date: date
    type: str  # 'eod', 'splits', 'dividends'
    run_id: str
