import database
from tests.conftest import register_user


def test_register_saves_user_to_sqlite(client):
    register_user(client, "test_user", "12345")

    conn = database.get_db_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT username, password FROM users WHERE username = ?",
        ("test_user",),
    )
    row = cursor.fetchone()
    conn.close()

    assert row is not None
    assert row["username"] == "test_user"
    assert row["password"] == "12345"


def test_todo_crud(client):
    create = client.post(
        "/todos",
        json={"title": "Buy groceries", "description": "Milk, eggs, bread"},
    )
    assert create.status_code == 201
    assert create.json()["completed"] is False
    todo_id = create.json()["id"]

    read = client.get(f"/todos/{todo_id}")
    assert read.status_code == 200
    assert read.json()["title"] == "Buy groceries"

    update = client.put(
        f"/todos/{todo_id}",
        json={
            "title": "Buy groceries",
            "description": "Milk",
            "completed": True,
        },
    )
    assert update.status_code == 200
    assert update.json()["completed"] is True

    delete = client.delete(f"/todos/{todo_id}")
    assert delete.status_code == 200

    not_found = client.get(f"/todos/{todo_id}")
    assert not_found.status_code == 404


def test_get_todo_not_found(client):
    response = client.get("/todos/999")
    assert response.status_code == 404
