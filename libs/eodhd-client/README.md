# EODHD Client

A high-performance Python client for the [EODHD API](https://eodhd.com).

## Features
- **Comprehensive Endpoint Support**: EOD, Intraday, Splits, Dividends, Bulk Data, News, Search, Real-Time, and Technical Indicators.
- **Lazy-Loaded Property Architecture**: Efficient resource usage by only initializing specific API clients when needed.
- **Robust Rate Limiting**: Built-in composite rate limiting (Daily and Per-Minute) to prevent API key suspension.
- **Structured Error Handling**: Custom exception hierarchy for API-specific errors.
- **Production Verified**: All implemented endpoints are tested against live production keys.

## Usage

```python
from eodhd_client.client import EODHDClientBase

client = EODHDClientBase(api_key="your_api_key")

# Fetch EOD data
eod_data = client.stocks_etf.get_eod_data("AAPL", "US")

# Bulk Download
bulk_eod = client.bulk.get_bulk_eod(country="US")
```

## Development

This project follows the monorepo's unified linting and formatting standards using **Ruff**.

- **Lint**: `npx nx run eodhd-client:lint`
- **Format**: `npx nx run eodhd-client:format`
- **Test**: `npx nx run eodhd-client:test`
