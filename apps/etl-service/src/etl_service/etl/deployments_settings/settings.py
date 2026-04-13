"""Module for managing application settings using Pydantic BaseSettings."""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings class."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
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

    @property
    def effective_db_host(self) -> str:
        """Returns the effective database host.
        Always returns host.docker.internal if db_host is localhost,
        as this settings class is primarily used by Kubernetes pods.
        """
        if self.db_host == "localhost":
            return "host.docker.internal"
        return self.db_host


# Global settings instance
settings = Settings()
