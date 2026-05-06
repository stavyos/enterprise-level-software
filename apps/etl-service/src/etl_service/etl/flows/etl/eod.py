"""EOD flow module for processing End-Of-Day stock data."""

import datetime
import uuid

from loguru import logger
from prefect import flow

from db_client.client import DBClient
from db_client.models import VirginTicker
from etl_service.etl.deployments_settings.deployments.stocks.eod import DeploymentEOD
from etl_service.etl.deployments_settings.settings import settings
from etl_service.etl.flows.models.eod import EODSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support, track_resources
from etl_service.etl.scripts.eod import eod_saver as _eod_saver

DEPLOYMENT_EOD = DeploymentEOD()


def _create_save_requests(
    tickers: list[str],
    from_date: datetime.date,
    to_date: datetime.date,
    run_id: str,
) -> list[EODSaveRequest]:
    """Creates individual save requests for each ticker.

    Args:
        tickers (list[str]): List of stock tickers.
        from_date (datetime.date): Start date.
        to_date (datetime.date): End date.
        run_id (str): Unique identifier for the run.

    Returns:
        list[EODSaveRequest]: A list of save request objects.
    """
    return [
        EODSaveRequest(
            from_date=from_date,
            to_date=to_date,
            ticker=ticker,
            run_id=run_id,
        )
        for ticker in tickers
    ]


@flow(**DEPLOYMENT_EOD.saver_flow_decorator_args)
@enable_loguru_support
@track_resources
def eod_saver(save_request: EODSaveRequest) -> None:
    """Flow task to save End-Of-Day data for a single ticker.

    Args:
        save_request (EODSaveRequest): The request containing dates, ticker, and run ID.
    """
    from_date = save_request.from_date
    to_date = save_request.to_date
    run_id = save_request.run_id
    ticker = save_request.ticker

    logger.info(
        f"Running EOD saver from {from_date} to {to_date}, run_id={run_id}, ticker={ticker}"
    )

    _eod_saver(from_date=from_date, to_date=to_date, tickers=[ticker], run_id=run_id)

    logger.info(f"EOD saver completed from {from_date} to {to_date}, run_id={run_id}")


@flow(**DEPLOYMENT_EOD.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
@track_resources
async def eod_saver_dispatcher(
    from_date: datetime.date | None = None,
    to_date: datetime.date | None = None,
    tickers: list[str] | None = None,
    get_from_virgin: bool = False,
) -> None:
    """Orchestrates EOD data saving by dispatching multiple parallel saver flows.

    Args:
        from_date (datetime.date | None, optional): Start date. Defaults to 1900-01-01.
        to_date (datetime.date | None, optional): End date. Defaults to today + 1.
        tickers (list[str] | None, optional): List of tickers to process. Defaults to None.
        get_from_virgin (bool, optional): Whether to fetch virgin tickers. Defaults to False.
    """
    if get_from_virgin:
        db_client = DBClient(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.effective_db_host,
            port=settings.db_port,
        )
        with db_client._session() as session:
            virgin_records = (
                session.query(VirginTicker)
                .filter(VirginTicker.first_eod_bus_date.is_(None))
                .limit(800)
                .all()
            )
            tickers = [f"{vt.ticker}.{vt.exchange}" for vt in virgin_records]

    if not tickers:
        logger.info("No tickers found to process.")
        return

    if not from_date:
        from_date = datetime.date(1900, 1, 1)

    if not to_date:
        to_date = datetime.date.today() + datetime.timedelta(days=1)

    logger.info(f"Running EOD dispatcher saver from {from_date} to {to_date}")

    if not tickers:
        raise ValueError("Tickers must be supplied for eod_saver_dispatcher.")

    run_id = str(uuid.uuid4())

    save_requests = _create_save_requests(
        tickers=tickers,
        from_date=from_date,
        to_date=to_date,
        run_id=run_id,
    )
    params_list = [
        {
            "save_request": req,
        }
        for req in save_requests
    ]

    results = await DEPLOYMENT_EOD.dispatch_sub_flows(params=params_list)

    for _ in results:
        pass

    # TODO (syosef): Add new function update_latest_run

    logger.info(
        f"EOD dispatcher saver completed from {from_date} to {to_date} for run_id={run_id}"
    )
