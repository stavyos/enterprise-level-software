"""Module for searching tickers and news from EODHD API."""

from .client import EODHDClientBase


class SearchClient(EODHDClientBase):
    """
    Client for searching tickers and news.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def search(self, query: str, type: str = "ticker", limit: int = 50) -> list:
        """
        Searches for tickers or news.

        Args:
            query (str): The search query.
            type (str, optional): The type of search ('ticker' or 'news'). Defaults to 'ticker'.
            limit (int, optional): The maximum number of results. Defaults to 50.

        Returns:
            list: A list of search results.
        """
        endpoint = "search"
        params = {"q": query, "limit": limit}
        if type:
            params["type"] = type
        return self._make_request(endpoint, params)
