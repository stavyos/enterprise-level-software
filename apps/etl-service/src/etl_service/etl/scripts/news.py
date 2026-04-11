"""Script for saving market news data."""

from datetime import date, datetime
import os

from loguru import logger

from db_client.client import DBClient
from eodhd_client.client import EODHDClientBase


def news_saver(
    symbols: str | None,
    tags: str | None,
    from_date: date | None,
    to_date: date | None,
    limit: int,
    run_id: str,
) -> None:
    """Core logic for saving market news data."""
    api_key = os.getenv("EODHD_API_KEY")
    client = EODHDClientBase(api_key).news

    db_client = DBClient(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 5432)),
    )

    try:
        articles = client.get_news(
            symbols=symbols,
            tags=tags,
            from_date=from_date.isoformat() if from_date else None,
            to_date=to_date.isoformat() if to_date else None,
            limit=limit,
        )
        for article in articles:
            db_client.insert_market_news(
                date=datetime.fromisoformat(article["date"].replace("Z", "+00:00")),
                title=article["title"],
                content=article["content"],
                link=article["link"],
                symbols=article.get("symbols", []),
                tags=article.get("tags", []),
            )
        logger.info(f"Saved {len(articles)} news articles.")
    except Exception as e:
        logger.error(f"Error saving news: {e}")
