def test_exception_a(client):
    response = client.get("/check-condition?fail=true")
    assert response.status_code == 400
    data = response.json()
    assert data["error_code"] == "ERR_A"


def test_exception_b(client):
    response = client.get("/resource/0")
    assert response.status_code == 404
    assert response.json()["error_code"] == "ERR_B"


def test_ok(client):
    response = client.get("/check-condition")
    assert response.status_code == 200
