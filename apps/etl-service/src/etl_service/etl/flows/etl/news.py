"""Market news flow module."""

import datetime
import uuid

from loguru import logger
from prefect import flow

from etl_service.etl.deployments_settings.deployments.stocks.news import DeploymentNews
from etl_service.etl.flows.models.news import NewsSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.news import news_saver as _news_saver

DEPLOYMENT_NEWS = DeploymentNews()


@flow(**DEPLOYMENT_NEWS.saver_flow_decorator_args)
@enable_loguru_support
def market_news_saver(save_request: NewsSaveRequest) -> None:
    """Flow task to save market news."""
    logger.info(
        f"Running news saver for symbols={save_request.symbols}, tags={save_request.tags}"
    )
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
    """Orchestrates market news saving.

    The EODHD API only allows one ticker per request, so we split symbols and dispatch.
    """
    run_id = str(uuid.uuid4())

    if not symbols and not tags:
        raise ValueError(
            "Symbols or Tags must be supplied for market_news_saver_dispatcher."
        )

    params_list = []

    if symbols:
        # Support both "AAPL,MSFT" and "[AAPL,MSFT]" formats
        clean_symbols = symbols.strip("[]").replace(" ", "")
        symbol_list = [s for s in clean_symbols.split(",") if s]

        for symbol in symbol_list:
            params_list.append(
                {
                    "save_request": NewsSaveRequest(
                        symbols=symbol,
                        tags=tags,
                        from_date=from_date,
                        to_date=to_date,
                        limit=limit,
                        run_id=run_id,
                    )
                }
            )
    else:
        # Only tags provided
        params_list.append(
            {
                "save_request": NewsSaveRequest(
                    symbols=None,
                    tags=tags,
                    from_date=from_date,
                    to_date=to_date,
                    limit=limit,
                    run_id=run_id,
                )
            }
        )

    await DEPLOYMENT_NEWS.dispatch_sub_flows(params=params_list)
