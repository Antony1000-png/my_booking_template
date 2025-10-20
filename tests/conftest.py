import os

import asyncpg
import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool, StaticPool

from src.my_booking.db.database import Base
from src.my_booking.dependencies import get_db
from src.my_booking.main import app

# Определяем, запущено ли в CI
IS_CI = os.getenv("CI", "false").lower() == "true"

if IS_CI:
    TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"
    TEST_DB_NAME = None
    CREATE_DB_PARAMS = None
else:
    DB_USER = os.getenv("DB_USER", "app")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "app1488")
    DB_HOST = os.getenv("DB_HOST", "db")
    DB_PORT = os.getenv("DB_PORT", "5432")
    TEST_DB_NAME = os.getenv("TEST_DB_NAME", "hotel_db_test")

    TEST_DATABASE_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{TEST_DB_NAME}"
    CREATE_DB_PARAMS = {
        "user": DB_USER,
        "password": DB_PASSWORD,
        "host": DB_HOST,
        "port": int(DB_PORT),
        "database": "postgres",
    }

# ... остальной код без изменений (вспомогательные функции и фикстуры)
# --- Вспомогательные функции для управления тестовой БД ---
async def _create_database_if_not_exists():
    if IS_CI or not CREATE_DB_PARAMS:
        return

    conn = await asyncpg.connect(**CREATE_DB_PARAMS)
    try:
        exists = await conn.fetchval(
            "SELECT 1 FROM pg_database WHERE datname = $1", TEST_DB_NAME
        )
        if not exists:
            await conn.execute(f'CREATE DATABASE "{TEST_DB_NAME}";')
    finally:
        await conn.close()


async def _drop_database():
    if IS_CI or not CREATE_DB_PARAMS:
        return

    conn = await asyncpg.connect(**CREATE_DB_PARAMS)
    try:
        await conn.execute("""
            SELECT pg_terminate_backend(pid)
            FROM pg_stat_activity
            WHERE datname = $1 AND pid <> pg_backend_pid();
        """, TEST_DB_NAME)
        await conn.execute(f'DROP DATABASE IF EXISTS "{TEST_DB_NAME}";')
    finally:
        await conn.close()


# --- Фикстуры pytest ---
@pytest.fixture(scope="session")
def anyio_backend():
    return "asyncio"


@pytest.fixture(scope="session")
async def test_engine():
    await _create_database_if_not_exists()

    engine = create_async_engine(
        TEST_DATABASE_URL,
        poolclass=StaticPool if IS_CI else NullPool,
        echo=False,
    )

    # Включаем внешние ключи для SQLite в CI
    if IS_CI:
        @event.listens_for(engine.sync_engine, "connect")
        def set_sqlite_pragma(dbapi_connection, connection_record):
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    # Создаём таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield engine

    # Очистка
    await engine.dispose()
    await _drop_database()


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