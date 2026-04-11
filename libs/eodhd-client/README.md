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

# Fetch Technical Indicators
rsi = client.technical.get_technical_indicator("AAPL", "US", function="rsi", period=14)

# Bulk Download
bulk_eod = client.bulk.get_bulk_eod(country="US")
```
