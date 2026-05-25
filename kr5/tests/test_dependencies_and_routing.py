def make_task(client, headers, **kwargs):
    payload = {
        "title": "Some task",
        "description": "x",
        "status": "todo",
        "priority": 3,
    }
    payload.update(kwargs)
    return client.post("/tasks", json=payload, headers=headers)


def test_users_me(client):
    response = client.get("/users/me", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    assert response.json() == {"id": 10, "role": "user"}


def test_users_me_no_header(client):
    response = client.get("/users/me")
    assert response.status_code == 401


def test_user_cannot_access_admin_stats(client):
    response = client.get("/admin/stats", headers={"X-User-Id": "10", "X-User-Role": "user"})
    assert response.status_code == 403


def test_admin_can_get_stats(client):
    make_task(client, headers={"X-User-Id": "10"}, status="todo")
    make_task(client, headers={"X-User-Id": "10"}, status="in_progress")
    make_task(client, headers={"X-User-Id": "20"}, status="done")
    make_task(client, headers={"X-User-Id": "20"}, status="done")

    response = client.get(
        "/admin/stats",
        headers={"X-User-Id": "1", "X-User-Role": "admin"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["total_tasks"] == 4
    assert data["by_status"] == {"todo": 1, "in_progress": 1, "done": 2}


def test_user_cannot_delete_someones_task(client):
    created = make_task(client, headers={"X-User-Id": "10"}).json()

    response = client.delete(
        f"/tasks/{created['id']}",
        headers={"X-User-Id": "20"},
    )
    assert response.status_code == 404


def test_admin_can_delete_any_task(client):
    created = make_task(client, headers={"X-User-Id": "10"}).json()

    response = client.delete(
        f"/admin/tasks/{created['id']}",
        headers={"X-User-Id": "1", "X-User-Role": "admin"},
    )
    assert response.status_code == 204


def test_openapi_groups_routes_by_tags(client):
    schema = client.get("/openapi.json").json()
    tags_used = set()
    for path in schema["paths"].values():
        for method in path.values():
            for tag in method.get("tags", []):
                tags_used.add(tag)
    assert {"tasks", "users", "admin"}.issubset(tags_used)
