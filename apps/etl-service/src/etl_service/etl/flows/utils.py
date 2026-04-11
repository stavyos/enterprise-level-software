"""Utility functions for Prefect flows."""

from collections.abc import Callable
from functools import wraps
import inspect
from typing import Any

from prefect import get_run_logger


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
        filter=lambda record: record["level"].name
        not in ["DEBUG", "WARNING", "ERROR", "CRITICAL"],
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
