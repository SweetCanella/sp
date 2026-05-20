import pytest
from fastapi.testclient import TestClient

import users_storage as storage
from main import app


@pytest.fixture(autouse=True)
def clear_db():
    storage.clear_users()
    yield
    storage.clear_users()


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client
