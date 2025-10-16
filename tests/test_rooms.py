import pytest


@pytest.mark.asyncio
async def test_create_room(client):
    response = await client.post("/rooms/create", json={
        "description": "Test Room",
        "price": 100
    })
    assert response.status_code == 200
    data = response.json()
    assert "room_id" in data

@pytest.mark.asyncio
async def test_list_rooms(client):
    await client.post("/rooms/create", json={
        "description": "Room 2",
        "price": 200
    })
    response = await client.get("/rooms/list")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert "description" in data[0]
    assert "price" in data[0]

@pytest.mark.asyncio
async def test_delete_room(client):
    response = await client.post("/rooms/create", json={
        "description": "Room to delete",
        "price": 300
    })
    room_id = response.json()["room_id"]

    response = await client.delete(f"/rooms/delete/{room_id}")
    assert response.status_code == 200
    assert response.json()["deleted"] == room_id

