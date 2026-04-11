"""Script for saving economic events data."""

from datetime import date
import os
from eodhd_client.client import EODHDClientBase
from db_client.client import DBClient
from loguru import logger


def economic_events_saver(from_date: date, to_date: date, country: str | None, run_id: str) -> None:
    """Core logic for saving economic events data."""
    api_key = os.getenv("EODHD_API_KEY")
    client = EODHDClientBase(api_key).economic
    
    db_client = DBClient(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    try:
        events = client.get_economic_events(
            from_date=from_date.isoformat(),
            to_date=to_date.isoformat(),
            country=country
        )
        for event in events:
            db_client.insert_economic_event(
                event_date=date.fromisoformat(event["date"]),
                country=event["country"],
                event_type=event["type"],
                value=float(event["value"]) if event["value"] else None,
                previous_value=float(event["previous"]) if event["previous"] else None,
                unit=event["unit"],
                comparison=event.get("comparison")
            )
        logger.info(f"Saved {len(events)} economic events.")
    except Exception as e:
        logger.error(f"Error saving economic events: {e}")
