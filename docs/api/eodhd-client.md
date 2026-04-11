# EODHD Client Architecture

The `eodhd-client` library is designed for reliability, scalability, and strict adherence to API limits.

## Core Design Patterns

### 1. Specialized Clients (Composition over Inheritance)
Instead of a single massive class, the library is split into focused clients:
- **`StocksETFClient`**: Basic OHLCV and corporate actions.
- **`BulkClient`**: Optimized for national-scale daily downloads.
- **`NewsClient`**: Financial news and sentiment.
- **`TechnicalIndicatorClient`**: Pre-calculated technical functions.

These all inherit from `EODHDClientBase`, which provides the core HTTP and rate-limiting logic.

### 2. Lazy-Loaded Properties
The main `EODHDClientBase` class uses Python properties to lazily initialize specialized clients.
```python
@property
def technical(self):
    from .technical_indicator_client import TechnicalIndicatorClient
    if self._technical is None:
        self._technical = TechnicalIndicatorClient(self.api_key)
    return self._technical
```
**Benefits:**
- **Performance**: We don't waste memory/time initializing every sub-client if only one is needed.
- **Circular Dependency Prevention**: By importing inside the property, we avoid complex circular import issues.

## Rate Limiting

We implement a **Composite Rate Limiter** to handle EODHD's multi-tier limits:
1.  **Daily Limit**: Based on your subscription (e.g., 100,000 calls).
2.  **Minute Limit**: Prevents rapid-fire bursts that could trigger 429 errors (e.g., 1,000 calls/min).

The system uses `time.sleep` calculations to "throttle" requests automatically, ensuring the ETL service never exceeds its quota.

## Error Handling

The library provides a custom exception hierarchy:
- `EODHDUnauthorizedError` (401)
- `EODHDNotFoundError` (404)
- `EODHDRateLimitExceededError` (429)
- `EODHDServerError` (500+)

Each error captures the raw API response, making it easier to debug issues in the Prefect UI.
