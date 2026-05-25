import os


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "env" in data


def test_health_docker_env(client, monkeypatch):
    monkeypatch.setenv("APP_ENV", "docker")
    response = client.get("/health")
    assert response.json()["env"] == "docker"
