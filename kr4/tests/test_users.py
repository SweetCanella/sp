def test_create_user(client):
    response = client.post("/users", json={"username": "test", "age": 25})
    assert response.status_code == 201
    data = response.json()
    assert data["username"] == "test"
    assert data["age"] == 25
    assert "id" in data


def test_get_user(client):
    created = client.post("/users", json={"username": "bob", "age": 30}).json()
    response = client.get(f"/users/{created['id']}")
    assert response.status_code == 200
    assert response.json()["username"] == "bob"


def test_get_user_not_found(client):
    response = client.get("/users/999")
    assert response.status_code == 404


def test_delete_user(client):
    created = client.post("/users", json={"username": "del", "age": 22}).json()
    response = client.delete(f"/users/{created['id']}")
    assert response.status_code == 204


def test_delete_twice(client):
    created = client.post("/users", json={"username": "del", "age": 22}).json()
    client.delete(f"/users/{created['id']}")
    response = client.delete(f"/users/{created['id']}")
    assert response.status_code == 404
