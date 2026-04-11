"""Script for saving technical indicator data."""

import os
from datetime import date

from db_client.client import DBClient
from eodhd_client.client import EODHDClientBase
from loguru import logger


def technical_indicator_saver(
    symbol: str, exchange: str, function: str, period: int | None, run_id: str
) -> None:
    """Core logic for saving technical indicator data."""
    api_key = os.getenv("EODHD_API_KEY")
    client = EODHDClientBase(api_key).technical

    db_client = DBClient(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    try:
        indicators = client.get_technical_indicator(
            symbol=symbol, exchange=exchange, function=function, period=period
        )
        for item in indicators:
            db_client.insert_technical_indicator(
                bus_date=date.fromisoformat(item["date"]),
                symbol=symbol,
                indicator_name=f"{function}_{period}" if period else function,
                value=float(item[function]) if item.get(function) is not None else None,
            )
        logger.info(f"Saved {len(indicators)} technical indicators for {symbol}.")
    except Exception as e:
        logger.error(f"Error saving technical indicators for {symbol}: {e}")
