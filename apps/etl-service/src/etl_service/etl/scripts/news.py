"""Script for saving market news data."""

from datetime import date, datetime

from loguru import logger

from db_client.client import DBClient
from db_client.models import MarketNews
from eodhd_client.client import EODHDClientBase
from etl_service.etl.deployments_settings.settings import settings


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
        host=settings.effective_db_host,
        port=settings.db_port,
    )

    try:
        # EODHD hard limit per request is 1000.
        # We paginate using 'offset' to get "as much as possible".
        request_limit = 1000
        current_offset = 0
        all_articles = []

        logger.info(
            f"Starting paginated news fetch for {symbols or tags} (Target: {limit})"
        )

        while len(all_articles) < limit:
            # Calculate how many to fetch in this batch
            remaining = limit - len(all_articles)
            batch_limit = min(remaining, request_limit)

            batch = client.get_news(
                symbols=symbols,
                tags=tags,
                from_date=from_date.isoformat() if from_date else None,
                to_date=to_date.isoformat() if to_date else None,
                limit=batch_limit,
                offset=current_offset,
            )

            if not batch:
                break

            all_articles.extend(batch)
            current_offset += len(batch)

            logger.info(
                f"Fetched batch of {len(batch)} articles (Total: {len(all_articles)})"
            )

            # If the API returned less than we asked for, we've hit the end of history
            if len(batch) < batch_limit:
                break

        total_articles = len(all_articles)
        if total_articles == 0:
            logger.warning(f"No news articles found for symbols={symbols}, tags={tags}")
            return

        objects_to_upsert = []
        for article in all_articles:
            news = MarketNews(
                date=datetime.fromisoformat(article.get("date").replace("Z", "+00:00"))
                if article.get("date")
                else None,
                title=article.get("title"),
                content=article.get("content"),
                link=article.get("link"),
                symbols=article.get("symbols", []),
                tags=article.get("tags", []),
            )
            objects_to_upsert.append(news)

        success = db_client.bulk_upsert(objects_to_upsert)
        if success:
            logger.info(
                f"Successfully inserted {len(objects_to_upsert)}/{total_articles} news articles."
            )
        else:
            logger.error("Failed to bulk upsert news articles")

    except Exception as e:
        logger.error(f"Error saving news: {e}")
