"""Market news flow module."""

import datetime
import uuid

from etl_service.etl.deployments_settings.deployments.stocks.news import DeploymentNews
from etl_service.etl.flows.models.news import NewsSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.news import news_saver as _news_saver
from loguru import logger
from prefect import flow

DEPLOYMENT_NEWS = DeploymentNews()


@flow(**DEPLOYMENT_NEWS.saver_flow_decorator_args)
@enable_loguru_support
def market_news_saver(save_request: NewsSaveRequest) -> None:
    """Flow task to save market news."""
    logger.info(f"Running news saver for symbols={save_request.symbols}, tags={save_request.tags}")
    _news_saver(
        symbols=save_request.symbols,
        tags=save_request.tags,
        from_date=save_request.from_date,
        to_date=save_request.to_date,
        limit=save_request.limit,
        run_id=save_request.run_id,
    )


@flow(**DEPLOYMENT_NEWS.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def market_news_saver_dispatcher(
    symbols: str | None = None,
    tags: str | None = None,
    from_date: datetime.date | None = None,
    to_date: datetime.date | None = None,
    limit: int = 50,
) -> None:
    """Orchestrates market news saving."""
    run_id = str(uuid.uuid4())

    # Simple dispatch for now
    params_list = [
        {
            "save_request": NewsSaveRequest(
                symbols=symbols,
                tags=tags,
                from_date=from_date,
                to_date=to_date,
                limit=limit,
                run_id=run_id,
            )
        }
    ]

    await DEPLOYMENT_NEWS.dispatch_sub_flows(params=params_list)
