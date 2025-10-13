# tests/test_booking_validation.py
import pytest
from datetime import date

@pytest.mark.asyncio
async def test_end_date_before_start(client):
    # Создаём комнату для теста
    response = await client.post("/rooms/create", json={"description": "Room validation", "price": 100})
    room_id = response.json()["room_id"]

    # Пробуем создать бронь с date_end < date_start
    response = await client.post("/bookings/create", json={
        "room_id": room_id,
        "date_start": "2025-10-20",
        "date_end": "2025-10-19"
    })
    assert response.status_code == 422  # Pydantic возвращает 422 Unprocessable Entity

@pytest.mark.asyncio
async def test_booking_for_nonexistent_room(client):
    # Пытаемся забронировать комнату с несуществующим ID
    response = await client.post("/bookings/create", json={
        "room_id": 9999,
        "date_start": "2025-10-20",
        "date_end": "2025-10-21"
    })
    # После добавления обработчика IntegrityError ожидаем 400
    assert response.status_code == 400
    assert "Room does not exist" in response.json()["detail"]