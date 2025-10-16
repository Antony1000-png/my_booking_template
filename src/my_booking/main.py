# src/my_booking/main.py
# src/my_booking/main.py
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from sqlalchemy.exc import IntegrityError

from .api import bookings, rooms
from .dependencies import close_db, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield
    await close_db()

app = FastAPI(lifespan=lifespan)
app.include_router(rooms.router)
app.include_router(bookings.router)

@app.exception_handler(IntegrityError)
async def integrity_error_handler(request, exc):
    # Проверяем, что это именно ошибка внешнего ключа
    if "foreign key constraint" in str(exc.orig):
        raise HTTPException(
            status_code=400,
            detail="Room does not exist"
        )
    # Другие IntegrityError можно обработать отдельно
    raise HTTPException(
        status_code=400,
        detail="Database integrity error"
    )