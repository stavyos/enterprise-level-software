from enum import Enum


class EndpointCost(Enum):
    """
    Enumeration of EODHD API endpoints and their associated call costs.
    """

    FUNDAMENTALS = ("fundamentals", 10)
    EOD = ("eod", 1)
    REAL_TIME = ("real-time", 1)
    HISTORICAL_MARKET_CAP = ("historical-market-cap", 10)
    EARNINGS_TRENDS = ("earnings-trends", 10)
    SCREENER = ("screener", 5)
    INTRADAY = ("intraday", 5)
    ECONOMIC_EVENTS = ("economic-events", 1)
    MACRO_INDICATORS = ("macro-indicators", 10)
    TECHNICAL_INDICATOR = ("technical-indicator", 5)
    EXCHANGE_DETAILS = ("exchange-details", 5)
    UPCOMING_SPLITS = ("upcoming-splits", 10)
    UPCOMING_EARNINGS = ("upcoming-earnings", 10)
    UPCOMING_IPOS = ("upcoming-ipos", 10)
    HISTORICAL_SPLITS = ("historical-splits", 1)
    HISTORICAL_DIVIDENDS = ("historical-dividends", 1)
    NEWS = ("news", 5)
    NEWS_SENTIMENT = ("news-sentiment", 5)
    EXCHANGE_SYMBOLS = ("exchange-symbols", 1)
    BULK_EOD = ("bulk-eod", 100)
    BULK_FUNDAMENTALS = ("bulk-fundamentals", 100)
    INSIDER_TRANSACTIONS = ("insider-transactions", 10)
    DEFAULT = ("default", 1)

    def __init__(self, endpoint_name: str, cost: int):
        """
        Initializes an endpoint cost entry.

        Args:
            endpoint_name (str): The base name of the endpoint.
            cost (int): The cost of calling this endpoint in API requests.
        """
        self.endpoint_name = endpoint_name
        self.cost = cost
