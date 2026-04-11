"""Module for fetching fundamental data from EODHD API."""

from .client import EODHDClientBase


class FundamentalsClient(EODHDClientBase):
    """
    Client for fetching fundamental data from the EODHD API.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_fundamentals(self, symbol: str, exchange: str) -> dict:
        """
        Retrieves comprehensive fundamental data for a specific stock ticker.

        Args:
            symbol (str): The stock ticker symbol (e.g., 'AAPL').
            exchange (str): The exchange code (e.g., 'US').

        Returns:
            dict: A dictionary containing fundamental data.
        """
        endpoint = f"fundamentals/{symbol}.{exchange}"
        return self._make_request(endpoint)

    def get_bulk_fundamentals(self, exchange: str, offset: int = 0, limit: int = 1000) -> list:
        """
        Retrieves fundamental data for all symbols in a specific exchange in bulk.

        Args:
            exchange (str): The exchange code (e.g., 'US').
            offset (int, optional): Number of records to skip. Defaults to 0.
            limit (int, optional): Number of records to return. Defaults to 1000.

        Returns:
            list: A list of fundamental data for multiple symbols.
        """
        endpoint = f"bulk-fundamentals/{exchange}"
        params = {"offset": offset, "limit": limit}
        return self._make_request(endpoint, params)
