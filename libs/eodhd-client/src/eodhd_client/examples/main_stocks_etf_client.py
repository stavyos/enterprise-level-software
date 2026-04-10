"""
Example script demonstrating the usage of all StocksETFClient methods.
"""

import os
from datetime import datetime, timedelta

import pandas as pd
from db_client.client import DBClient
from eodhd_client.eod_exceptions import EODHDAPIError
from eodhd_client.stocks_etf_client import StocksETFClient
from loguru import logger


def save_data_to_files(data, filename_prefix, output_dir):
    if not data:
        logger.info(f"No data to save for {filename_prefix}.")
        return

    df = pd.DataFrame(data)
    parquet_path = os.path.join(output_dir, f"{filename_prefix}.parquet")
    csv_path = os.path.join(output_dir, f"{filename_prefix}.csv")

    df.to_parquet(parquet_path, index=False)
    logger.info(f"Data saved to {parquet_path}")
    df.to_csv(csv_path, index=False)
    logger.info(f"Data saved to {csv_path}")


def run_stocks_etf_examples():
    api_key = os.getenv("EODHD_API_KEY", "YOUR_API_KEY_HERE")

    # Load DB credentials from environment variables
    db_name = os.getenv("DB_NAME", "postgres")
    db_user = os.getenv("DB_USER", "postgres")
    db_pass = os.getenv("DB_PASSWORD")
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = int(os.getenv("DB_PORT", 5430))

    if not db_pass:
        logger.error("DB_PASSWORD environment variable is not set.")
        return

    db_client = DBClient(dbname=db_name, user=db_user, password=db_pass, host=db_host, port=db_port)

    if api_key == "YOUR_API_KEY_HERE":
        logger.warning(
            "Please set your EODHD API key as an environment variable "
            "(EODHD_API_KEY) or replace 'YOUR_API_KEY_HERE' in the example script."
        )
        return

    logger.info("Initializing StocksETFClient...")
    try:
        stocks_etf_client = StocksETFClient(api_key=api_key)

        # Define common parameters for examples
        symbol = "AAPL"
        exchange = "US"
        today = datetime.now()
        five_days_ago = today - timedelta(days=5)
        date_from_str = five_days_ago.strftime("%Y-%m-%d")
        date_to_str = today.strftime("%Y-%m-%d")
        interval = "1h"  # For intraday data

        # For intraday data, 'from' and 'to' parameters expect Unix timestamps
        date_from_timestamp = int(five_days_ago.timestamp())
        date_to_timestamp = int(today.timestamp())

        output_dir = "data"
        os.makedirs(output_dir, exist_ok=True)

        logger.info("\n--- Stocks, ETF, Funds Data Examples ---")

        # 1. get_eod_data(symbol, exchange, date_from, date_to)
        logger.info(
            f"\nFetching EOD data for {symbol}.{exchange} from {date_from_str} to {date_to_str}..."
        )
        aapl_eod = stocks_etf_client.get_eod_data(symbol, exchange, date_from_str, date_to_str)
        logger.info(f"{symbol}.{exchange} EOD data (first 2 entries): {aapl_eod[:2]}")
        save_data_to_files(aapl_eod, f"{symbol}_{exchange}_eod", output_dir)
        for entry in aapl_eod:
            db_client.insert_stock_data(
                bus_date=datetime.strptime(entry["date"], "%Y-%m-%d").date(),
                symbol=symbol,
                open_price=entry["open"],
                high_price=entry["high"],
                low_price=entry["low"],
                close_price=entry["close"],
                adjusted_close_price=entry["adjusted_close"],
                volume=entry["volume"],
            )

        # 2. get_intraday_data(symbol, exchange, interval, date_from, date_to)
        logger.info(
            f"\nFetching Intraday data for {symbol}.{exchange} "
            f"(interval: {interval}) from {date_from_timestamp} to {date_to_timestamp}..."
        )
        aapl_intraday = stocks_etf_client.get_intraday_data(
            symbol, exchange, interval, date_from_timestamp, date_to_timestamp
        )
        logger.info(f"{symbol}.{exchange} Intraday data (first 2 entries): {aapl_intraday[:2]}")
        save_data_to_files(aapl_intraday, f"{symbol}_{exchange}_intraday", output_dir)
        for entry in aapl_intraday:
            db_client.insert_stock_intraday_data(
                timestamp=entry["timestamp"],
                symbol=symbol,
                bus_date=datetime.strptime(entry["datetime"].split(" ")[0], "%Y-%m-%d").date(),
                gmt_offset=entry["gmtoffset"],
                open_price=entry["open"],
                high_price=entry["high"],
                low_price=entry["low"],
                close_price=entry["close"],
                volume=entry["volume"],
            )

        # 3. get_dividends(symbol, exchange, date_from, date_to)
        logger.info(
            f"\nFetching Dividends for {symbol}.{exchange} from {date_from_str} to {date_to_str}..."
        )
        aapl_dividends = stocks_etf_client.get_dividends(
            symbol, exchange, "2000-01-01", date_to_str
        )
        logger.info(f"{symbol}.{exchange} Dividends (first 2 entries): {aapl_dividends[:2]}")
        save_data_to_files(aapl_dividends, f"{symbol}_{exchange}_dividends", output_dir)
        for entry in aapl_dividends:
            db_client.insert_stock_dividends_data(
                bus_date=datetime.strptime(entry["date"], "%Y-%m-%d").date(),
                symbol=symbol,
                declaration_bus_date=datetime.strptime(entry["declarationDate"], "%Y-%m-%d").date(),
                record_bus_date=datetime.strptime(entry["recordDate"], "%Y-%m-%d").date(),
                payment_bus_date=datetime.strptime(entry["paymentDate"], "%Y-%m-%d").date(),
                period=entry["period"],
                value=entry["value"],
                unadjusted_value=entry["unadjustedValue"],
                currency=entry["currency"],
            )

        # 4. get_splits(symbol, exchange, date_from, date_to)
        logger.info(
            f"\nFetching Splits for {symbol}.{exchange} from {date_from_str} to {date_to_str}..."
        )
        aapl_splits = stocks_etf_client.get_splits(symbol, exchange, "2000-01-01", date_to_str)
        logger.info(f"{symbol}.{exchange} Splits (first 2 entries): {aapl_splits[:2]}")
        save_data_to_files(aapl_splits, f"{symbol}_{exchange}_splits", output_dir)
        for entry in aapl_splits:
            db_client.insert_stock_splits_data(
                bus_date=datetime.strptime(entry["date"], "%Y-%m-%d").date(),
                symbol=symbol,
                split=entry["split"],
            )

        # 5. get_adjusted_data(symbol, exchange, date_from, date_to)
        logger.info(
            f"\nFetching Adjusted EOD data for "
            f"{symbol}.{exchange} from {date_from_str} to {date_to_str}..."
        )
        aapl_adjusted = stocks_etf_client.get_adjusted_data(
            symbol, exchange, "2020-01-01", date_to_str
        )
        logger.info(f"{symbol}.{exchange} Adjusted EOD data (first 2 entries): {aapl_adjusted[:2]}")
        save_data_to_files(aapl_adjusted, f"{symbol}_{exchange}_adjusted", output_dir)
        for entry in aapl_adjusted:
            db_client.insert_stock_adjusted_data(
                bus_date=datetime.strptime(entry["date"], "%Y-%m-%d").date(),
                symbol=symbol,
                open_price=entry["open"],
                high_price=entry["high"],
                low_price=entry["low"],
                close_price=entry["close"],
                adjusted_close_price=entry["adjusted_close"],
                volume=entry["volume"],
            )

    except EODHDAPIError as e:
        logger.error(f"An EODHD API error occurred: {e}")
    except Exception as e:
        logger.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    run_stocks_etf_examples()
