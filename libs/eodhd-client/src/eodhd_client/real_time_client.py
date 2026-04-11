"""Module for fetching real-time data from EODHD API."""

from .client import EODHDClientBase


class RealTimeClient(EODHDClientBase):
    """
    Client for fetching real-time (delayed) data.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_real_time_data(self, symbol: str, exchange: str, additional_symbols: list[str] = None) -> dict | list:
        """
        Retrieves real-time (delayed) data for one or more tickers.

        Args:
            symbol (str): The primary ticker symbol (e.g., 'AAPL').
            exchange (str): The exchange code (e.g., 'US').
            additional_symbols (list[str], optional): Additional ticker symbols. Defaults to None.

        Returns:
            dict | list: Real-time data for the requested ticker(s).
        """
        endpoint = f"real-time/{symbol}.{exchange}"
        params = {}
        if additional_symbols:
            params["s"] = ",".join(additional_symbols)
        return self._make_request(endpoint, params)
