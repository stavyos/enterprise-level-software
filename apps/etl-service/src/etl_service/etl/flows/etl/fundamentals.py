"""Fundamentals flow module for processing stock fundamental data."""

import datetime
import uuid

from etl_service.etl.deployments_settings.deployments.stocks.fundamentals import DeploymentFundamentals
from etl_service.etl.flows.models.fundamentals import Fundamental, FundamentalSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.fundamentals import fundamentals_saver as _fundamentals_saver
from loguru import logger
from prefect import flow

DEPLOYMENT_FUNDAMENTALS = DeploymentFundamentals()


def _get_tickers_chunks(
    tickers: list[dict], chunk_size: int, updated_at: datetime.date, run_id: str
) -> list[FundamentalSaveRequest]:
    """Splits the list of tickers into smaller chunks."""
    chunks = []
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i : i + chunk_size]
        chunks.append(
            FundamentalSaveRequest(
                updated_at=updated_at,
                tickers=[Fundamental(symbol=t["symbol"], exchange=t["exchange"]) for t in chunk],
                run_id=run_id
            )
        )
    return chunks


@flow(**DEPLOYMENT_FUNDAMENTALS.saver_flow_decorator_args)
@enable_loguru_support
def fundamentals_saver(save_request: FundamentalSaveRequest) -> None:
    """Flow task to save fundamental data for a chunk of tickers."""
    updated_at = save_request.updated_at
    run_id = save_request.run_id
    tickers = [{"symbol": t.symbol, "exchange": t.exchange} for t in save_request.tickers]

    logger.info(f"Running fundamentals saver for updated_at={updated_at}, run_id={run_id}, tickers count={len(tickers)}")

    _fundamentals_saver(updated_at=updated_at, tickers=tickers, run_id=run_id)


@flow(**DEPLOYMENT_FUNDAMENTALS.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def fundamentals_saver_dispatcher(updated_at: datetime.date, tickers: list[dict] | None = None) -> None:
    """Orchestrates fundamentals data saving."""
    logger.info(f"Running fundamentals dispatcher saver for updated_at={updated_at}")

    run_id = str(uuid.uuid4())

    if not tickers:
        # For testing
        tickers = [
            {"symbol": "AAPL", "exchange": "US"},
            {"symbol": "MSFT", "exchange": "US"},
        ]

    chunks = _get_tickers_chunks(
        tickers=tickers,
        chunk_size=1,  # Fundamentals are heavy, process 1 by 1
        updated_at=updated_at,
        run_id=run_id,
    )
    params_list = [{"save_request": chunk} for chunk in chunks]

    await DEPLOYMENT_FUNDAMENTALS.dispatch_sub_flows(params=params_list)
    logger.info(f"Fundamentals dispatcher saver completed for run_id={run_id}")
