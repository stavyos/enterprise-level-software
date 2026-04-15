"""Module for managing application settings using Pydantic BaseSettings."""

from contextlib import contextmanager
import os

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class."""

    model_config = SettingsConfigDict(
        env_file=None, env_file_encoding="utf-8", extra="ignore"
    )

    # Prefect Settings
    prefect_api_url: str = Field(
        default="http://host.docker.internal:4200/api", env="PREFECT_API_URL"
    )

    # EODHD Settings
    eodhd_api_key: str = Field(..., env="EODHD_API_KEY")

    # Database Settings
    db_host: str = Field(default="host.docker.internal", env="DB_HOST")
    db_port: int = Field(default=5432, env="DB_PORT")
    db_user: str = Field(..., env="DB_USER")
    db_password: str = Field(..., env="DB_PASSWORD")
    db_name: str = Field(..., env="DB_NAME")

    # App Settings
    job_pythonpath: str = Field(
        default="/app/libs/db-client/src:/app/libs/eodhd-client/src:/app/apps/etl-service/src",
        env="JOB_PYTHONPATH",
    )
    env_prefix: str = Field(default="", env="ENV_PREFIX")
    is_local: bool = Field(default=False, env="IS_LOCAL")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Only force is_local if we are in a Prefect Runner process
        # (NOT during deployment or general app use unless IS_LOCAL is env-set)
        if os.getenv("PREFECT_RUNNER") == "true" or os.getenv("PREFECT__FLOW_RUN_ID"):
            self.is_local = True

    @property
    def effective_db_host(self) -> str:
        """Returns the effective database host."""
        if self.db_host == "localhost" and not self.is_local:
            return "host.docker.internal"
        return self.db_host

    def reload(self) -> None:
        """Reload settings from environment variables."""
        # Manually refresh each field from environment
        for field_name, field in self.model_fields.items():
            # Get env key from validation_alias or similar if present,
            # but we use simple Field(env=...) which might not be directly in model_fields easily
            # We'll use a mapping or just uppercase
            env_key = field_name.upper()
            if field_name == "prefect_api_url":
                env_key = "PREFECT_API_URL"
            if field_name == "eodhd_api_key":
                env_key = "EODHD_API_KEY"

            val = os.getenv(env_key)
            if val is not None:
                if field.annotation == int:
                    val = int(val)
                elif field.annotation == bool:
                    val = val.lower() in ("true", "1")
                setattr(self, field_name, val)

        # Re-run init logic for is_local
        if os.getenv("PREFECT_RUNNER") == "true" or os.getenv("PREFECT__FLOW_RUN_ID"):
            self.is_local = True

    @contextmanager
    def override(self, **kwargs):
        """Context manager to temporarily override settings."""
        old_values = {k: getattr(self, k) for k in kwargs}
        for k, v in kwargs.items():
            setattr(self, k, v)
        try:
            yield self
        finally:
            for k, v in old_values.items():
                setattr(self, k, v)


# Global settings instance
settings = Settings()
