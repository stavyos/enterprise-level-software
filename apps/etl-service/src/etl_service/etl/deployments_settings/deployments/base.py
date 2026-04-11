import asyncio
import os
import random
import string
from abc import ABC, abstractmethod
from importlib.util import module_from_spec, spec_from_file_location
from typing import Any, Callable

from etl_service.etl.deployments_settings.deps_utils import (
    get_deployment_flow_name,
    get_deployment_name,
)
from etl_service.etl.deployments_settings.enums import PrefectDeployment, PrefectDeploymentType
from etl_service.etl.deployments_settings.job_variables import (
    JobResources,
    JobVariables,
    ResourceLimits,
    ResourceRequests,
)
from etl_service.etl.flows.locator import get_path
from loguru import logger
from prefect.client.schemas import FlowRun
from prefect.deployments import run_deployment
from prefect.flows import Flow
from prefect.schedules import Schedule


class AbstractDeploymentSettings(ABC):
    """Abstract base class for defining Prefect deployment settings for ETL flows.

    This class provides common configuration and utility methods for managing
    Prefect deployments, including work pool settings, source directories,
    and resource requirements.
    """

    # region Constants
    WORK_POOL = "my-k8s-pool"

    WP_QUEUE_DEFAULT = "default"

    SOURCE_DEFAULT = str(get_path().absolute())
    SAVER_RETRIES_DEFAULT = 3
    SAVER_RETRY_DELAY_DEFAULT = 60
    SAVER_TIMEOUT_SECONDS_DEFAULT = 15 * 60  # 15 minutes
    MEMORY_LIMIT_MULTIPLIER = 4

    SCHEDULES_MAIN_HOUR = 9
    SCHEDULES_MONDAY_TO_FRIDAY = "1-5"
    SCHEDULES_DEFAULT_CRON = "daily"

    FLOW_RUN_NAME_SUFFIX = "END"

    # endregion

    def __init__(self, deployment: PrefectDeployment) -> None:
        """Initializes the deployment settings with a specific deployment type.

        Args:
            deployment (PrefectDeployment): The specific deployment enum value.
        """
        self.deployment = deployment

    # region Work Pool Properties
    @property
    def work_pool(self) -> str:
        """Work pool for the deployment."""
        return f"{self.WORK_POOL}"

    @property
    def work_pool_queue(self) -> str:
        """Work pool queue for the deployment."""
        return self.WP_QUEUE_DEFAULT

    # endregion

    # region Availability Properties
    @property
    @abstractmethod
    def is_saver_available(self) -> bool:
        """Check if the saver deployment type is available."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    @abstractmethod
    def is_saver_dispatcher_available(self) -> bool:
        """Check if the saver dispatcher deployment type is available."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    def get_is_available(self, deployment_type: PrefectDeploymentType) -> bool:
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.is_saver_available
            case PrefectDeploymentType.DISPATCHER:
                return self.is_saver_dispatcher_available
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # endregion

    # region Source and Module Properties
    @property
    def source_directory(self) -> str:
        """Source directory for the deployment."""
        # Use absolute path for Docker/K8s development
        # to ensure Prefect finds the source in the container
        return "/app/apps/etl-service/src/etl_service/etl/flows/etl"

    @property
    @abstractmethod
    def flows_module(self) -> str:
        """Module containing the flows for the deployment."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    # endregion

    # region Flow Name Properties
    @property
    def saver_flow_name(self) -> str:
        """Flow name for the saver deployment type."""
        return get_deployment_flow_name(
            deployment=self.deployment, deployment_type=PrefectDeploymentType.SAVER
        )

    @property
    def saver_dispatcher_flow_name(self) -> str:
        """Flow name for the saver dispatcher deployment type."""
        return get_deployment_flow_name(
            deployment=self.deployment, deployment_type=PrefectDeploymentType.DISPATCHER
        )

    def get_flow_name(self, deployment_type: PrefectDeploymentType) -> str:
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.saver_flow_name
            case PrefectDeploymentType.DISPATCHER:
                return self.saver_dispatcher_flow_name
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # endregion

    # region Flow Run Name Properties
    @staticmethod
    def _gen_random_string(k: int) -> str:
        """Generate a random string of k length."""
        characters = string.ascii_letters + string.digits
        random_string = "".join(random.choices(characters, k=k))
        return random_string

    def _get_flow_run_name(
        self,
        flow_name: str,
        with_chunk_size: bool,
        suffix: str = FLOW_RUN_NAME_SUFFIX,
    ) -> str:
        """Generate flow run name with optional chunk size."""
        if with_chunk_size:
            name = f"{flow_name}-{self.saver_chunks_size}-{suffix}"
        else:
            name = f"{flow_name}-{suffix}"

        if len(name) > 60:  # Kubernetes Jobs also have a limit of 63 characters for names
            raise ValueError(
                f"Flow run name '{name}' is too long, must be less than 60 characters."
            )

        rnd_str = self._gen_random_string(k=63 - len(name))
        return f"{name}-{rnd_str}"

    @property
    def saver_flow_run_name(self) -> str:
        """Flow run name for the saver deployment type with random number."""
        return self._get_flow_run_name(self.saver_flow_name, with_chunk_size=False)

    @property
    def saver_dispatcher_flow_run_name(self) -> str:
        """Flow run name for the dispatcher deployment type with random number."""
        return self._get_flow_run_name(self.saver_dispatcher_flow_name, with_chunk_size=False)

    def get_flow_run_name(self, deployment_type: PrefectDeploymentType) -> str:
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.saver_flow_run_name
            case PrefectDeploymentType.DISPATCHER:
                return self.saver_dispatcher_flow_run_name
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # endregion

    # region Flow Function Properties
    @staticmethod
    def _load_function_from_file(file_path: str, function_name: str) -> Callable:
        module_name = os.path.splitext(os.path.basename(file_path))[0]
        spec = spec_from_file_location(module_name, file_path)
        if spec is None:
            raise ImportError(f"Could not load spec from file: {file_path}")

        module = module_from_spec(spec)
        spec.loader.exec_module(module)

        if hasattr(module, function_name):
            return getattr(module, function_name)
        else:
            raise AttributeError(f"Function '{function_name}' not found in {file_path}")

    def _get_flow_function(
        self,
        is_available: bool,
        function_name: str,
    ) -> Flow | None:
        if not is_available:
            return None

        # For loading locally during registration, use the current working directory
        # which is apps/etl-service when running via nx
        from prefect.flows import load_flow_from_entrypoint

        entrypoint = f"src/etl_service/etl/flows/etl/{self.flows_module}:{function_name}"
        return load_flow_from_entrypoint(entrypoint)

    @property
    def saver_flow_function(self) -> Flow | None:
        return self._get_flow_function(
            is_available=self.is_saver_available,
            function_name=self.saver_flow_function_name,
        )

    @property
    def saver_dispatcher_flow_function(self) -> Flow | None:
        return self._get_flow_function(
            is_available=self.is_saver_dispatcher_available,
            function_name=self.saver_dispatcher_flow_function_name,
        )

    # endregion

    # region Flow Function Name Properties
    def _flow_function_name(self, deployment_type: PrefectDeploymentType) -> str:
        dep = self.deployment.value.lower().replace(" ", "_")
        type_ = deployment_type.value.lower().replace(" ", "_")

        return f"{dep}_{type_}"

    @property
    def saver_flow_function_name(self) -> str:
        """Get flow function name for the saver deployment type."""
        return self._flow_function_name(deployment_type=PrefectDeploymentType.SAVER)

    @property
    def saver_dispatcher_flow_function_name(self) -> str:
        """Get flow function name for the dispatcher deployment type."""
        return self._flow_function_name(deployment_type=PrefectDeploymentType.DISPATCHER)

    # endregion

    # region Entry Point Properties
    def _get_entry_point(self, deployment_type: PrefectDeploymentType) -> str:
        function_name = self._flow_function_name(deployment_type=deployment_type)
        return f"{self.flows_module}:{function_name}"

    @property
    def saver_entry_point(self) -> str:
        """Get entry point for the saver deployment type."""
        return self._get_entry_point(deployment_type=PrefectDeploymentType.SAVER)

    @property
    def saver_dispatcher_entry_point(self) -> str:
        """Get entry point for the dispatcher deployment type."""
        return self._get_entry_point(deployment_type=PrefectDeploymentType.DISPATCHER)

    def get_entry_point(self, deployment_type: PrefectDeploymentType) -> str:
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.saver_entry_point
            case PrefectDeploymentType.DISPATCHER:
                return self.saver_dispatcher_entry_point
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # endregion

    # region Deployment Run Name Properties
    @property
    def saver_deployment_run_name(self) -> str:
        """Get deployment run name."""
        dep_name = get_deployment_name(
            deployment=self.deployment, deployment_type=PrefectDeploymentType.SAVER
        )
        return f"{self.saver_flow_name}/{dep_name}"

    @property
    def saver_dispatcher_deployment_run_name(self) -> str:
        """Get deployment run name."""
        dep_name = get_deployment_name(
            deployment=self.deployment, deployment_type=PrefectDeploymentType.DISPATCHER
        )
        return f"{self.saver_dispatcher_flow_name}/{dep_name}"

    def get_deployment_run_name(self, deployment_type: PrefectDeploymentType) -> str:
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.saver_deployment_run_name
            case PrefectDeploymentType.DISPATCHER:
                return self.saver_dispatcher_deployment_run_name
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # endregion

    # region Deployment Name Properties
    @property
    def saver_deployment_name(self) -> str:
        """Get deployment name for the saver deployment type."""
        return get_deployment_name(
            deployment=self.deployment, deployment_type=PrefectDeploymentType.SAVER
        )

    @property
    def saver_dispatcher_deployment_name(self) -> str:
        """Get deployment name for the dispatcher deployment type."""
        return get_deployment_name(
            deployment=self.deployment, deployment_type=PrefectDeploymentType.DISPATCHER
        )

    def get_deployment_name(self, deployment_type: PrefectDeploymentType) -> str:
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.saver_deployment_name
            case PrefectDeploymentType.DISPATCHER:
                return self.saver_dispatcher_deployment_name
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # endregion

    # region Saver Configuration Properties
    @property
    def saver_retries(self) -> int | None:
        """Number of retries for saver operations."""
        return self.SAVER_RETRIES_DEFAULT

    @property
    def saver_retry_delay(self) -> int | None:
        """Retry delay in seconds for saver operations."""
        return self.SAVER_RETRY_DELAY_DEFAULT

    @property
    def saver_timeout_seconds(self) -> int | None:
        """Timeout in seconds for saver operations."""
        return None

    @property
    def saver_chunks_size(self) -> int | None:
        """Chunk size for processing."""
        return None

    # endregion

    # region Flow Decorator Args Properties
    @property
    def saver_flow_decorator_args(self) -> dict[str, str | int]:
        """Get the arguments for the flow decorator for saver flows."""
        return {
            "name": self.saver_flow_name,
            "flow_run_name": self.saver_deployment_run_name,
            "retries": self.saver_retries,
            "retry_delay_seconds": self.saver_retry_delay,
        }

    @property
    def saver_dispatcher_flow_decorator_args(self) -> dict[str, str]:
        """Get the arguments for the flow decorator for saver dispatcher flows."""
        return {
            "name": self.saver_dispatcher_flow_name,
            "flow_run_name": self.saver_dispatcher_deployment_run_name,
        }

    # endregion

    # region Job Variables Properties
    def _get_job_variables(
        self,
        deployment_type: PrefectDeploymentType,
        cpu_request: str | float | int | None = None,
        cpu_limit: str | float | int | None = None,
        mem_request: str | None = None,
        mem_limit: str | None = None,
        ttl: float = 43200,  # Default TTL in seconds (12 hours)
    ) -> JobVariables:
        """Get default job variables for the saver deployment type."""
        jr_requests = ResourceRequests()
        jr_limits = ResourceLimits()

        if cpu_request is not None:
            jr_requests.cpu = cpu_request
        if cpu_limit is not None:
            jr_limits.cpu = cpu_limit
        if mem_request is not None:
            jr_requests.memory = mem_request
        if mem_limit is not None:
            jr_limits.memory = mem_limit

        jr = JobResources(
            requests=jr_requests,
            limits=jr_limits,
        )

        jv = JobVariables(
            deployment=self.deployment,
            deployment_type=deployment_type,
            job_resources=jr,
            job_ttl_sec=ttl,
        )

        if cpu_request is not None:
            jv.job_resources.requests.cpu = cpu_request
        if cpu_limit is not None:
            jv.job_resources.limits.cpu = cpu_limit
        if mem_request is not None:
            jv.job_resources.requests.memory = mem_request
        if mem_limit is not None:
            jv.job_resources.limits.memory = mem_limit

        if ttl is not None:
            jv.job_ttl = ttl

        return jv

    def _get_job_variables_gigabytes(
        self,
        deployment_type: PrefectDeploymentType,
        cpu_request: float | int | None = None,
        cpu_limit: float | int | None = None,
        mem_request: float | int | None = None,
        mem_limit: float | int | None = None,
        ttl: float = 43200,  # Default TTL in seconds (12 hours)
        memory_limit_multiplier: float | None = None,
    ) -> JobVariables:
        """Set default job variables for the saver deployment type with memory in GiB."""
        if memory_limit_multiplier is None:
            memory_limit_multiplier = self.MEMORY_LIMIT_MULTIPLIER

        mem_request_str = f"{mem_request}Gi" if mem_request is not None else None
        if mem_limit is not None:
            mem_limit_str = f"{mem_limit}Gi"
        elif mem_request is not None and mem_limit is None:
            mem_limit_str = f"{mem_request * memory_limit_multiplier}Gi"
        else:
            raise NotImplementedError(
                "Memory limit is not set and memory_limit_multiplier is not provided."
            )

        return self._get_job_variables(
            deployment_type=deployment_type,
            cpu_request=cpu_request,
            cpu_limit=cpu_limit,
            mem_request=mem_request_str,
            mem_limit=mem_limit_str,
            ttl=ttl,
        )

    @property
    @abstractmethod
    def saver_job_variables(self) -> JobVariables | None:
        """Default job variables for the saver deployment type."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    @property
    @abstractmethod
    def saver_dispatcher_job_variables(self) -> JobVariables | None:
        """Default job variables for the dispatcher deployment type."""
        raise NotImplementedError("This method should be implemented in subclasses.")

    def get_job_variables(self, deployment_type: PrefectDeploymentType) -> JobVariables:
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.saver_job_variables
            case PrefectDeploymentType.DISPATCHER:
                return self.saver_dispatcher_job_variables
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # endregion

    @property
    def saver_concurrency_limit(self) -> int | None:
        """Concurrency limit for the saver deployment."""
        return 2

    @property
    def saver_dispatcher_concurrency_limit(self) -> int | None:
        """Concurrency limit for the saver dispatcher deployment."""
        return 1

    def get_concurrency_limit(self, deployment_type: PrefectDeploymentType) -> int | None:
        """Get the concurrency limit for a specific deployment type."""
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.saver_concurrency_limit
            case PrefectDeploymentType.DISPATCHER:
                return self.saver_dispatcher_concurrency_limit
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # region Sub-Flow Orchestration
    async def dispatch_deployment_saver_dispatcher(
        self,
        parameters: dict[str, Any] | None,
        timeout: float = None,
    ) -> FlowRun:
        """Dispatch a saver dispatcher deployment."""
        dep_run_name = self.saver_dispatcher_deployment_run_name
        logger.info(
            f"Dispatching deployment {dep_run_name} with parameters {list(parameters.keys())}"
        )
        return await run_deployment(
            name=dep_run_name,
            flow_run_name=self.saver_dispatcher_flow_run_name,
            parameters=parameters,
            job_variables=self.saver_dispatcher_job_variables.to_dict(),
            timeout=timeout,
        )

    async def dispatch_deployment_saver(
        self,
        parameters: dict[str, Any] | None,
        timeout: float = None,
    ) -> FlowRun:
        """Dispatch a saver deployment."""
        dep_run_name = self.saver_deployment_run_name
        logger.info(
            f"Dispatching deployment {dep_run_name} with parameters {list(parameters.keys())}"
        )
        return await run_deployment(
            name=dep_run_name,
            flow_run_name=self.saver_flow_run_name,
            parameters=parameters,
            job_variables=self.saver_job_variables.to_dict(),
            timeout=timeout,
        )

    async def dispatch_deployment(
        self,
        dep_type: PrefectDeploymentType,
        parameters: dict[str, Any] | None,
        timeout: float = None,
    ) -> FlowRun:
        """Dispatch a deployment."""
        if dep_type == PrefectDeploymentType.SAVER:
            return await self.dispatch_deployment_saver(parameters=parameters, timeout=timeout)
        elif dep_type == PrefectDeploymentType.DISPATCHER:
            return await self.dispatch_deployment_saver_dispatcher(
                parameters=parameters, timeout=timeout
            )
        else:
            raise NotImplementedError(f"Unknown deployment type: {dep_type}")

    async def dispatch_sub_flows(
        self,
        params: list[dict],
        deployment_type: PrefectDeploymentType = PrefectDeploymentType.SAVER,
    ) -> list[FlowRun]:
        """
        Asynchronously dispatch multiple sub-flows for parallel processing.

        Args:
            params: List of parameter dictionaries for each sub-flow
            deployment_type: Either SAVER or DISPATCHER deployment type

        Returns:
            List of FlowRun results from the dispatched sub-flows
        """
        saver_sub_flows = []
        for i, param in enumerate(params):
            sub_flow = self.dispatch_deployment(dep_type=deployment_type, parameters=param)
            logger.info(f"Started for chunk {i + 1}/{len(params)}")
            saver_sub_flows.append(sub_flow)

        results: list[FlowRun] = await asyncio.gather(*saver_sub_flows)
        return results

    # endregion

    # region Schedule Properties
    @property
    def saver_schedules(self) -> list[Schedule]:
        """Get schedules for the deployment type."""
        return []

    @staticmethod
    def saver_dispatcher_schedules() -> list[Schedule]:
        """Get schedules for the deployment type."""
        return []

    def get_schedules(self, deployment_type: PrefectDeploymentType) -> list[Schedule]:
        # noinspection PyUnreachableCode
        match deployment_type:
            case PrefectDeploymentType.SAVER:
                return self.saver_schedules
            case PrefectDeploymentType.DISPATCHER:
                return self.saver_dispatcher_schedules()
            case _:
                raise NotImplementedError(f"Unknown deployment type: {deployment_type}")

    # endregion
