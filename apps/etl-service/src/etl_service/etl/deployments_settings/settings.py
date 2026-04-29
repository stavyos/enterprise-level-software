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
        default="http://host.docker.internal:4200/api",
        validation_alias="PREFECT_API_URL",
    )

    # EODHD Settings
    eodhd_api_key: str = Field(..., validation_alias="EODHD_API_KEY")

    # Database Settings
    db_host: str = Field(default="host.docker.internal", validation_alias="DB_HOST")
    db_port: int = Field(default=5432, validation_alias="DB_PORT")
    db_user: str = Field(..., validation_alias="DB_USER")
    db_password: str = Field(..., validation_alias="DB_PASSWORD")
    db_name: str = Field(..., validation_alias="DB_NAME")

    # App Settings
    job_pythonpath: str = Field(
        default="/app/libs/db-client/src:/app/libs/eodhd-client/src:/app/libs/storage-client/src:/app/apps/etl-service/src",
        validation_alias="JOB_PYTHONPATH",
    )
    env_prefix: str = Field(default="", validation_alias="ENV_PREFIX")
    data_dir: str = Field(default="data", validation_alias="DATA_DIR")
    is_local: bool = Field(default=False, validation_alias="IS_LOCAL")

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    @property
    def effective_db_host(self) -> str:
        """Returns the effective database host."""
        if self.db_host in ("localhost", "127.0.0.1") and not self.is_local:
            return "host.docker.internal"
        return self.db_host

    @property
    def effective_prefect_api_url(self) -> str:
        """Returns the effective Prefect API URL."""
        if (
            "localhost" in self.prefect_api_url or "127.0.0.1" in self.prefect_api_url
        ) and not self.is_local:
            return self.prefect_api_url.replace(
                "localhost", "host.docker.internal"
            ).replace("127.0.0.1", "host.docker.internal")
        return self.prefect_api_url

    def reload(self, env_file: str | None = None) -> None:
        """Reload settings from environment variables."""
        # Priority 1: Explicitly provided env_file
        # Priority 2: Standard env files (dev.env, prod.env, .env) in search dirs

        file_values = {}

        if env_file and os.path.exists(env_file):
            from dotenv import dotenv_values

            file_values.update(dotenv_values(env_file))
        else:
            # Try to find a .env file to force-load (prioritize file over process env)
            env_files = ["dev.env", "prod.env", ".env"]
            # Check parent dirs too since we often run from apps/etl-service
            search_dirs = [".", "..", "../.."]

            for d in search_dirs:
                for f in env_files:
                    path = os.path.abspath(os.path.join(d, f))
                    if os.path.exists(path):
                        from dotenv import dotenv_values

                        loaded = dotenv_values(path)
                        file_values.update(loaded)

        # Manually refresh each field
        for field_name, field in self.model_fields.items():
            env_key = field_name.upper()
            if field.validation_alias and isinstance(field.validation_alias, str):
                env_key = field.validation_alias

            # Priority: 1. Value in .env file, 2. Process environment variable
            f_val = file_values.get(env_key)
            e_val = os.getenv(env_key)
            val = f_val if f_val is not None else e_val

            if val is not None:
                if field.annotation is int:
                    val = int(val)
                elif field.annotation is bool:
                    val = str(val).lower() in ("true", "1")
                setattr(self, field_name, val)

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
