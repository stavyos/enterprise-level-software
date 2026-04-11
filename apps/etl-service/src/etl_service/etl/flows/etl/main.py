"""Main ETL flow orchestration module."""

import asyncio
import datetime

from etl_service.etl.deployments_settings.deployments.base import AbstractDeploymentSettings
from etl_service.etl.deployments_settings.deployments.stocks.eod import DeploymentEOD
from etl_service.etl.deployments_settings.deployments.stocks.exchanges import DeploymentExchanges
from etl_service.etl.deployments_settings.deployments.stocks.intraday import DeploymentIntraday
from etl_service.etl.deployments_settings.deployments.stocks.main import DeploymentMain
from etl_service.etl.flows.utils import enable_loguru_support
from loguru import logger
from prefect import flow
from prefect.client.schemas import FlowRun, StateType

DEPLOYMENT_MAIN = DeploymentMain()

TIERS: list[list[AbstractDeploymentSettings]] = [
    [dep] for dep in [DeploymentExchanges(), DeploymentEOD(), DeploymentIntraday()]
]


@flow(**DEPLOYMENT_MAIN.saver_dispatcher_flow_decorator_args)
@enable_loguru_support
async def main_saver_dispatcher(bus_date: datetime.date | None = None) -> None:
    """Orchestrates the main ETL pipeline by running tiers of sub-flows sequentially.

    Args:
        bus_date (datetime.date | None, optional): The business date for which the ETL is running.
    """
    if not bus_date:
        bus_date = datetime.date.today()

    for i, tier in enumerate(TIERS):
        logger.info(f"Started running tear number {i} :: {tier=}")

        results: list[FlowRun | Exception] = await asyncio.gather(
            *(
                deployment.dispatch_deployment_saver_dispatcher(parameters={"bus_date": bus_date})
                for deployment in tier
            ),
            return_exceptions=True,
        )

        for deployment, result in zip(tier, results):
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
