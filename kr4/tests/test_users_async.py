import pytest
from httpx import ASGITransport, AsyncClient
from faker import Faker

import users_storage as storage
from main import app

fake = Faker()


@pytest.fixture(autouse=True)
async def clear_db():
    storage.clear_users()
    yield
    storage.clear_users()


@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_create_user_async(async_client):
    username = fake.user_name()
    age = fake.random_int(min=19, max=60)

    response = await async_client.post(
        "/users",
        json={"username": username, "age": age},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == username
    assert data["age"] == age


@pytest.mark.asyncio
async def test_get_user_async(async_client):
    username = fake.first_name()
    created = await async_client.post(
        "/users",
        json={"username": username, "age": 25},
    )
    user_id = created.json()["id"]

    response = await async_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json()["username"] == username


@pytest.mark.asyncio
async def test_get_not_found_async(async_client):
    response = await async_client.get("/users/9999")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_user_async(async_client):
    created = await async_client.post(
        "/users",
        json={"username": fake.user_name(), "age": 30},
    )
    user_id = created.json()["id"]

    response = await async_client.delete(f"/users/{user_id}")
    assert response.status_code == 204


@pytest.mark.asyncio
async def test_delete_twice_async(async_client):
    created = await async_client.post(
        "/users",
        json={"username": fake.user_name(), "age": 21},
    )
    user_id = created.json()["id"]

    await async_client.delete(f"/users/{user_id}")
    response = await async_client.delete(f"/users/{user_id}")
    assert response.status_code == 404
