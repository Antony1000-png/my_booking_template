# src/my_booking/main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool
import os

from .db.database import Base
from .api import bookings, rooms# убедитесь, что роутеры импортированы

# Определяем URL БД
IS_TEST = os.getenv("TESTING", "false").lower() == "true"
if IS_TEST:
    DATABASE_URL = "sqlite+aiosqlite:///:memory:"
else:
    DATABASE_URL = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://app:app1488@db:5432/hotel_db"
    )

# Создаём engine для lifespan (только для создания таблиц)
engine = create_async_engine(
    DATABASE_URL,
    poolclass=NullPool if not IS_TEST else None,
    echo=False,
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Создаём таблицы при старте
    if not IS_TEST:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Таблицы созданы в PostgreSQL")
    else:
        print("ℹ️  Пропускаем создание таблиц — режим тестирования")
    
    yield  # приложение работает

    # Закрываем соединение при завершении
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# Подключаем роутеры
app.include_router(rooms.router)
app.include_router(bookings.router)