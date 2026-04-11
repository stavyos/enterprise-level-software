"""Script for saving macro indicator data."""

from datetime import date
import os
from eodhd_client.client import EODHDClientBase
from db_client.client import DBClient
from loguru import logger


def macro_indicators_saver(country: str, indicator_codes: list[str], run_id: str) -> None:
    """Core logic for saving macro indicator data."""
    api_key = os.getenv("EODHD_API_KEY")
    client = EODHDClientBase(api_key).economic
    
    db_client = DBClient(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    for code in indicator_codes:
        try:
            indicators = client.get_macro_indicator(country=country, indicator=code)
            for item in indicators:
                db_client.insert_macro_indicator(
                    country=country,
                    indicator_code=code,
                    bus_date=date.fromisoformat(item["date"]),
                    value=float(item["value"]) if item["value"] else None
                )
            logger.info(f"Saved {len(indicators)} macro indicators for {code} ({country}).")
        except Exception as e:
            logger.error(f"Error saving macro indicators {code} for {country}: {e}")
