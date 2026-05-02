"""Intraday ETL flow module."""

import datetime

from loguru import logger
from prefect import flow

from etl_service.etl.deployments_settings.deployments.stocks.intraday import (
    DeploymentIntraday,
)
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.intraday import intraday_saver as _intraday_saver

DEPLOYMENT_INTRADAY = DeploymentIntraday()


@flow(**DEPLOYMENT_INTRADAY.saver_flow_decorator_args)
@enable_loguru_support
def intraday_saver(
    tickers: list[str],
    bus_date: datetime.date | None = None,
    start_timestamp: int | None = None,
    end_timestamp: int | None = None,
) -> None:
    """Saver flow for intraday data.

    Args:
        tickers (list[str]): List of stock tickers.
        bus_date (datetime.date | None, optional): Single date.
        start_timestamp (int | None, optional): Start timestamp for range.
        end_timestamp (int | None, optional): End timestamp for range.
    """
    msg = f"Running Intraday saver for tickers={tickers}"
    if bus_date:
        msg += f", bus_date={bus_date}"
    if start_timestamp:
        msg += f", range={start_timestamp} to {end_timestamp}"
    logger.info(msg)

    _intraday_saver(
        tickers=tickers,
        bus_date=bus_date,
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
    )


@flow(**DEPLOYMENT_INTRADAY.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def intraday_saver_dispatcher(
    bus_date: datetime.date | None = None,
    end_date: datetime.date | None = None,
    tickers: list[str] = None,
) -> None:
    """Dispatcher flow for intraday data. Supports 120-day chunked backfills.

    Args:
        bus_date (datetime.date | None, optional): Start business date. Defaults to today.
        end_date (datetime.date | None, optional): End business date for range fetch.
        tickers (list[str]): List of stock tickers.
    """
    if not bus_date:
        bus_date = datetime.date.today()

    if not tickers:
        raise ValueError("Tickers must be supplied for intraday_saver_dispatcher.")

    # Determine range and chunks
    if end_date:
        if end_date < bus_date:
            raise ValueError(f"end_date ({end_date}) must be >= bus_date ({bus_date})")

        logger.info(
            f"Starting optimized intraday backfill from {bus_date} to {end_date}"
        )

        # EODHD limit for 1m data is 120 days per request.
        # We split the requested range into 120-day chunks.
        chunks = []
        current_start = bus_date
        while current_start <= end_date:
            current_end = min(current_start + datetime.timedelta(days=119), end_date)

            # Convert to timestamps
            ts_start = int(
                datetime.datetime.combine(current_start, datetime.time.min).timestamp()
            )
            ts_end = int(
                datetime.datetime.combine(current_end, datetime.time.max).timestamp()
            )

            chunks.append((ts_start, ts_end))
            current_start = current_end + datetime.timedelta(days=1)

        params_list = []
        for ts_start, ts_end in chunks:
            for ticker in tickers:
                params_list.append(
                    {
                        "tickers": [ticker],
                        "start_timestamp": ts_start,
                        "end_timestamp": ts_end,
                    }
                )
    else:
        logger.info(f"Starting single-day intraday fetch for {bus_date}")
        params_list = [
            {"bus_date": bus_date, "tickers": [ticker]} for ticker in tickers
        ]

    if not params_list:
        logger.warning("No valid range found to process.")
        return

    logger.info(f"Dispatching {len(params_list)} total optimized sub-flows.")
    await DEPLOYMENT_INTRADAY.dispatch_sub_flows(params=params_list)
