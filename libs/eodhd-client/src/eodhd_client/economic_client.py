"""Module for fetching economic data from EODHD API."""

from .client import EODHDClientBase


class EconomicClient(EODHDClientBase):
    """
    Client for fetching economic events and macro indicators.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_economic_events(
        self,
        from_date: str = None,
        to_date: str = None,
        country: str = None,
        comparison: str = None,
        limit: int = 1000,
    ) -> list:
        """
        Retrieves economic events data.

        Args:
            from_date (str, optional): Start date in YYYY-MM-DD format. Defaults to None.
            to_date (str, optional): End date in YYYY-MM-DD format. Defaults to None.
            country (str, optional): 2-symbol ISO country code. Defaults to None.
            comparison (str, optional): Comparison type ('mom', 'qoq', 'yoy'). Defaults to None.
            limit (int, optional): Number of records to return. Defaults to 1000.

        Returns:
            list: A list of economic events.
        """
        endpoint = "economic-events"
        params = {"limit": limit}
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        if country:
            params["country"] = country
        if comparison:
            params["comparison"] = comparison
        return self._make_request(endpoint, params)

    def get_macro_indicator(self, country: str, indicator: str = None) -> list:
        """
        Retrieves macroeconomic indicators data for a specific country.

        Args:
            country (str): 3-symbol ISO country code (e.g., 'USA').
            indicator (str, optional): The indicator code. Defaults to None.

        Returns:
            list: A list of macroeconomic indicator values.
        """
        endpoint = f"macro-indicator/{country}"
        params = {}
        if indicator:
            params["indicator"] = indicator
        return self._make_request(endpoint, params)
