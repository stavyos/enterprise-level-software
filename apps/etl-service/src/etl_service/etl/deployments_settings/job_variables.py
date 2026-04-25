"""Module for managing Kubernetes job variables for Prefect deployments."""

from typing import Any

from etl_service.etl.deployments_settings.enums import (
    PrefectDeployment,
    PrefectDeploymentType,
)


class ResourceLimits:
    """Class to represent Kubernetes resource limits (CPU and memory)."""

    def __init__(self, cpu: str | None = None, memory: str | None = None) -> None:
        """Initializes resource limits.

        Args:
            cpu (str | None): CPU limit (e.g., '2000m').
            memory (str | None): Memory limit (e.g., '4Gi').
        """
        self.cpu = cpu
        self.memory = memory

    @property
    def cpu(self) -> str | None:
        """CPU limit."""
        return self._cpu

    @cpu.setter
    def cpu(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise ValueError("CPU limit must be a string or None")
        self._cpu = value

    @property
    def memory(self) -> str | None:
        """Memory limit."""
        return self._memory

    @memory.setter
    def memory(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise ValueError("Memory limit must be a string or None")
        self._memory = value

    def to_dict(self) -> dict[str, str]:
        """Converts limits to a dictionary.

        Returns:
            dict[str, str]: Dictionary representation of limits.
        """
        result = {}
        if self._cpu is not None:
            result["cpu"] = self._cpu
        if self._memory is not None:
            result["memory"] = self._memory
        return result


class ResourceRequests:
    """Class to represent Kubernetes resource requests (CPU and memory)."""

    def __init__(
        self, cpu: str | float | int | None = None, memory: str | None = None
    ) -> None:
        """Initializes resource requests.

        Args:
            cpu (str | float | int | None): CPU request.
            memory (str | None): Memory request.
        """
        self.cpu = cpu
        self.memory = memory

    @property
    def cpu(self) -> str | None:
        """CPU request."""
        return self._cpu

    @cpu.setter
    def cpu(self, value: str | float | int | None) -> None:
        if isinstance(value, float | int):
            value = str(value)

        if value is not None and not isinstance(value, str):
            raise ValueError("CPU request must be a string or None")
        self._cpu = value

    @property
    def memory(self) -> str | None:
        """Memory request."""
        return self._memory

    @memory.setter
    def memory(self, value: str | None) -> None:
        if value is not None and not isinstance(value, str):
            raise ValueError("Memory request must be a string or None")
        self._memory = value

    def to_dict(self) -> dict[str, str]:
        """Converts requests to a dictionary.

        Returns:
            dict[str, str]: Dictionary representation of requests.
        """
        result = {}
        if self._cpu is not None:
            result["cpu"] = self._cpu
        if self._memory is not None:
            result["memory"] = self._memory
        return result


class JobResources:
    """Class to represent combined Kubernetes job resources (requests and limits)."""

    def __init__(
        self,
        limits: ResourceLimits | None = None,
        requests: ResourceRequests | None = None,
    ) -> None:
        """Initializes job resources.

        Args:
            limits (ResourceLimits | None): Resource limits.
            requests (ResourceRequests | None): Resource requests.
        """
        self.limits = limits if limits is not None else ResourceLimits()
        self.requests = requests if requests is not None else ResourceRequests()

    @property
    def limits(self) -> ResourceLimits:
        """Resource limits."""
        return self._limits

    @limits.setter
    def limits(self, value: ResourceLimits) -> None:
        if not isinstance(value, ResourceLimits):
            raise ValueError("Limits must be a ResourceLimits instance")
        self._limits = value

    @property
    def requests(self) -> ResourceRequests:
        """Resource requests."""
        return self._requests

    @requests.setter
    def requests(self, value: ResourceRequests) -> None:
        if not isinstance(value, ResourceRequests):
            raise ValueError("Requests must be a ResourceRequests instance")
        self._requests = value

    def to_dict(self) -> dict[str, dict[str, str]]:
        """Converts job resources to a dictionary.

        Returns:
            dict[str, dict[str, str]]: Dictionary representation of resources.
        """
        result = {}
        limits_dict = self._limits.to_dict()
        requests_dict = self._requests.to_dict()

        if limits_dict:
            result["limits"] = limits_dict
        if requests_dict:
            result["requests"] = requests_dict
        return result


class JobVariables:
    """Class to manage Prefect Job Variables for Kubernetes execution."""

    def __init__(
        self,
        deployment: PrefectDeployment,
        deployment_type: PrefectDeploymentType,
        job_resources: JobResources,
        pod_watch_timeout_seconds: int = 3600,
        job_ttl_sec: float | int = 43200,
    ) -> None:
        """Initializes job variables.

        Args:
            deployment (PrefectDeployment): The deployment type.
            deployment_type (PrefectDeploymentType): The subtype (Saver or Dispatcher).
            job_resources (JobResources): Resource specifications.
            pod_watch_timeout_seconds (int): Timeout for watching pod creation.
            job_ttl_sec (float | int): Time-to-live for the job after completion.
        """
        self._deployment = deployment
        self._deployment_type = deployment_type

        # Initialize properties
        self.pod_watch_timeout_seconds = pod_watch_timeout_seconds
        self._app_label = self._get_app_label()
        self.job_ttl_sec = job_ttl_sec

        if job_resources is None or not isinstance(job_resources, JobResources):
            raise ValueError("Job resources must be a JobResources instance")
        self._job_resources = job_resources

    def _get_app_label(self) -> str:
        """Generates a Kubernetes-compatible app label for the deployment.

        Returns:
            str: The generated app label.
        """
        dep = self._deployment.value
        type_ = self._deployment_type.value.lower()

        dep = dep.replace("_", "-")
        type_ = type_.replace("_", "-")

        return f"flow-{dep}-{type_}"

    @property
    def deployment(self) -> PrefectDeployment:
        """Prefect deployment enum."""
        return self._deployment

    @deployment.setter
    def deployment(self, value: PrefectDeployment) -> None:
        if not isinstance(value, PrefectDeployment):
            raise ValueError("Deployment must be a PrefectDeployment instance")
        self._deployment = value

    @property
    def pod_watch_timeout_seconds(self) -> int:
        """Pod watch timeout in seconds."""
        return self._pod_watch_timeout_seconds

    @pod_watch_timeout_seconds.setter
    def pod_watch_timeout_seconds(self, value: int | None) -> None:
        if not isinstance(value, int) or value <= 0:
            raise ValueError("Pod watch timeout seconds must be a positive integer")
        self._pod_watch_timeout_seconds = value

    @property
    def app_label(self) -> str:
        """Kubernetes app label."""
        return self._app_label

    @app_label.setter
    def app_label(self, value: str) -> None:
        if not isinstance(value, str):
            raise ValueError("App label must be a string")
        self._app_label = value

    @property
    def job_resources(self) -> JobResources:
        """Job resource specifications."""
        return self._job_resources

    @job_resources.setter
    def job_resources(self, value: JobResources) -> None:
        if not isinstance(value, JobResources):
            raise ValueError("Job resources must be a JobResources instance")
        self._job_resources = value

    @property
    def job_ttl_sec(self) -> float | int:
        """Job time-to-live in seconds."""
        return self._job_ttl_sec

    @job_ttl_sec.setter
    def job_ttl_sec(self, value: float | int) -> None:
        if not isinstance(value, float | int) or value <= 0:
            raise ValueError("Job TTL must be a positive float in seconds")
        self._job_ttl_sec = value

    def to_dict(self) -> dict[str, Any]:
        """Converts job variables to a dictionary compatible with Prefect worker expectations.

        Returns:
            dict[str, Any]: Configuration dictionary for the K8s worker.
        """
        from etl_service.etl.deployments_settings.settings import settings

        return {
            "active_deadline_seconds": int(self.job_ttl_sec),
            "pod_watch_timeout_seconds": self.pod_watch_timeout_seconds,
            "app_label": self.app_label,
            "job_resources": self.job_resources.to_dict(),
            "env": {
                "PREFECT_API_URL": settings.effective_prefect_api_url,
                "EODHD_API_KEY": settings.eodhd_api_key,
                "DB_HOST": settings.effective_db_host,
                "DB_PORT": str(settings.db_port),
                "DB_USER": settings.db_user,
                "DB_PASSWORD": settings.db_password,
                "DB_NAME": settings.db_name,
                "PYTHONPATH": settings.job_pythonpath,
                "ENV_PREFIX": settings.env_prefix,
            },
        }
