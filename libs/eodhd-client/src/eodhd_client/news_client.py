"""Module for fetching news data from EODHD API."""

from .client import EODHDClientBase


class NewsClient(EODHDClientBase):
    """
    Client for fetching market news data.
    """

    def __init__(self, api_key: str):
        super().__init__(api_key)

    def get_news(
        self,
        symbols: str = None,
        tags: str = None,
        from_date: str = None,
        to_date: str = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list:
        """
        Retrieves financial news data.

        Args:
            symbols (str, optional): Ticker symbols (e.g., 'AAPL,MSFT'). Defaults to None.
            tags (str, optional): News tags (e.g., 'earnings,ipo'). Defaults to None.
            from_date (str, optional): Start date in YYYY-MM-DD format. Defaults to None.
            to_date (str, optional): End date in YYYY-MM-DD format. Defaults to None.
            limit (int, optional): Number of news items to return. Defaults to 50. Max 1000.
            offset (int, optional): Number of news items to skip. Defaults to 0.

        Returns:
            list: A list of news articles.
        """
        endpoint = "news"
        params = {"limit": limit, "offset": offset}
        if symbols:
            params["s"] = symbols
        if tags:
            params["t"] = tags
        if from_date:
            params["from"] = from_date
        if to_date:
            params["to"] = to_date
        return self._make_request(endpoint, params)
