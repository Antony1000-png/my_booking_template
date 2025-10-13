
# src/my_booking/db/database.py
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()

def create_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, echo=True)

def create_session_factory(engine: AsyncEngine):
    return sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)