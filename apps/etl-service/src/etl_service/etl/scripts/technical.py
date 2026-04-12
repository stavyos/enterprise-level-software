"""Script for saving technical indicator data."""

import os
from datetime import date

from db_client.client import DBClient
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings
from loguru import logger


def technical_indicator_saver(
    symbol: str, exchange: str, function: str, period: int | None, run_id: str
) -> None:
    """Core logic for saving technical indicator data."""
    client = EODHDClientBase(settings.eodhd_api_key).technical

    db_client = DBClient(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )

    inserted_count = 0
    try:
        indicators = client.get_technical_indicator(
            symbol=symbol, exchange=exchange, function=function, period=period
        )
        total_indicators = len(indicators)
        for i, item in enumerate(indicators):
            success = db_client.insert_technical_indicator(
                bus_date=date.fromisoformat(item.get("date")) if item.get("date") else None,
                symbol=symbol,
                indicator_name=f"{function}_{period}" if period else function,
                value=float(item.get(function)) if item.get(function) is not None else None,
            )
            if success:
                inserted_count += 1

            if (i + 1) % 500 == 0:
                logger.info(f"Progress: {i + 1}/{total_indicators} technical indicators processed for {symbol}...")

        logger.info(
            f"Successfully inserted {inserted_count}/{total_indicators} technical indicators for {symbol}."
        )
    except Exception as e:
        logger.error(f"Error saving technical indicators for {symbol}: {e}")
