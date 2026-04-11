"""Pydantic models for macro indicators data flows."""

from pydantic import BaseModel


class EconomicIndicator(BaseModel):
    """Model representing a single macro indicator."""
    indicator_code: str


class MacroSaveRequest(BaseModel):
    """Request model for macro indicators saver flow."""
    country: str
    indicators: list[EconomicIndicator]
    run_id: str
