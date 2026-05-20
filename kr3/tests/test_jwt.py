from tests.conftest import bearer_header, register_user, login_jwt


def test_jwt_login_user_not_found(client):
    response = login_jwt(client, "nobody", "pass")
    assert response.status_code == 404
    assert response.json()["detail"] == "User not found"


def test_jwt_login_wrong_password(client):
    register_user(client, "alice", "qwerty123")
    response = login_jwt(client, "alice", "wrong")
    assert response.status_code == 401
    assert response.json()["detail"] == "Authorization failed"


def test_jwt_login_success(client):
    register_user(client, "alice", "qwerty123")
    response = login_jwt(client, "alice", "qwerty123")
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_protected_without_token(client):
    response = client.get("/protected_resource")
    assert response.status_code == 403


def test_protected_with_token(client):
    register_user(client, "alice", "qwerty123", role="user")
    token = login_jwt(client, "alice", "qwerty123").json()["access_token"]

    response = client.get(
        "/protected_resource",
        headers=bearer_header(token),
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Access granted"


def test_protected_guest_forbidden(client):
    register_user(client, "guest1", "pass", role="guest")
    token = login_jwt(client, "guest1", "pass").json()["access_token"]

    response = client.get(
        "/protected_resource",
        headers=bearer_header(token),
    )
    assert response.status_code == 403
