# src/my_booking/dependencies.py
from sqlalchemy.ext.asyncio import AsyncSession

from .config import settings
from .db.database import create_engine, create_session_factory

# Глобальные переменные уровня приложения
app_engine = None
app_session_factory = None

async def init_db():
    global app_engine, app_session_factory
    app_engine = create_engine(settings.database_url)
    app_session_factory = create_session_factory(app_engine)

async def close_db():
    global app_engine
    if app_engine:
        await app_engine.dispose()

async def get_db() -> AsyncSession:
    async with app_session_factory() as session:
        yield session