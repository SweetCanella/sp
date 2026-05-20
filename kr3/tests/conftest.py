import os
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# настройки до импорта приложения
os.environ["MODE"] = "DEV"
os.environ["DOCS_USER"] = "admin"
os.environ["DOCS_PASSWORD"] = "secret"
os.environ["JWT_SECRET"] = "test-secret-key"

import slowapi

# отключаем rate limit в тестах
def _no_rate_limit(self, *args, **kwargs):
    def decorator(func):
        return func
    return decorator


slowapi.Limiter.limit = _no_rate_limit

import database
from security import get_password_hash
from main import app


@pytest.fixture(autouse=True)
def reset_state(tmp_path, monkeypatch):
    """Чистая база и память перед каждым тестом."""
    db_file = tmp_path / "test.db"
    monkeypatch.setattr(database, "DB_PATH", db_file)

    database.fake_users_db.clear()
    database.demo_items.clear()
    database.next_item_id = 1

    database.fake_users_db["admin"] = {
        "hashed_password": get_password_hash("secret"),
        "role": "admin",
    }

    database.create_tables()
    yield


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def auth_header(username: str, password: str) -> dict:
    import base64
    token = base64.b64encode(f"{username}:{password}".encode()).decode()
    return {"Authorization": f"Basic {token}"}


def bearer_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def register_user(client, username: str, password: str, role: str = "user"):
    return client.post(
        "/register",
        json={"username": username, "password": password, "role": role},
    )


def login_jwt(client, username: str, password: str):
    response = client.post(
        "/login",
        json={"username": username, "password": password},
    )
    return response
