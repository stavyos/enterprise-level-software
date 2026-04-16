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
```

### Key Features (Pydantic V2)
- **`validation_alias`**: Replaces the old `env` parameter to map environment variables to class attributes.
- **`extra="ignore"`**: Prevents Pydantic from failing if the environment contains variables it doesn't recognize.

## Advanced Logic & Parity
To ensure seamless transitions between local development (host) and Dockerized execution (container), we use dynamic properties:

```python
@property
def effective_db_host(self) -> str:
    """Returns host.docker.internal if db_host is localhost (for Docker)."""
    if self.db_host in ("localhost", "127.0.0.1") and not self.is_local:
        return "host.docker.internal"
    return self.db_host

@property
def effective_prefect_api_url(self) -> str:
    """Returns the effective Prefect API URL."""
    if ("localhost" in self.prefect_api_url or "127.0.0.1" in self.prefect_api_url) and not self.is_local:
        return self.prefect_api_url.replace("localhost", "host.docker.internal").replace("127.0.0.1", "host.docker.internal")
    return self.prefect_api_url
```

## Robust Reloading
Because Prefect and Nx often involve nested directory structures and complex environment variable merging, we implemented a custom `reload()` method. This method searches for `.env`, `dev.env`, and `prod.env` in the current and parent directories, ensuring that the correct configuration is always prioritized during deployment and runtime.

```python
def reload(self) -> None:
    """Reload settings with multi-directory .env search and priority logic."""
    # ... search and load logic ...
```

## Benefits of This Approach
By combining Pydantic Settings with custom resolution logic, we achieve high environment parity, making our application robust, easy to debug, and perfectly suited for containerized orchestration.
