__all__ = ["ExchangesClient"]


from eodhd_client import EODHDClientBase


class ExchangesClient(EODHDClientBase):
    """
    Client for fetching Exchanges data from the EODHD API.
    Inherits common functionality from EODHDClientBase.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_supported_exchanges(self) -> list:
        """
        Retrieves a list of all supported exchanges from the EODHD API.

        Returns:
            list: A list of dictionaries, each containing details about an exchange.
        """
        endpoint = "exchanges-list/"
        return self._make_request(endpoint)

    def get_all_tickers_from_all_exchanges(self) -> list:
        """
        Collects all tickers from all supported exchanges by iterating through the exchange list.

        Note: This can be a very expensive and time-consuming operation depending on the number of exchanges.  # noqa: E501

        Returns:
            list: A consolidated list of ticker dictionaries from all exchanges.
        """
        all_exchanges = self.get_supported_exchanges()
        all_tickers = []
        for exchange in all_exchanges:
            exchange_code = exchange.get("Code")
            if exchange_code:
                try:
                    tickers = self.get_traded_tickers(exchange_code=exchange_code)
                    all_tickers.extend(tickers)
                except Exception:
                    pass
        return all_tickers

    def get_traded_tickers(self, exchange_code: str) -> list:
        """
        Retrieves a list of all tickers traded on a specific exchange.

        Args:
            exchange_code (str): The code of the exchange (e.g., 'US', 'LSE').

        Returns:
            list: A list of dictionaries, each containing ticker details for the specified exchange.
        """
        endpoint = f"exchange-symbol-list/{exchange_code}/"
        return self._make_request(endpoint)

    def get_exchange_trading_hours(self, exchange_code: str) -> dict:
        """
        Retrieves trading hours and other details for a specific exchange.

        Args:
            exchange_code (str): The code of the exchange (e.g., 'US').

        Returns:
            dict: A dictionary containing exchange details and trading hours.
        """
        endpoint = f"exchange-details/{exchange_code}/"
        return self._make_request(endpoint)
