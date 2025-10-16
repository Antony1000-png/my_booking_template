# tests/conftest.py
import os

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, StaticPool

from src.my_booking.db.database import Base
from src.my_booking.dependencies import get_db
from src.my_booking.main import app

# Определяем, в CI мы или нет
IS_CI = os.getenv("CI", "false").lower() == "true"

if IS_CI:
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    TEST_DATABASE_URL = "postgresql+asyncpg://app:app1488@db:5432/hotel_db_test"

@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"

@pytest.fixture(scope="session")
async def test_engine():
    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool if IS_CI else NullPool,
        echo=False,
    )
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()

@pytest.fixture()
async def session(test_engine):
    session_factory = async_sessionmaker(
        test_engine, expire_on_commit=False, class_=AsyncSession
    )
    async with session_factory() as s:
        yield s

@pytest.fixture()
async def client(session):
    async def override_get_db():
        yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()