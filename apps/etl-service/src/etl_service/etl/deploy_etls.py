"""Module for deploying Prefect flows for the ETL service."""

import asyncio
import os

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

                # Use the modern flow.deploy() API. This is the recommended way in Prefect 3.x
                # to register deployments to a work pool while ensuring that the code is
                # loaded from the baked-in image rather than being pulled from the host.
                from prefect.flows import load_flow_from_entrypoint

                flow = load_flow_from_entrypoint(entrypoint)

                print(f"Registering flow: {flow_name} -> {dep_name}")
                deployment_id = await flow.deploy(
                    name=dep_name,
                    work_pool_name=dep_settings.work_pool,
                    image=image,
                    tags=tags,
                    job_variables=job_variables,
                    build=False,
                    push=False,
                )

                # CRITICAL: Clear pull_steps and path to force the worker to use the code
                # baked into the image. This prevents FileNotFoundError when registered from CI.
                from prefect.client import get_client
                from prefect.client.schemas.actions import DeploymentUpdate

                async with get_client() as client:
                    await client.update_deployment(
                        deployment_id,
                        deployment=DeploymentUpdate(
                            path=None,
                            pull_steps=[],
                        ),
                    )


if __name__ == "__main__":
    import sys

    from etl_service.etl.deployments_settings.settings import settings

    # Determine env file from environment or defaults
    env_file = None
    # Priority: 1. ENV_PREFIX from process env, 2. "prod" in arguments (excluding script path)
    is_prod = os.environ.get("ENV_PREFIX") == "prod" or any(
        "prod" in arg for arg in sys.argv[1:]
    )

    if is_prod:
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
