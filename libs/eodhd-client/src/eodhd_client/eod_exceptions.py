__all__ = [
    "EODHDAPIError",
    "EODHDUnauthorizedError",
    "EODHDInvalidRequestError",
    "EODHDNotFoundError",
    "EODHDRateLimitExceededError",
    "EODHDServerError",
]


class EODHDAPIError(Exception):
    """Base exception for all EODHD API-related errors."""

    def __init__(self, message: str, status_code: int = None, response_data: dict = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.response_data = response_data

    def __str__(self):
        if self.status_code and self.response_data:

            return (
                f"EODHDAPIError: Status {self.status_code} - "
                f"{self.message} - "
                f"Details: {self.response_data}"
            )
        elif self.status_code:
            return f"EODHDAPIError: Status {self.status_code} - {self.message}"
        return f"EODHDAPIError: {self.message}"


class EODHDUnauthorizedError(EODHDAPIError):
    """Raised when the API key is invalid or missing (HTTP 401)."""

    def __init__(
        self, message: str = "Unauthorized: Invalid or missing API key.", response_data: dict = None
    ):
        super().__init__(message, 401, response_data)


class EODHDInvalidRequestError(EODHDAPIError):
    """Raised for bad requests (HTTP 400)."""

    def __init__(
        self, message: str = "Bad Request: The request was invalid.", response_data: dict = None
    ):
        super().__init__(message, 400, response_data)


class EODHDNotFoundError(EODHDAPIError):
    """Raised when a requested resource is not found (HTTP 404)."""

    def __init__(
        self,
        message: str = "Not Found: The requested resource could not be found.",
        response_data: dict = None,
    ):
        super().__init__(message, 404, response_data)


class EODHDRateLimitExceededError(EODHDAPIError):
    """Raised when the API rate limit is exceeded (HTTP 429)."""

    def __init__(
        self, message: str = "Rate Limit Exceeded: Too many requests.", response_data: dict = None
    ):
        super().__init__(message, 429, response_data)


class EODHDServerError(EODHDAPIError):
    """Raised for server-side errors (HTTP 5xx)."""

    def __init__(
        self,
        message: str = "Server Error: An unexpected error occurred on the API server.",
        status_code: int = 500,
        response_data: dict = None,
    ):
        super().__init__(message, status_code, response_data)
