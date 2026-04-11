"""Pydantic models for economic data flows."""

from datetime import date
from pydantic import BaseModel


class EconomicSaveRequest(BaseModel):
    """Request model for economic data saver flow."""
    from_date: date
    to_date: date
    country: str | None = None
    run_id: str
