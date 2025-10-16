# src/my_booking/config.py
# src/my_booking/config.py
import os
from typing import Optional
from pydantic import ConfigDict, computed_field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Обязательные поля (всегда нужны)
    secret_key: str
    jwt_secret_key: str
    jwt_expire_days: int

    # Опциональные поля (нужны только в продакшене)
    db_user: Optional[str] = None
    db_password: Optional[str] = None
    db_host: Optional[str] = None
    db_port: int = 5432
    db_name: Optional[str] = None

    redis_host: Optional[str] = None
    redis_port: int = 6379
    redis_db: int = 0

    debug: bool = False

    @computed_field
    def database_url(self) -> str:
        if os.getenv("CI"):
            return "sqlite+aiosqlite:///:memory:"
        # В продакшене — проверяем, что все поля для PostgreSQL заданы
        if not all([self.db_user, self.db_password, self.db_host, self.db_name]):
            raise ValueError("Missing database configuration for PostgreSQL")
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = ConfigDict(
        env_file=".env" if not os.getenv("CI") else None,
        extra="ignore",
    )


settings = Settings()
