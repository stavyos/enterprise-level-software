"""Utility functions for Prefect flows."""

from collections.abc import Callable
import datetime
from functools import wraps
import inspect
import os
import time
from typing import Any

from prefect import get_run_logger
from prefect.context import get_run_context
import psutil


def _enable_loguru_support() -> Any:
    """Configures Loguru to redirect all logs to the Prefect run logger.

    Returns:
        Any: The configured loguru logger instance.
    """
    from loguru import logger

    run_logger = get_run_logger()
    logger.remove()
    log_format = "{name}:{function}:{line} - {message}"

    logger.add(
        run_logger.debug,
        filter=lambda record: record["level"].name == "DEBUG",
        level="TRACE",
        format=log_format,
    )

    logger.add(
        run_logger.warning,
        filter=lambda record: record["level"].name == "WARNING",
        level="TRACE",
        format=log_format,
    )

    logger.add(
        run_logger.error,
        filter=lambda record: record["level"].name == "ERROR",
        level="TRACE",
        format=log_format,
    )

    logger.add(
        run_logger.critical,
        filter=lambda record: record["level"].name == "CRITICAL",
        level="TRACE",
        format=log_format,
    )

    logger.add(
        run_logger.info,
        filter=lambda record: (
            record["level"].name not in ["DEBUG", "WARNING", "ERROR", "CRITICAL"]
        ),
        level="TRACE",
        format=log_format,
    )

    return logger


def enable_loguru_support(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator to enable Loguru support within a Prefect flow or task.

    Args:
        func (Callable[..., Any]): The flow or task function to decorate.

    Returns:
        Callable[..., Any]: The wrapped function with Loguru support.
    """

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        _enable_loguru_support()
        return await func(*args, **kwargs)

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        _enable_loguru_support()
        return func(*args, **kwargs)

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper


def _save_resource_metric(
    flow_name: str,
    flow_run_id: str | None,
    peak_memory_mb: float,
    cpu_time_seconds: float,
    wall_time_seconds: float,
) -> None:
    """Persist a resource metric record to the database.

    Args:
        flow_name: Name of the Prefect flow.
        flow_run_id: UUID of the flow run.
        peak_memory_mb: Peak memory usage in megabytes.
        cpu_time_seconds: Total CPU time consumed.
        wall_time_seconds: Total wall clock time.
    """
    try:
        from db_client.client import DBClient
        from db_client.models import FlowResourceMetric
        from etl_service.etl.deployments_settings.settings import settings

        db_client = DBClient(
            dbname=settings.db_name,
            user=settings.db_user,
            password=settings.db_password,
            host=settings.effective_db_host,
            port=settings.db_port,
        )

        metric = FlowResourceMetric(
            flow_name=flow_name,
            flow_run_id=flow_run_id,
            recorded_at=datetime.date.today(),
            peak_memory_mb=round(peak_memory_mb, 2),
            cpu_time_seconds=round(cpu_time_seconds, 2),
            wall_time_seconds=round(wall_time_seconds, 2),
            env_prefix=settings.env_prefix,
        )

        with db_client._session() as session:
            session.add(metric)
            session.commit()
    except Exception as exc:
        # Never let metric persistence crash a flow
        from loguru import logger

        logger.warning(f"Failed to save resource metric: {exc}")


def track_resources(func: Callable[..., Any]) -> Callable[..., Any]:
    """Decorator that tracks CPU and memory usage of a Prefect flow run.

    Captures peak RSS memory, CPU time, and wall time, then logs the results
    and persists them to the flow_resource_metrics database table.

    Args:
        func (Callable[..., Any]): The flow or task function to decorate.

    Returns:
        Callable[..., Any]: The wrapped function with resource tracking.
    """

    @wraps(func)
    async def async_wrapper(*args: Any, **kwargs: Any) -> Any:
        process = psutil.Process(os.getpid())
        start_cpu = process.cpu_times()
        start_wall = time.monotonic()

        result = await func(*args, **kwargs)

        end_cpu = process.cpu_times()
        end_wall = time.monotonic()
        peak_mem_mb = process.memory_info().rss / (1024 * 1024)
        cpu_seconds = (end_cpu.user - start_cpu.user) + (
            end_cpu.system - start_cpu.system
        )
        wall_seconds = end_wall - start_wall

        flow_name = func.__name__
        flow_run_id = None
        try:
            ctx = get_run_context()
            flow_name = ctx.flow_run.flow_name or flow_name
            flow_run_id = str(ctx.flow_run.id)
        except Exception:
            pass

        run_logger = get_run_logger()
        run_logger.info(
            f"📊 Resource Report | Flow: {flow_name} | "
            f"Peak Memory: {peak_mem_mb:.0f}MB | "
            f"CPU Time: {cpu_seconds:.1f}s | "
            f"Wall Time: {wall_seconds:.1f}s"
        )

        _save_resource_metric(
            flow_name=flow_name,
            flow_run_id=flow_run_id,
            peak_memory_mb=peak_mem_mb,
            cpu_time_seconds=cpu_seconds,
            wall_time_seconds=wall_seconds,
        )

        return result

    @wraps(func)
    def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
        process = psutil.Process(os.getpid())
        start_cpu = process.cpu_times()
        start_wall = time.monotonic()

        result = func(*args, **kwargs)

        end_cpu = process.cpu_times()
        end_wall = time.monotonic()
        peak_mem_mb = process.memory_info().rss / (1024 * 1024)
        cpu_seconds = (end_cpu.user - start_cpu.user) + (
            end_cpu.system - start_cpu.system
        )
        wall_seconds = end_wall - start_wall

        flow_name = func.__name__
        flow_run_id = None
        try:
            ctx = get_run_context()
            flow_name = ctx.flow_run.flow_name or flow_name
            flow_run_id = str(ctx.flow_run.id)
        except Exception:
            pass

        run_logger = get_run_logger()
        run_logger.info(
            f"📊 Resource Report | Flow: {flow_name} | "
            f"Peak Memory: {peak_mem_mb:.0f}MB | "
            f"CPU Time: {cpu_seconds:.1f}s | "
            f"Wall Time: {wall_seconds:.1f}s"
        )

        _save_resource_metric(
            flow_name=flow_name,
            flow_run_id=flow_run_id,
            peak_memory_mb=peak_mem_mb,
            cpu_time_seconds=cpu_seconds,
            wall_time_seconds=wall_seconds,
        )

        return result

    return async_wrapper if inspect.iscoroutinefunction(func) else sync_wrapper
