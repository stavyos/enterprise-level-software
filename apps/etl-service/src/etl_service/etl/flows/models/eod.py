import datetime

from pydantic import BaseModel, Field


class EOD(BaseModel):
    ticker: str


class EODSaveRequest(BaseModel):
    bus_date: datetime.date
    tickers: list[EOD] = Field(default_factory=list)
    run_id: str
