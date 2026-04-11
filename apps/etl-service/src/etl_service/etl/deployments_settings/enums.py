from __future__ import annotations

from enum import StrEnum


class PrefectDeploymentType(StrEnum):
    SAVER = "Saver"
    DISPATCHER = "Saver Dispatcher"


class PrefectDeployment(StrEnum):
    """Enum for Prefect deployment tags."""

    MAIN = "Main"
    MAIN_DATE_RANGE = "Main Date Range"
    EOD = "EOD"
    INTRADAY = "Intraday"
    EXCHANGES = "Exchanges"
    FUNDAMENTALS = "Fundamentals"
    ECONOMIC_EVENTS = "Economic Events"
    MACRO_INDICATORS = "Macro Indicators"
    MARKET_NEWS = "Market News"
    TECHNICAL_INDICATORS = "Technical Indicators"
    BULK_DATA = "Bulk Data"
