# src/my_booking/api/rooms.py
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from ..db import repository
from ..dependencies import get_db  # ← ИЗМЕНЕНО

# ... остальной код без изменений

router = APIRouter(prefix="/rooms", tags=["rooms"])


class RoomIn(BaseModel):
    description: str
    price: float

@router.post("/create")
async def create_room(room: RoomIn, db: AsyncSession = Depends(get_db)):
    room_id = await repository.add_room(db, room.description, room.price)
    return {"room_id": room_id}

@router.get("/list")
async def list_rooms(
    order_by: str = Query("created_at"),
    asc: bool = Query(True),
    db: AsyncSession = Depends(get_db)
):
    asc_desc = "asc" if asc else "desc"
    try:
        rooms = await repository.get_rooms(db, order_by=order_by, asc_desc=asc_desc)
    except Exception as err:
        raise HTTPException(status_code=400, detail="Invalid order_by field") from err
    return [
        {
            "id": r.id,
            "description": r.description,
            "price": r.price,
            "created_at": r.created_at.isoformat()
        }
        for r in rooms
    ]

@router.delete("/delete/{room_id}")
async def delete_room(room_id: int, db: AsyncSession = Depends(get_db)):
    await repository.delete_room(db, room_id)
    return {"deleted": room_id}