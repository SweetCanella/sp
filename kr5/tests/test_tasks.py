USER_HEADER = {"X-User-Id": "10"}


def make_task(client, headers=USER_HEADER, **kwargs):
    payload = {
        "title": "Подготовить тесты",
        "description": "Описание",
        "status": "todo",
        "priority": 4,
    }
    payload.update(kwargs)
    return client.post("/tasks", json=payload, headers=headers)


def test_create_task(client):
    response = make_task(client)
    assert response.status_code == 201
    data = response.json()
    assert data["title"] == "Подготовить тесты"
    assert data["owner_id"] == 10
    assert "id" in data


def test_create_task_short_title(client):
    response = make_task(client, title="ab")
    assert response.status_code == 422


def test_create_task_without_header(client):
    response = client.post(
        "/tasks",
        json={"title": "Hello world", "priority": 3},
    )
    assert response.status_code == 401


def test_user_sees_only_own_tasks(client):
    make_task(client, headers={"X-User-Id": "10"})
    make_task(client, headers={"X-User-Id": "20"})

    response = client.get("/tasks", headers={"X-User-Id": "10"})
    assert response.status_code == 200
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["owner_id"] == 10


def test_filter_by_status_and_priority(client):
    make_task(client, title="Task one", priority=1, status="todo")
    make_task(client, title="Task two", priority=5, status="done")
    make_task(client, title="Task three", priority=3, status="todo")

    response = client.get("/tasks?status=todo&min_priority=2", headers=USER_HEADER)
    tasks = response.json()
    assert len(tasks) == 1
    assert tasks[0]["title"] == "Task three"


def test_update_status(client):
    created = make_task(client).json()

    response = client.patch(
        f"/tasks/{created['id']}/status",
        json={"status": "done"},
        headers=USER_HEADER,
    )
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_get_someone_else_task(client):
    created = make_task(client, headers={"X-User-Id": "10"}).json()

    response = client.get(f"/tasks/{created['id']}", headers={"X-User-Id": "20"})
    assert response.status_code == 404


def test_get_unknown_task(client):
    response = client.get("/tasks/999", headers=USER_HEADER)
    assert response.status_code == 404


def test_delete_task(client):
    created = make_task(client).json()

    response = client.delete(f"/tasks/{created['id']}", headers=USER_HEADER)
    assert response.status_code == 204

    again = client.get(f"/tasks/{created['id']}", headers=USER_HEADER)
    assert again.status_code == 404
