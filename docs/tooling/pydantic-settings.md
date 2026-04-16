# Pydantic Settings (Environment-Aware Config)

## Overview
This project uses **Pydantic Settings** to manage its configuration. Pydantic's `BaseSettings` class allows us to define our application's configuration in a single, type-safe Python class that automatically loads values from environment variables or `.env` files.

## Why We Use Pydantic Settings
1.  **Type Safety**: Configuration values are automatically converted to their correct types (e.g., `int` for `DB_PORT`).
2.  **Validation**: Pydantic validates the presence and format of each setting, ensuring the application fails fast if a required variable is missing.
3.  **Environment-First**: Values are prioritized from the environment, making the application cloud-ready.
4.  **Automatic Defaults**: We can provide sensible defaults (e.g., `ENV_PREFIX=""`) that can be overridden by environment variables.

## Implementation Details
We define our settings in `etl_service/etl/deployments_settings/settings.py`.

### Example `Settings` Class
```python
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )

    # Prefect Settings
    prefect_api_url: str = Field(
        default="http://host.docker.internal:4200/api", env="PREFECT_API_URL"
    )

    # EODHD Settings
    eodhd_api_key: str = Field(..., env="EODHD_API_KEY")

    # App Settings
    env_prefix: str = Field(default="", env="ENV_PREFIX")
```

### Key Features
- **`env_file`**: Instructs Pydantic to look for a `.env` file for local development.
- **`Field(..., env="...")`**: Specifies the environment variable name to map to the class attribute.
- **`extra="ignore"`**: Prevents Pydantic from failing if the `.env` file contains variables it doesn't recognize.

## Advanced Logic
We can add properties to the `Settings` class to handle complex configuration logic:

```python
@property
def effective_db_host(self) -> str:
    """Returns host.docker.internal if db_host is localhost (for K8s)."""
    if self.db_host == "localhost":
        return "host.docker.internal"
    return self.db_host
```

## Benefits of This Approach
By using Pydantic Settings, we ensure that our application's configuration is robust, easy to manage, and perfectly suited for a multi-environment architecture.
