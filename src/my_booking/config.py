# src/my_booking/config.py
from pydantic_settings import BaseSettings
from pydantic import computed_field, ConfigDict


class Settings(BaseSettings):
    db_user: str
    db_password: str
    db_host: str
    db_port: int
    db_name: str

    redis_host: str
    redis_port: int
    redis_db: int

    debug: bool = False
    secret_key: str
    jwt_secret_key: str
    jwt_expire_days: int

    @computed_field
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.db_user}:{self.db_password}"
            f"@{self.db_host}:{self.db_port}/{self.db_name}"
        )

    model_config = ConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()

