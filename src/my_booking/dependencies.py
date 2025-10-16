# src/my_booking/dependencies.py
# src/my_booking/dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from .config import settings

# Глобальные переменные уровня приложения
app_engine = None
app_session_factory = None

async def init_db():
    global app_engine, app_session_factory
    app_engine = create_async_engine(settings.database_url, echo=True)
    app_session_factory = async_sessionmaker(
        app_engine, expire_on_commit=False, class_=AsyncSession
    )

async def close_db():
    global app_engine
    if app_engine:
        await app_engine.dispose()

async def get_db() -> AsyncSession:
    async with app_session_factory() as session:
        yield session