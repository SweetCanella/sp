from tests.conftest import auth_header, register_user


def test_login_without_credentials(client):
    response = client.get("/login")
    assert response.status_code == 401
    assert response.headers.get("www-authenticate") == "Basic"


def test_login_wrong_password(client):
    register_user(client, "user1", "correctpass")
    response = client.get(
        "/login",
        headers=auth_header("user1", "wrongpass"),
    )
    assert response.status_code == 401


def test_login_success(client):
    register_user(client, "user1", "correctpass")
    response = client.get(
        "/login",
        headers=auth_header("user1", "correctpass"),
    )
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, user1!"}


def test_register_creates_user(client):
    response = register_user(client, "alice", "pass123")
    assert response.status_code == 201
    assert response.json() == {"message": "New user created"}


def test_register_duplicate(client):
    register_user(client, "alice", "pass123")
    response = register_user(client, "alice", "other")
    assert response.status_code == 409
    assert response.json()["detail"] == "User already exists"
