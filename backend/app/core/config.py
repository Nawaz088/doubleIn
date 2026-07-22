import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "DoubleHQ Clone"
    APP_ENV: str = "development"
    DEBUG: bool = os.getenv("APP_ENV", "development") == "development"

    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/doublehq"
    DATABASE_URL_SYNC: str = "postgresql://postgres:postgres@localhost:5432/doublehq"

    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me-in-production-this-should-be-very-long-and-random"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 30
    ALGORITHM: str = "HS256"

    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173"

    S3_ENDPOINT: str = "http://localhost:9000"
    S3_ACCESS_KEY: str = "minioadmin"
    S3_SECRET_KEY: str = "minioadmin"
    S3_BUCKET_NAME: str = "doublehq-files"
    S3_REGION: str = "us-east-1"

    QBO_CLIENT_ID: Optional[str] = None
    QBO_CLIENT_SECRET: Optional[str] = None
    XERO_CLIENT_ID: Optional[str] = None
    XERO_CLIENT_SECRET: Optional[str] = None

    SENDGRID_API_KEY: Optional[str] = None
    MAGIC_LINK_BASE_URL: str = "http://localhost:5173"

    PASSWORD_HASH_ROUNDS: int = 12

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


settings = Settings()
