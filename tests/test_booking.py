
import pytest


@pytest.mark.asyncio
async def test_create_booking(client):
    # создаём комнату
    response = await client.post("/rooms/create", 
                                 json={"description": "Room for booking", "price": 150})
    room_id = response.json()["room_id"]

    response = await client.post("/bookings/create", json={
        "room_id": room_id,
        "date_start": "2025-10-14",
        "date_end": "2025-10-16"
    })
    assert response.status_code == 200
    data = response.json()
    assert "booking_id" in data

@pytest.mark.asyncio
async def test_list_bookings(client):
    response = await client.post("/rooms/create", 
                                 json={"description": "Room for list", "price": 120})
    room_id = response.json()["room_id"]
    await client.post("/bookings/create", json={
        "room_id": room_id,
        "date_start": "2025-10-15",
        "date_end": "2025-10-17"
    })

    response = await client.get(f"/bookings/list?room_id={room_id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert "date_start" in data[0]
    assert "date_end" in data[0]

@pytest.mark.asyncio
async def test_delete_booking(client):
    response = await client.post("/rooms/create", 
                                 json={"description": "Room for delete booking", "price": 180})
    room_id = response.json()["room_id"]
    response = await client.post("/bookings/create", json={
        "room_id": room_id,
        "date_start": "2025-10-18",
        "date_end": "2025-10-19"
    })
    booking_id = response.json()["booking_id"]

    response = await client.delete(f"/bookings/delete/{booking_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] == booking_id
