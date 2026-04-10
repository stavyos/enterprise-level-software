# Loguru Logging

## Overview
We use **Loguru** for structured, asynchronous, and easily configurable logging across all our Python applications and Prefect flows.

## Prefect Integration
To ensure Loguru logs are correctly captured and displayed in the Prefect UI, we use a custom decorator located in `etl_service.etl.flows.utils`.

### Usage in Flows
Every Prefect flow should be decorated with `@enable_loguru_support`:

```python
from etl_service.etl.flows.utils import enable_loguru_support
from loguru import logger
from prefect import flow

@flow(name="My Flow")
@enable_loguru_support
def my_flow():
    logger.info("This log will be visible in the Prefect UI")
```

## Standards
- **Format**: `{name}:{function}:{line} - {message}`
- **Levels**: standard Loguru levels (TRACE, DEBUG, INFO, WARNING, ERROR, CRITICAL) are mapped to corresponding Prefect log levels.
