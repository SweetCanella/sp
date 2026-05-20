from tests.conftest import auth_header

import main


def test_docs_without_auth(client):
    response = client.get("/docs")
    assert response.status_code == 401


def test_docs_with_valid_auth(client):
    response = client.get("/docs", headers=auth_header("admin", "secret"))
    assert response.status_code == 200
    assert "swagger" in response.text.lower() or "html" in response.headers.get("content-type", "")


def test_redoc_hidden(client):
    response = client.get("/redoc")
    assert response.status_code == 404


def test_docs_prod_mode(client, monkeypatch):
    monkeypatch.setattr(main, "MODE", "PROD")
    response = client.get("/docs")
    assert response.status_code == 404
