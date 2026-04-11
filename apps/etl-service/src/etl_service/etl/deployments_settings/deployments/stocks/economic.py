from etl_service.etl.deployments_settings.deployments.base import AbstractDeploymentSettings
from etl_service.etl.deployments_settings.enums import PrefectDeployment, PrefectDeploymentType
from etl_service.etl.deployments_settings.job_variables import JobVariables


class DeploymentEconomic(AbstractDeploymentSettings):
    """Deployment settings for the Economic Events ETL flow."""

    def __init__(self) -> None:
        super().__init__(deployment=PrefectDeployment.ECONOMIC_EVENTS)

    @property
    def is_saver_available(self) -> bool:
        return True

    @property
    def is_saver_dispatcher_available(self) -> bool:
        return True

    @property
    def flows_module(self) -> str:
        return "economic.py"

    @property
    def saver_job_variables(self) -> JobVariables | None:
        return self._get_job_variables_gigabytes(
            deployment_type=PrefectDeploymentType.SAVER, cpu_request=1, mem_request=1
        )

    @property
    def saver_dispatcher_job_variables(self) -> JobVariables | None:
        return self._get_job_variables_gigabytes(
            deployment_type=PrefectDeploymentType.DISPATCHER, cpu_request=1, mem_request=1
        )
