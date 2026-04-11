"""Technical indicators flow module."""

import uuid

from etl_service.etl.deployments_settings.deployments.stocks.technical import (
    DeploymentTechnical,
)
from etl_service.etl.flows.models.technical import TechnicalIndicatorSaveRequest
from etl_service.etl.flows.utils import enable_loguru_support
from etl_service.etl.scripts.technical import (
    technical_indicator_saver as _technical_indicator_saver,
)
from loguru import logger
from prefect import flow

DEPLOYMENT_TECHNICAL = DeploymentTechnical()


@flow(**DEPLOYMENT_TECHNICAL.saver_flow_decorator_args)
@enable_loguru_support
def technical_indicators_saver(save_request: TechnicalIndicatorSaveRequest) -> None:
    """Flow task to save technical indicators."""
    logger.info(
        f"Running technical indicator saver for {save_request.symbol} "
        f"function={save_request.function}"
    )
    _technical_indicator_saver(
        symbol=save_request.symbol,
        exchange=save_request.exchange,
        function=save_request.function,
        period=save_request.period,
        run_id=save_request.run_id,
    )


@flow(**DEPLOYMENT_TECHNICAL.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def technical_indicators_saver_dispatcher(
    tickers: list[dict], function: str, period: int | None = None
) -> None:
    """Orchestrates technical indicators saving."""
    if not tickers:
        raise ValueError("Tickers must be supplied for technical_indicators_saver_dispatcher.")

    run_id = str(uuid.uuid4())

    params_list = [
        {
            "save_request": TechnicalIndicatorSaveRequest(
                symbol=t["symbol"],
                exchange=t["exchange"],
                function=function,
                period=period,
                run_id=run_id,
            )
        }
        for t in tickers
    ]

    await DEPLOYMENT_TECHNICAL.dispatch_sub_flows(params=params_list)
