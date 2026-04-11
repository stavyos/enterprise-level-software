"""Module for fetching technical indicator data from EODHD API."""

from .client import EODHDClientBase


class TechnicalIndicatorClient(EODHDClientBase):
    """
    Client for fetching technical indicator data.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_technical_indicator(
        self,
        symbol: str,
        exchange: str,
        function: str,
        period: int = None,
        **kwargs,
    ) -> list:
        """
        Retrieves technical indicator data for a specific ticker.

        Args:
            symbol (str): The stock ticker symbol.
            exchange (str): The exchange code.
            function (str): The technical indicator function (e.g., 'rsi', 'sma', 'ema').
            period (int, optional): The period for the indicator calculation. Defaults to None.
            **kwargs: Additional parameters for specific indicators (e.g., 'from', 'to').

        Returns:
            list: A list of technical indicator data points.
        """
        endpoint = f"technical/{symbol}.{exchange}"
        params = {"function": function}
        if period:
            params["period"] = period
        params.update(kwargs)
        return self._make_request(endpoint, params)
