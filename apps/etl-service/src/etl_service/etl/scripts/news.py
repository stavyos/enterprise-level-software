"""Script for saving market news data."""

import os
from datetime import date, datetime

from db_client.client import DBClient
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings
from loguru import logger


def news_saver(
    symbols: str | None,
    tags: str | None,
    from_date: date | None,
    to_date: date | None,
    limit: int,
    run_id: str,
) -> None:
    """Core logic for saving market news data."""
    client = EODHDClientBase(settings.eodhd_api_key).news

    db_client = DBClient(
        dbname=settings.db_name,
        user=settings.db_user,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )

    inserted_count = 0
    try:
        articles = client.get_news(
            symbols=symbols,
            tags=tags,
            from_date=from_date.isoformat() if from_date else None,
            to_date=to_date.isoformat() if to_date else None,
            limit=limit,
        )
        for article in articles:
            success = db_client.insert_market_news(
                date=datetime.fromisoformat(article.get("date").replace("Z", "+00:00"))
                if article.get("date")
                else None,
                title=article.get("title"),
                content=article.get("content"),
                link=article.get("link"),
                symbols=article.get("symbols", []),
                tags=article.get("tags", []),
            )
            if success:
                inserted_count += 1
        logger.info(f"Successfully inserted {inserted_count}/{len(articles)} news articles.")
    except Exception as e:
        logger.error(f"Error saving news: {e}")
