"""Pydantic models for technical indicator flows."""

from pydantic import BaseModel


class TechnicalIndicatorSaveRequest(BaseModel):
    """Request model for technical indicator saver flow."""
    symbol: str
    exchange: str
    function: str
    period: int | None = None
    run_id: str
