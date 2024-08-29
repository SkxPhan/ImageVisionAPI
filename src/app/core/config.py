import os
from enum import Enum

from pydantic.types import SecretStr
from pydantic_settings import BaseSettings
from starlette.config import Config

current_file_dir = os.path.dirname(os.path.realpath(__file__))
env_path = os.path.join(current_file_dir, "..", "..", "..", ".env")
config = Config(env_path)


class AppSettings(BaseSettings):
    APP_NAME: str = config("APP_NAME", default="FastAPI app")
    APP_SUMMARY: str | None = config("APP_SUMMARY", default=None)
    APP_DESCRIPTION: str | None = config("APP_DESCRIPTION", default=None)
    APP_VERSION: str | None = config("APP_VERSION", default="0.1.0")
    LICENSE_NAME: str | None = config("LICENSE", default=None)
    LICENSE_URL: str | None = config("LICENSE_URL", default=None)
    CONTACT_NAME: str | None = config("CONTACT_NAME", default=None)
    CONTACT_URL: str | None = config("CONTACT_URL", default=None)


class CryptSettings(BaseSettings):
    SECRET_KEY: SecretStr = config("SECRET_KEY")
    ALGORITHM: str = config("ALGORITHM", default="HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = config(
        "ACCESS_TOKEN_EXPIRE_MINUTES", default=30
    )


class CNNSettings:
    MODEL_PATH: str = config(
        "MODEL_PATH",
        default=os.path.join("core", "ml", "mobilenet_v3_large.pth"),
    )
    LABEL_PATH: str = config(
        "LABEL_PATH",
        default=os.path.join("core", "ml", "imagenet_classes.txt"),
    )


class DatabaseSettings(BaseSettings):
    pass


class PostgresSettings(DatabaseSettings):
    POSTGRES_USER: str = config("POSTGRES_USER", default="postgres")
    POSTGRES_PASSWORD: SecretStr = config(
        "POSTGRES_PASSWORD", default="postgres"
    )
    POSTGRES_HOST: str = config("POSTGRES_HOST", default="localhost")
    POSTGRES_PORT: int = config("POSTGRES_PORT", default=5432)
    POSTGRES_DB: str = config("POSTGRES_DB", default="postgres")
    POSTGRES_SYNC_PREFIX: str = config(
        "POSTGRES_SYNC_PREFIX", default="postgresql://"
    )
    POSTGRES_ASYNC_PREFIX: str = config(
        "POSTGRES_ASYNC_PREFIX", default="postgresql+asyncpg://"
    )
    POSTGRES_URI: str = (
        f"{POSTGRES_USER}:{POSTGRES_PASSWORD}"
        f"@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DB}"
    )
    POSTGRES_URL: str | None = config("POSTGRES_URL", default=None)


class EnvironmentOption(Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class EnvironmentSettings(BaseSettings):
    ENVIRONMENT: EnvironmentOption = config("ENVIRONMENT", default="local")


class Settings(
    AppSettings,
    CNNSettings,
    PostgresSettings,
    CryptSettings,
    EnvironmentSettings,
):
    pass


settings = Settings()
