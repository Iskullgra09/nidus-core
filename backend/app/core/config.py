from pathlib import Path

from pydantic import (
    computed_field,
)
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).resolve().parent.parent.parent.parent
ENV_PATH = ROOT_DIR / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), env_ignore_empty=True, extra="ignore")

    PROJECT_NAME: str = "NIDUS Core API"
    ENVIRONMENT: str = "development"
    API_V1_STR: str = "/api/v1"

    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7

    POSTGRES_SERVER: str = "localhost"
    POSTGRES_PORT: int = 5444
    POSTGRES_DB: str = "nidus_core"
    POSTGRES_TEST_DB: str = "nidus_test"

    APP_USER: str
    APP_PASSWORD: str

    ADMIN_USER: str
    ADMIN_PASSWORD: str

    @computed_field
    @property
    def DATABASE_URL(self) -> str:
        """Assembles the restricted app user URL."""
        return f"postgresql+asyncpg://{self.APP_USER}:{self.APP_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    @computed_field
    @property
    def DATABASE_ADMIN_URL(self) -> str:
        """Assembles the superuser URL for migrations."""
        return (
            f"postgresql+asyncpg://{self.ADMIN_USER}:{self.ADMIN_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )

    @computed_field
    @property
    def TEST_DATABASE_URL(self) -> str:
        """Assembles the URL for the test database."""
        return f"postgresql+asyncpg://{self.ADMIN_USER}:{self.ADMIN_PASSWORD}@{self.POSTGRES_SERVER}:{self.POSTGRES_PORT}/{self.POSTGRES_TEST_DB}"


settings = Settings()  # type: ignore
