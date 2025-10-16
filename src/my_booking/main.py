# src/my_booking/main.py
# src/my_booking/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

from .api import bookings, rooms
from .config import settings
from .db.database import Base

# Глобальные переменные уровня приложения
app_engine = None
app_session_factory = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global app_engine, app_session_factory
    # Создаём движок без пула (для инициализации)
    init_engine = create_async_engine(settings.database_url, poolclass=NullPool)
    async with init_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await init_engine.dispose()

    # Создаём основной движок для работы приложения
    app_engine = create_async_engine(settings.database_url, echo=True)
    app_session_factory = async_sessionmaker(
        app_engine, expire_on_commit=False, class_=AsyncSession
    )
    yield
    await app_engine.dispose()

app = FastAPI(lifespan=lifespan)

# Зависимость для роутов
async def get_db() -> AsyncSession:
    async with app_session_factory() as session:
        yield session

app.include_router(rooms.router)
app.include_router(bookings.router)

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request: Request, exc: IntegrityError):
    if "foreign key constraint" in str(exc.orig):
        raise HTTPException(status_code=400, detail="Room does not exist")
    raise HTTPException(status_code=400, detail="Database integrity error")