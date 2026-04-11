__all__ = ["EODHDClientBase"]

import time
from urllib.parse import urljoin

import requests
from loguru import logger

from .endpoint_cost import EndpointCost
from .eod_exceptions import (
    EODHDAPIError,
    EODHDInvalidRequestError,
    EODHDNotFoundError,
    EODHDRateLimitExceededError,
    EODHDServerError,
    EODHDUnauthorizedError,
)
from .rate_limiter import CompositeRateLimiter, RateLimiter


class EODHDClientBase:
    """
    Base class for EODHD API clients, providing common functionality like
    API key management, request handling, error handling, and rate limiting.
    """

    BASE_URL = "https://eodhd.com/api/"
    MAX_RETRIES = 3
    RETRY_DELAY_SECONDS = 1

    DAILY_REQUEST_LIMIT = 100000
    DAILY_PERIOD_SECONDS = 24 * 60 * 60  # 24 hours

    MINUTE_REQUEST_LIMIT = 1000
    MINUTE_PERIOD_SECONDS = 60  # 1 minute

    def __init__(self, api_key: str):
        """
        Initializes the EODHD client with an API key.

        Args:
            api_key (str): The API key provided by EODHD.

        Raises:
            ValueError: If the API key is empty.
        """
        if not api_key:
            raise ValueError("API key cannot be empty.")

        self.api_key = api_key
        self.session = requests.Session()

        daily_limiter = RateLimiter(self.DAILY_REQUEST_LIMIT, self.DAILY_PERIOD_SECONDS)
        minute_limiter = RateLimiter(self.MINUTE_REQUEST_LIMIT, self.MINUTE_PERIOD_SECONDS)
        self.rate_limiter = CompositeRateLimiter([daily_limiter, minute_limiter])

        self._stocks_etf = None
        self._exchanges = None
        self._bulk = None
        self._technical = None
        self._real_time = None
        self._news = None
        self._search = None

    @property
    def stocks_etf(self):
        from .stocks_etf_client import StocksETFClient

        if self._stocks_etf is None:
            self._stocks_etf = StocksETFClient(self.api_key)
        return self._stocks_etf

    @property
    def exchanges(self):
        from .exchanges_client import ExchangesClient

        if self._exchanges is None:
            self._exchanges = ExchangesClient(self.api_key)
        return self._exchanges

    @property
    def bulk(self):
        from .bulk_client import BulkClient

        if self._bulk is None:
            self._bulk = BulkClient(self.api_key)
        return self._bulk

    @property
    def technical(self):
        from .technical_indicator_client import TechnicalIndicatorClient

        if self._technical is None:
            self._technical = TechnicalIndicatorClient(self.api_key)
        return self._technical

    @property
    def real_time(self):
        from .real_time_client import RealTimeClient

        if self._real_time is None:
            self._real_time = RealTimeClient(self.api_key)
        return self._real_time

    @property
    def news(self):
        from .news_client import NewsClient

        if self._news is None:
            self._news = NewsClient(self.api_key)
        return self._news

    @property
    def search_client(self):
        from .search_client import SearchClient

        if self._search is None:
            self._search = SearchClient(self.api_key)
        return self._search

    @staticmethod
    def _get_endpoint_cost(endpoint: str) -> int:
        """
        Determines the API call cost for a given endpoint.

        Args:
            endpoint (str): The API endpoint (e.g., 'exchanges').

        Returns:
            int: The cost of the call in API requests.
        """
        base_endpoint = endpoint.split("/")[0]
        for ec in EndpointCost:
            if ec.endpoint_name == base_endpoint:
                return ec.cost
        return EndpointCost.DEFAULT.cost

    def _make_request(self, endpoint: str, params: dict = None) -> dict | list:
        """
        Makes a GET request to the EODHD API, handling errors and rate limiting.

        Args:
            endpoint (str): The API endpoint path.
            params (dict, optional): Query parameters for the request. Defaults to None.

        Returns:
            dict | list: The parsed JSON response from the API.

        Raises:
            EODHDUnauthorizedError: If the API key is invalid.
            EODHDInvalidRequestError: If the request parameters are invalid.
            EODHDNotFoundError: If the endpoint is not found.
            EODHDRateLimitExceededError: If the API rate limit is reached.
            EODHDServerError: If a server-side error occurs.
            EODHDAPIError: For unexpected API errors.
        """
        full_url = urljoin(base=self.BASE_URL, url=endpoint)

        if params is None:
            params = {}
        params["api_token"] = self.api_key
        params["fmt"] = "json"

        request_cost = self._get_endpoint_cost(endpoint=endpoint)

        for attempt in range(self.MAX_RETRIES):
            self.rate_limiter.wait_for_next_request(cost=request_cost)

            try:
                params_copy = params.copy()

                if "api_token" in params_copy:
                    params_copy["api_token"] = "### REDACTED ###"
                logger.info(
                    "Making request to URL: {url} with params: {params}",
                    url=full_url,
                    params=params_copy,
                )

                response = self.session.get(full_url, params=params)
                response.raise_for_status()  # Raises HTTPError for bad responses (4xx or 5xx)

                # Check if the response content type is JSON
                if "application/json" in response.headers.get("Content-Type", ""):
                    return response.json()
                else:
                    # If not JSON, return the raw text content
                    logger.warning(
                        "Received non-JSON response from {url}. Content: {content}",
                        url=full_url,
                        content=response.text,
                    )
                    return {
                        "raw_response": response.text
                    }  # Or raise an error if non-JSON is always an error
            except requests.exceptions.HTTPError as http_err:
                status_code = http_err.response.status_code
                response_data = {}
                if http_err.response.content:
                    if "application/json" in http_err.response.headers.get("Content-Type", ""):
                        try:
                            response_data = http_err.response.json()
                        except ValueError:
                            response_data = {"raw_response": http_err.response.text}
                    else:
                        response_data = {"raw_response": http_err.response.text}

                if status_code == 401:
                    raise EODHDUnauthorizedError(response_data=response_data)
                elif status_code == 400:
                    raise EODHDInvalidRequestError(response_data=response_data)
                elif status_code == 404:
                    raise EODHDNotFoundError(response_data=response_data)
                elif status_code == 429:
                    raise EODHDRateLimitExceededError(response_data=response_data)
                elif 500 <= status_code < 600:
                    raise EODHDServerError(status_code=status_code, response_data=response_data)
                else:
                    raise EODHDAPIError(
                        f"An unexpected HTTP error occurred: {http_err}",
                        status_code=status_code,
                        response_data=response_data,
                    )
            except requests.exceptions.ConnectionError as conn_err:
                logger.warning(
                    f"Connection error: {conn_err}. Retrying in {self.RETRY_DELAY_SECONDS}s..."
                )
                time.sleep(self.RETRY_DELAY_SECONDS)
            except requests.exceptions.Timeout as timeout_err:
                logger.warning(
                    f"Request timed out: {timeout_err}. Retrying in {self.RETRY_DELAY_SECONDS}s..."
                )
                time.sleep(self.RETRY_DELAY_SECONDS)
            except requests.exceptions.RequestException as req_err:
                raise EODHDAPIError(f"An unexpected request error occurred: {req_err}")

        raise EODHDAPIError(
            f"Failed to make request to {full_url} after {self.MAX_RETRIES} attempts."
        )
