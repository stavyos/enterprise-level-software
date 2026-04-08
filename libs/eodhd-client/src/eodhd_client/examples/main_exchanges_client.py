"""
Example script demonstrating the usage of all ExchangesClient methods.
"""

import os

from eodhd_client.eod_exceptions import EODHDAPIError
from eodhd_client.exchanges_client import ExchangesClient
from loguru import logger


def run_exchanges_examples():
    api_key = os.getenv("EODHD_API_KEY", "YOUR_API_KEY_HERE")

    if api_key == "YOUR_API_KEY_HERE":
        logger.warning(
            "Please set your EODHD API key as an environment variable "
            "(EODHD_API_KEY) or replace 'YOUR_API_KEY_HERE' in the example script."
        )
        return

    logger.info("Initializing ExchangesClient...")
    try:
        exchanges_client = ExchangesClient(api_key=api_key)

        # Define common parameters for examples
        exchange_code = "US"

        logger.info("\n--- Exchanges Data Examples ---")

        # 1. get_supported_exchanges()
        logger.info("Fetching all supported exchanges...")
        supported_exchanges = exchanges_client.get_supported_exchanges()
        logger.info(f"First 5 supported exchanges: {supported_exchanges[:5]}")

        # 2. get_traded_tickers(exchange_code)
        logger.info(f"\nFetching all traded tickers for exchange '{exchange_code}'...")
        traded_tickers = exchanges_client.get_traded_tickers(exchange_code=exchange_code)
        logger.info(f"First 5 traded tickers for {exchange_code}: {traded_tickers[:5]}")

        # 3. get_exchange_trading_hours(exchange_code)
        logger.info(f"\nFetching trading hours for exchange '{exchange_code}'...")
        trading_hours = exchanges_client.get_exchange_trading_hours(exchange_code=exchange_code)
        logger.info(f"Trading hours for {exchange_code}: {trading_hours}")

        # 4. get_all_tickers_from_all_exchanges()
        logger.info("\nFetching all tickers from all exchanges (this may take a while)...")
        all_tickers = exchanges_client.get_all_tickers_from_all_exchanges()
        logger.info(f"First 5 tickers from all exchanges: {all_tickers[:5]}")

    except EODHDAPIError as e:
        logger.error(f"An EODHD API error occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    run_exchanges_examples()
