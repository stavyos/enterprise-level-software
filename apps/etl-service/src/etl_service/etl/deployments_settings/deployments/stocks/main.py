from etl_service.etl.deployments_settings.deployments.base import AbstractDeploymentSettings
from etl_service.etl.deployments_settings.enums import PrefectDeployment, PrefectDeploymentType
from etl_service.etl.deployments_settings.job_variables import JobVariables


class DeploymentMain(AbstractDeploymentSettings):
    """Deployment settings for the MAIN ETL flow."""

    def __init__(self) -> None:
        """Initializes the DeploymentMain with the corresponding PrefectDeployment."""
        super().__init__(deployment=PrefectDeployment.MAIN)

    @property
    def is_saver_available(self) -> bool:
        """Availability of the saver deployment."""
        return False

    @property
    def is_saver_dispatcher_available(self) -> bool:
        """Availability of the saver dispatcher deployment."""
        return True

    @property
    def flows_module(self) -> str:
        """The Python module containing the flows for this deployment."""
        return "main.py"

    @property
    def saver_job_variables(self) -> JobVariables | None:
        """Kubernetes job variables for the saver."""
        return None

    @property
    def saver_dispatcher_job_variables(self) -> JobVariables | None:
        """Kubernetes job variables for the saver dispatcher."""
        return self._get_job_variables_gigabytes(
            deployment_type=PrefectDeploymentType.DISPATCHER, cpu_request=1, mem_request=2
        )
