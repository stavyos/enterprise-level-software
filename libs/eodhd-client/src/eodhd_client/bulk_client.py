"""Module for fetching bulk historical data from EODHD API."""

from .client import EODHDClientBase


class BulkClient(EODHDClientBase):
    """
    Client for fetching bulk End-of-Day, Splits, and Dividends data.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_bulk_eod(self, country: str, date: str = None, symbols: str = None) -> list:
        """
        Retrieves bulk End-Of-Day (EOD) data for a specific country.

        Args:
            country (str): The country code (e.g., 'US').
            date (str, optional): The date in YYYY-MM-DD format. Defaults to None.
            symbols (str, optional): A comma-separated list of symbols. Defaults to None.

        Returns:
            list: A list of EOD data for multiple symbols.
        """
        endpoint = f"eod-bulk-last-day/{country}"
        params = {}
        if date:
            params["date"] = date
        if symbols:
            params["symbols"] = symbols
        return self._make_request(endpoint, params)

    def get_bulk_splits(self, country: str, date: str = None, symbols: str = None) -> list:
        """
        Retrieves bulk stock splits data for a specific country.

        Args:
            country (str): The country code (e.g., 'US').
            date (str, optional): The date in YYYY-MM-DD format. Defaults to None.
            symbols (str, optional): A comma-separated list of symbols. Defaults to None.

        Returns:
            list: A list of splits data for multiple symbols.
        """
        endpoint = f"eod-bulk-last-day/{country}"
        params = {"type": "splits"}
        if date:
            params["date"] = date
        if symbols:
            params["symbols"] = symbols
        return self._make_request(endpoint, params)

    def get_bulk_dividends(self, country: str, date: str = None, symbols: str = None) -> list:
        """
        Retrieves bulk dividends data for a specific country.

        Args:
            country (str): The country code (e.g., 'US').
            date (str, optional): The date in YYYY-MM-DD format. Defaults to None.
            symbols (str, optional): A comma-separated list of symbols. Defaults to None.

        Returns:
            list: A list of dividends data for multiple symbols.
        """
        endpoint = f"eod-bulk-last-day/{country}"
        params = {"type": "dividends"}
        if date:
            params["date"] = date
        if symbols:
            params["symbols"] = symbols
        return self._make_request(endpoint, params)
