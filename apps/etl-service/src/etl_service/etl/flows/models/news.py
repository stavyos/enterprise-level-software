"""Pydantic models for market news flows."""

from datetime import date

from pydantic import BaseModel


class NewsSaveRequest(BaseModel):
    """Request model for market news saver flow."""

    symbols: str | None = None
    tags: str | None = None
    from_date: date | None = None
    to_date: date | None = None
    limit: int = 50
    run_id: str
