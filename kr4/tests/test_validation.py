def test_valid_user(client):
    response = client.post(
        "/validate-user",
        json={
            "username": "anna",
            "age": 20,
            "email": "anna@mail.ru",
            "password": "12345678",
        },
    )
    assert response.status_code == 200


def test_invalid_age(client):
    response = client.post(
        "/validate-user",
        json={
            "username": "anna",
            "age": 15,
            "email": "anna@mail.ru",
            "password": "12345678",
        },
    )
    assert response.status_code == 422
    assert response.json()["error_code"] == "VALIDATION_ERROR"


def test_invalid_password(client):
    response = client.post(
        "/validate-user",
        json={
            "username": "anna",
            "age": 20,
            "email": "anna@mail.ru",
            "password": "123",
        },
    )
    assert response.status_code == 422
