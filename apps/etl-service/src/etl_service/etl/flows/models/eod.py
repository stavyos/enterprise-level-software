import datetime

from pydantic import BaseModel


class EODSaveRequest(BaseModel):
    """Model representing a request to save EOD data for a single ticker."""

    from_date: datetime.date
    to_date: datetime.date
    ticker: str
    run_id: str
