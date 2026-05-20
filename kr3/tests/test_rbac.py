from tests.conftest import bearer_header, register_user, login_jwt


def get_token(client, username, password):
    return login_jwt(client, username, password).json()["access_token"]


def test_admin_can_create_item(client):
    register_user(client, "boss", "pass", role="admin")
    token = get_token(client, "boss", "pass")

    response = client.post(
        "/admin/items?title=Test&description=Desc",
        headers=bearer_header(token),
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Item created"


def test_user_cannot_create_item(client):
    register_user(client, "worker", "pass", role="user")
    token = get_token(client, "worker", "pass")

    response = client.post(
        "/admin/items?title=Test&description=Desc",
        headers=bearer_header(token),
    )
    assert response.status_code == 403


def test_guest_can_read_but_not_update(client):
    register_user(client, "admin1", "pass", role="admin")
    admin_token = get_token(client, "admin1", "pass")
    client.post(
        "/admin/items?title=Book&description=Read me",
        headers=bearer_header(admin_token),
    )

    register_user(client, "visitor", "pass", role="guest")
    guest_token = get_token(client, "visitor", "pass")

    read_response = client.get("/items/1", headers=bearer_header(guest_token))
    assert read_response.status_code == 200

    update_response = client.put(
        "/items/1?title=New&description=Text",
        headers=bearer_header(guest_token),
    )
    assert update_response.status_code == 403


def test_admin_can_delete_item(client):
    register_user(client, "admin1", "pass", role="admin")
    token = get_token(client, "admin1", "pass")

    client.post(
        "/admin/items?title=Temp&description=Delete me",
        headers=bearer_header(token),
    )

    response = client.delete("/items/1", headers=bearer_header(token))
    assert response.status_code == 200
    assert response.json()["message"] == "Item deleted"
