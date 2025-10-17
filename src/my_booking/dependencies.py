# src/my_booking/dependencies.py
import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

IS_TEST = os.getenv("TESTING", "false").lower() == "true"
if IS_TEST:
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://app:app1488@db:5432/hotel_db"
    )

# Создаём engine и sessionmaker один раз при импорте
engine = create_async_engine(DATABASE_URL, echo=False)
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

async def close_db():
    await engine.dispose()