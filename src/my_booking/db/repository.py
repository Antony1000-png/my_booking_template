from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, asc, desc
from . import models

async def add_room(db: AsyncSession, description: str, price: float) -> int:
    room = models.Room(description=description, price=price)
    db.add(room)
    await db.commit()
    await db.refresh(room)
    return room.id

async def get_rooms(db: AsyncSession, order_by: str = "created_at", asc_desc: str = "asc"):
    q = select(models.Room)
    order_col = getattr(models.Room, order_by, models.Room.created_at)
    q = q.order_by(asc(order_col) if asc_desc == "asc" else desc(order_col))
    result = await db.execute(q)
    return result.scalars().all()

async def delete_room(db: AsyncSession, room_id: int):
    await db.execute(delete(models.Booking).where(models.Booking.room_id == room_id))
    await db.execute(delete(models.Room).where(models.Room.id == room_id))
    await db.commit()

async def add_booking(db: AsyncSession, room_id: int, date_start, date_end) -> int:
    booking = models.Booking(room_id=room_id, date_start=date_start, date_end=date_end)
    db.add(booking)
    await db.commit()
    await db.refresh(booking)
    return booking.id

async def get_bookings(db: AsyncSession, room_id: int):
    q = select(models.Booking).where(models.Booking.room_id == room_id).order_by(models.Booking.date_start)
    result = await db.execute(q)
    return result.scalars().all()

async def delete_booking(db: AsyncSession, booking_id: int):
    await db.execute(delete(models.Booking).where(models.Booking.id == booking_id))
    await db.commit()
