__all__ = ["StocksETFClient"]

from eodhd_client import EODHDClientBase


class StocksETFClient(EODHDClientBase):
    """
    Client for fetching Stocks, ETFs, and Funds data from the EODHD API.
    Inherits common functionality from EODHDClientBase.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_eod_data(
        self, symbol: str, exchange: str, date_from: str, date_to: str
    ) -> list:
        """
        Retrieves End-Of-Day (EOD) historical data for a specific symbol.

        Args:
            symbol (str): The ticker symbol (e.g., 'AAPL').
            exchange (str): The exchange code (e.g., 'US').
            date_from (str): Start date in YYYY-MM-DD format.
            date_to (str): End date in YYYY-MM-DD format.

        Returns:
            list: A list of EOD data points.
        """
        endpoint = f"eod/{symbol}.{exchange}"
        params = {
            "from": date_from,
            "to": date_to,
        }
        return self._make_request(endpoint, params)

    def get_intraday_data(
        self, symbol: str, exchange: str, date_from: int, date_to: int
    ) -> list:
        """
        Retrieves intraday historical data for a specific symbol.
        The interval is strictly limited to 1-minute ('1m').

        Args:
            symbol (str): The ticker symbol.
            exchange (str): The exchange code.
            date_from (int): Start timestamp (Unix time).
            date_to (int): End timestamp (Unix time).

        Returns:
            list: A list of intraday data points.
        """
        endpoint = f"intraday/{symbol}.{exchange}"
        params = {
            "interval": "1m",
            "from": date_from,
            "to": date_to,
        }
        return self._make_request(endpoint, params)

    def get_dividends(
        self, symbol: str, exchange: str, date_from: str = None, date_to: str = None
    ) -> list:
        """
        Retrieves dividend history for a specific symbol.

        Args:
            symbol (str): The ticker symbol.
            exchange (str): The exchange code.
            date_from (str, optional): Start date in YYYY-MM-DD format.
            date_to (str, optional): End date in YYYY-MM-DD format.

        Returns:
            list: A list of dividend events.
        """
        endpoint = f"div/{symbol}.{exchange}"
        params = {}
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        return self._make_request(endpoint, params)

    def get_splits(
        self, symbol: str, exchange: str, date_from: str = None, date_to: str = None
    ) -> list:
        """
        Retrieves stock split history for a specific symbol.

        Args:
            symbol (str): The ticker symbol.
            exchange (str): The exchange code.
            date_from (str, optional): Start date in YYYY-MM-DD format.
            date_to (str, optional): End date in YYYY-MM-DD format.

        Returns:
            list: A list of split events.
        """
        endpoint = f"splits/{symbol}.{exchange}"
        params = {}
        if date_from:
            params["from"] = date_from
        if date_to:
            params["to"] = date_to
        return self._make_request(endpoint, params)

    def get_adjusted_data(
        self, symbol: str, exchange: str, date_from: str, date_to: str
    ) -> list:
        """
        Retrieves adjusted End-Of-Day (EOD) historical data for a specific symbol.

        Args:
            symbol (str): The ticker symbol.
            exchange (str): The exchange code.
            date_from (str): Start date in YYYY-MM-DD format.
            date_to (str): End date in YYYY-MM-DD format.

        Returns:
            list: A list of adjusted EOD data points.
        """
        endpoint = f"eod/{symbol}.{exchange}"
        params = {
            "from": date_from,
            "to": date_to,
            "adjusted": "true",
        }
        return self._make_request(endpoint, params)
