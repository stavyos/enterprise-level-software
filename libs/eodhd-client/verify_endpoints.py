import os
from datetime import date
from eodhd_client.client import EODHDClientBase
from loguru import logger

def test_endpoints():
    api_key = os.getenv("EODHD_API_KEY")
    if not api_key:
        logger.error("EODHD_API_KEY not found in environment.")
        return

    client = EODHDClientBase(api_key)
    
    # Test cases: (Client Property, Method Name, Arguments)
    tests = [
        ("stocks_etf", "get_eod_data", {"symbol": "AAPL", "exchange": "US", "date_from": "2024-01-01", "date_to": "2024-01-05"}),
        ("stocks_etf", "get_intraday_data", {"symbol": "AAPL", "exchange": "US", "interval": "1h", "date_from": 1704067200, "date_to": 1704153600}),
        ("stocks_etf", "get_dividends", {"symbol": "AAPL", "exchange": "US"}),
        ("stocks_etf", "get_splits", {"symbol": "AAPL", "exchange": "US"}),
        ("exchanges", "get_supported_exchanges", {}),
        ("exchanges", "get_traded_tickers", {"exchange_code": "US"}),
        ("fundamentals", "get_fundamentals", {"symbol": "AAPL", "exchange": "US"}),
        ("bulk", "get_bulk_eod", {"country": "US", "date": "2024-04-09"}),
        ("technical", "get_technical_indicator", {"symbol": "AAPL", "exchange": "US", "function": "rsi"}),
        ("economic", "get_economic_events", {"from_date": "2024-04-01", "to_date": "2024-04-10"}),
        ("economic", "get_macro_indicator", {"country": "USA", "indicator": "gdp_current_usd"}),
        ("real_time", "get_real_time_data", {"symbol": "AAPL", "exchange": "US"}),
        ("news", "get_news", {"symbols": "AAPL", "limit": 1}),
        ("search_client", "search", {"query": "Apple", "type": "stock"}),
    ]

    results = []
    for client_prop, method_name, kwargs in tests:
        try:
            logger.info(f"Testing {client_prop}.{method_name}...")
            target_client = getattr(client, client_prop)
            method = getattr(target_client, method_name)
            response = method(**kwargs)
            
            # Check for generic failure indicators in response
            if isinstance(response, dict) and "raw_response" in response:
                status = "FAILED (Non-JSON)"
            else:
                status = "SUCCESS"
            
            results.append((f"{client_prop}.{method_name}", status))
        except Exception as e:
            results.append((f"{client_prop}.{method_name}", f"FAILED: {str(e)}"))

    print("\n" + "="*50)
    print(f"{'Endpoint':<40} | {'Status'}")
    print("-" * 50)
    for endpoint, status in results:
        print(f"{endpoint:<40} | {status}")
    print("="*50 + "\n")

if __name__ == "__main__":
    test_endpoints()
