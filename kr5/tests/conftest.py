import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.storage import storage
from app.ws_manager import room_manager


@pytest.fixture(autouse=True)
def clear_state():
    storage.clear()
    room_manager.clear()
    yield
    storage.clear()
    room_manager.clear()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
