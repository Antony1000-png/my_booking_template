from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, field_validator, ValidationInfo
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from ..dependencies import get_db
from src.my_booking.db import repository

router = APIRouter(prefix="/bookings", tags=["bookings"])

class BookingIn(BaseModel):
    room_id: int
    date_start: date
    date_end: date

    @field_validator("date_end")
    def end_must_be_after_start(cls, v, info: ValidationInfo):
        date_start = info.data.get("date_start")
        if date_start is not None and v < date_start:
            raise ValueError("End date must be after start date")
        return v

@router.post("/create")
async def create_booking(booking: BookingIn, db: AsyncSession = Depends(get_db)):
    async with db:
        booking_id = await repository.add_booking(db, booking.room_id, booking.date_start, booking.date_end)
        return {"booking_id": booking_id}

@router.get("/list")
async def list_bookings(room_id: int = Query(...), db: AsyncSession = Depends(get_db)):
    async with db:
        bookings = await repository.get_bookings(db, room_id)
        return [
            {"booking_id": b.id, "date_start": b.date_start.isoformat(), "date_end": b.date_end.isoformat()}
            for b in bookings
        ]

@router.delete("/delete/{booking_id}")
async def delete_booking(booking_id: int, db: AsyncSession = Depends(get_db)):
    async with db:
        await repository.delete_booking(db, booking_id)
        return {"deleted": booking_id}
