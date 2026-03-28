from pydantic import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "NIDUS Core API"
    ENVIRONMENT: str = "development"

    # Strictly typed PostgreSQL URL
    DATABASE_URL: PostgresDsn
    DATABASE_ADMIN_URL: PostgresDsn

    # Pydantic V2 config: reads from .env, ignores extra variables
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", extra="ignore"
    )


# Singleton pattern: instantiate once, import anywhere
settings = Settings()  # type: ignore[call-arg]
