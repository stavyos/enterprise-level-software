"""Module for deploying Prefect flows for the ETL service."""

import asyncio
import os

from prefect.deployments.runner import RunnerDeployment
from prefect.deployments.runner import deploy as prefect_deploy

from etl_service.etl.deployments_settings.enums import (
    PrefectDeployment,
    PrefectDeploymentType,
)


async def deploy(
    image: str | None = None,
    version_tag: str | None = None,
    env_file: str | None = None,
) -> None:
    """Iterates through all defined Prefect deployments and registers them.

    Args:
        image (str | None, optional): The Docker image to use for all deployments. Defaults to None.
        version_tag (str | None, optional): A version tag for all deployments. Defaults to None.
        env_file (str | None, optional): The environment file to load settings from. Defaults to None.
    """
    # Group deployments by work pool
    pool_deployments = {}

    from etl_service.etl.deployments_settings.settings import settings

    # Reload settings to ensure we pick up environment-specific variables
    # (especially ENV_PREFIX from .env files or process env)
    settings.reload(env_file=env_file)

    with settings.override(env_prefix=settings.env_prefix):
        for prefect_dep in PrefectDeployment:
            # Re-import mapper inside loop to ensure fresh state if possible
            import importlib

            import etl_service.etl.deployments_settings.mapper as mapper_module

            importlib.reload(mapper_module)

            dep_settings = mapper_module.map_deployment_to_settings(
                deployment=prefect_dep
            )

            for dep_type in [
                PrefectDeploymentType.SAVER,
                PrefectDeploymentType.DISPATCHER,
            ]:
                is_available = dep_settings.get_is_available(deployment_type=dep_type)
                if not is_available:
                    continue

                flow_name = dep_settings.get_flow_name(deployment_type=dep_type)
                dep_name = dep_settings.get_deployment_name(deployment_type=dep_type)
                job_variables = dep_settings.get_job_variables(
                    deployment_type=dep_type
                ).to_dict()

                if image:
                    job_variables["image"] = image

                # Ensure PYTHONPATH is set in job variables for Docker
                if "env" not in job_variables:
                    job_variables["env"] = {}
                job_variables["env"]["PYTHONPATH"] = settings.job_pythonpath

                tags = [version_tag] if version_tag else []
                tags += ["etl", dep_settings.deployment.value]
                if settings.env_prefix:
                    tags.append(settings.env_prefix)

                # Get entrypoint
                module_path = dep_settings.flows_module.replace(".py", "")
                ep = dep_settings.get_entry_point(deployment_type=dep_type)
                flow_function_name = ep.split(":")[-1]
                entrypoint = (
                    f"etl_service.etl.flows.etl.{module_path}:{flow_function_name}"
                )

                # Create deployment specification
                d = RunnerDeployment(
                    name=dep_name,
                    flow_name=flow_name,
                    entrypoint=entrypoint,
                    tags=tags,
                    job_variables=job_variables,
                )

                work_pool = dep_settings.work_pool
                if work_pool not in pool_deployments:
                    pool_deployments[work_pool] = []
                pool_deployments[work_pool].append(d)

    # Register each pool's deployments
    for pool_name, deployments in pool_deployments.items():
        print(f"Deploying {len(deployments)} flows to pool: {pool_name}")
        await prefect_deploy(
            *deployments, work_pool_name=pool_name, image=image, build=False, push=False
        )


if __name__ == "__main__":
    import sys

    from etl_service.etl.deployments_settings.settings import settings

    # Determine env file from environment or defaults
    # When running via Nx, we often have --env-file passed to uv run
    # but it doesn't always reflect in sys.argv.
    # We can check the image name or other args.
    env_file = None
    if any("prod" in arg for arg in sys.argv):
        if os.path.exists("../../prod.env"):
            env_file = "../../prod.env"
        elif os.path.exists("prod.env"):
            env_file = "prod.env"
    else:
        if os.path.exists("../../dev.env"):
            env_file = "../../dev.env"
        elif os.path.exists("dev.env"):
            env_file = "dev.env"

    # Reload settings to ensure we pick up environment-specific variables
    # (especially ENV_PREFIX from .env files or process env)
    settings.reload(env_file=env_file)

    default_img = (
        f"etl-service:{settings.env_prefix}"
        if settings.env_prefix
        else "etl-service:dev"
    )
    img = sys.argv[1] if len(sys.argv) > 1 else default_img

    print(f"Deploying using image: {img} and env_file: {env_file}")
    asyncio.run(deploy(image=img, env_file=env_file))
