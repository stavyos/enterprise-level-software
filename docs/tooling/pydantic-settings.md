# Pydantic Settings (Environment-Aware Config)

## Overview
This project uses **Pydantic Settings** to manage its configuration. Pydantic's `BaseSettings` class allows us to define our application's configuration in a single, type-safe Python class that automatically loads values from environment variables or `.env` files.

## Why We Use Pydantic Settings
1.  **Type Safety**: Configuration values are automatically converted to their correct types (e.g., `int` for `DB_PORT`).
2.  **Validation**: Pydantic validates the presence and format of each setting, ensuring the application fails fast if a required variable is missing.
3.  **Environment-First**: Values are prioritized from the environment, making the application cloud-ready.
4.  **Automatic Defaults**: We can provide sensible defaults (e.g., `ENV_PREFIX=""`) that can be overridden by environment variables.

## Implementation Details
We define our settings in `apps/etl-service/src/etl_service/etl/deployments_settings/settings.py`.

### Example `Settings` Class
```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=None, env_file_encoding="utf-8", extra="ignore"
    )

    # Prefect Settings
    prefect_api_url: str = Field(
        default="http://host.docker.internal:4200/api", validation_alias="PREFECT_API_URL"
    )

    # Database Settings
    db_host: str = Field(default="host.docker.internal", validation_alias="DB_HOST")
    db_port: int = Field(default=5432, validation_alias="DB_PORT")
<<<<<<< Updated upstream

    # App Settings
    data_dir: str = Field(default="data", validation_alias="DATA_DIR")
    is_local: bool = Field(default=False, validation_alias="IS_LOCAL")
```
=======
    db_user: str = Field(default="", validation_alias="DB_USER")
    db_password: str = Field(default="", validation_alias="DB_PASSWORD")
    db_name: str = Field(default="", validation_alias="DB_NAME")
>>>>>>> Stashed changes

    # App Settings
    job_pythonpath: str = Field(
        default="/app/libs/db-client/src:/app/libs/eodhd-client/src:/app/libs/storage-client/src:/app/apps/etl-service/src",
        validation_alias="JOB_PYTHONPATH",
    )
    env_prefix: str = Field(default="", validation_alias="ENV_PREFIX")
    data_dir: str = Field(default="/data", validation_alias="DATA_DIR")
    is_local: bool = Field(default=False, validation_alias="IS_LOCAL")
```

## Advanced Logic & Parity
To ensure seamless transitions between local development (host) and Dockerized execution (container), we use dynamic properties:

### Host-to-Container Bridging
```python
@property
def effective_db_host(self) -> str:
    """Returns host.docker.internal if db_host is localhost (for Docker)."""
    if self.db_host in ("localhost", "127.0.0.1") and not self.is_local:
        return "host.docker.internal"
    return self.db_host
```

### Hybrid Storage Resolution
The `data_dir` setting defaults to `/data` (container path). During local host execution, it is overridden by `DATA_DIR` in `dev.env` (e.g., `G:/My Drive/...`). The Prefect worker handles mounting this host path to the container's `/data` directory automatically via `JobVariables`.

## Robust Reloading
Because Prefect and Nx often involve nested directory structures and complex environment variable merging, we implemented a custom `reload()` method. This method searches for `.env`, `dev.env`, and `prod.env` in the current and parent directories, ensuring that the correct configuration is always prioritized.

```python
def reload(self, env_file: str | None = None) -> None:
    """Reload settings with multi-directory .env search and priority logic."""
    # 1. Search for .env, dev.env, prod.env in '.', '..', '../..'
    # 2. Prioritize values in .env files over process environment variables.
    # 3. Manually refresh fields to ensure Pydantic validation is bypassed for initial instantiation.
```

## Benefits of This Approach
By combining Pydantic Settings with custom resolution logic, we achieve high environment parity, making our application robust, easy to debug, and perfectly suited for containerized orchestration.
