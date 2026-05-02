"""EOD flow module for processing End-Of-Day stock data."""

import datetime
import uuid

from loguru import logger
from prefect import flow

from etl_service.etl.deployments_settings.deployments.stocks.eod import DeploymentEOD
from etl_service.etl.flows.models.eod import EOD, EODSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.eod import eod_saver as _eod_saver

DEPLOYMENT_EOD = DeploymentEOD()


def _get_tickers_chunks(
    tickers: list[str],
    chunk_size: int,
    from_date: datetime.date,
    to_date: datetime.date,
    run_id: str,
) -> list[EODSaveRequest]:
    """Splits the list of tickers into smaller chunks of specified size.

    Args:
        tickers (list[str]): List of stock tickers.
        chunk_size (int): The number of tickers per chunk.
        from_date (datetime.date): Start date.
        to_date (datetime.date): End date.
        run_id (str): Unique identifier for the run.

    Returns:
        list[EODSaveRequest]: A list of save request objects for each chunk.
    """
    chunks = []
    for i in range(0, len(tickers), chunk_size):
        chunk = tickers[i : i + chunk_size]
        chunks.append(
            EODSaveRequest(
                from_date=from_date,
                to_date=to_date,
                tickers=[EOD(ticker=ticker) for ticker in chunk],
                run_id=run_id,
            )
        )
    return chunks


@flow(**DEPLOYMENT_EOD.saver_flow_decorator_args)
@enable_loguru_support
def eod_saver(save_request: EODSaveRequest) -> None:
    """Flow task to save End-Of-Day data for a chunk of tickers.

    Args:
        save_request (EODSaveRequest): The request containing date range, tickers, and run ID.
    """
    from_date = save_request.from_date
    to_date = save_request.to_date
    run_id = save_request.run_id
    tickers = [eod.ticker for eod in save_request.tickers]

    logger.info(
        f"Running EOD saver for range={from_date} to {to_date}, run_id={run_id}, tickers count={len(tickers)}"
    )

    if len(tickers) > 5:
        raise ValueError(f"Too many tickers provided: {len(tickers)}, max allowed is 5")

    _eod_saver(from_date=from_date, to_date=to_date, tickers=tickers, run_id=run_id)

    logger.info(
        f"EOD saver completed for range={from_date} to {to_date}, run_id={run_id}"
    )


@flow(**DEPLOYMENT_EOD.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def eod_saver_dispatcher(
    from_date: datetime.date = None,
    to_date: datetime.date = None,
    tickers: list[str] = None,
) -> None:
    """Orchestrates EOD data saving by dispatching multiple parallel saver flows.

    Args:
        from_date (datetime.date): Start date. Defaults to 1800-01-01.
        to_date (datetime.date): End date. Defaults to today + 1 day.
        tickers (list[str]): List of tickers to process.
    """
    if from_date is None:
        from_date = datetime.date(1800, 1, 1)
    if to_date is None:
        to_date = datetime.date.today() + datetime.timedelta(days=1)
    logger.info(f"Running EOD dispatcher saver for range: {from_date} to {to_date}")

    if not tickers:
        raise ValueError("Tickers must be supplied for eod_saver_dispatcher.")

    run_id = str(uuid.uuid4())

    # Update saver to accept the full range
    chunks = _get_tickers_chunks(
        tickers=tickers,
        chunk_size=2,
        from_date=from_date,
        to_date=to_date,
        run_id=run_id,
    )
    params_list = [
        {
            "save_request": chunk,
        }
        for chunk in chunks
    ]

    results = await DEPLOYMENT_EOD.dispatch_sub_flows(params=params_list)

    for _ in results:
        pass

    logger.info(
        f"EOD dispatcher saver completed for range: {from_date} to {to_date} for run_id={run_id}"
    )
