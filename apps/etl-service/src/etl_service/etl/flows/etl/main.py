"""Main ETL flow orchestration module."""

import asyncio

from loguru import logger
from prefect import flow
from prefect.client.schemas import FlowRun, StateType

from etl_service.etl.deployments_settings.deployments.base import (
    AbstractDeploymentSettings,
)
from etl_service.etl.deployments_settings.deployments.stocks.eod import DeploymentEOD
from etl_service.etl.deployments_settings.deployments.stocks.exchanges import (
    DeploymentExchanges,
)
from etl_service.etl.deployments_settings.deployments.stocks.main import DeploymentMain
from etl_service.etl.deployments_settings.deployments.stocks.tickers import (
    DeploymentTickers,
)
from etl_service.etl.flows.utils import enable_loguru_support

DEPLOYMENT_MAIN = DeploymentMain()

TIERS: list[list[AbstractDeploymentSettings]] = [
    [DeploymentExchanges()],
    [DeploymentTickers()],
    [DeploymentEOD()],
]


@flow(**DEPLOYMENT_MAIN.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def main_saver_dispatcher() -> None:
    """Orchestrates the main ETL pipeline by running tiers of sub-flows sequentially.

    Runs each tier of deployments (Exchanges → Tickers → EOD) in order.
    Uses today's date as the business date and always fetches from virgin tickers.
    """

    for i, tier in enumerate(TIERS):
        logger.info(f"Started running tier number {i} :: {tier=}")

        results: list[FlowRun | Exception] = await asyncio.gather(
            *(
                deployment.dispatch_deployment_saver_dispatcher(parameters={})
                if isinstance(deployment, DeploymentExchanges)
                else deployment.dispatch_deployment_saver_dispatcher(
                    parameters={"exchange_codes": None}
                )
                if isinstance(deployment, DeploymentTickers)
                else deployment.dispatch_deployment_saver_dispatcher(
                    parameters={
                        "tickers": None,
                        "get_from_virgin": True,
                    }
                )
                for deployment in tier
            ),
            return_exceptions=True,
        )

        for deployment, result in zip(tier, results, strict=False):
            if isinstance(result, Exception):
                raise RuntimeError(
                    f"Flow {deployment} failed with, cannot continue with ETL execution"
                ) from result

            logger.info(
                f"Result received for {deployment=} with flow_run_id={str(result.id)} "
                f"and state {result.state_name}"
            )

            if result.state_type != StateType.COMPLETED:
                raise RuntimeError(
                    f"Flow {deployment} failed with status {result.state.type}, "
                    f"cannot continue with ETL execution"
                )

    return None
