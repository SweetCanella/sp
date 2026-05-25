def drain_join_events(ws, expected_users: int):
    """Сбрасываем событие user_joined по одному на каждого пользователя."""
    for _ in range(expected_users):
        ws.receive_json()


def test_connect_with_username(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        msg = ws.receive_json()
        assert msg["type"] == "user_joined"
        assert msg["username"] == "alice"


def test_message_echo(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()
        ws.send_json({"type": "message", "text": "Привет"})
        msg = ws.receive_json()
        assert msg["type"] == "message"
        assert msg["room_id"] == "python"
        assert msg["username"] == "alice"
        assert msg["text"] == "Привет"


def test_two_clients_in_same_room(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()

        with client.websocket_connect("/ws/rooms/python?username=bob") as bob:
            alice.receive_json()
            bob.receive_json()

            bob.send_json({"type": "message", "text": "Всем привет"})

            alice_msg = alice.receive_json()
            bob_msg = bob.receive_json()

            assert alice_msg["text"] == "Всем привет"
            assert bob_msg["text"] == "Всем привет"
            assert alice_msg["username"] == "bob"


def test_users_isolated_between_rooms(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as alice:
        alice.receive_json()

        with client.websocket_connect("/ws/rooms/golang?username=bob") as bob:
            bob.receive_json()

            bob.send_json({"type": "message", "text": "Hi golang"})
            bob_msg = bob.receive_json()
            assert bob_msg["text"] == "Hi golang"

            alice.send_json({"type": "message", "text": "Hi python"})
            alice_msg = alice.receive_json()
            assert alice_msg["text"] == "Hi python"


def test_message_too_long(client):
    with client.websocket_connect("/ws/rooms/python?username=alice") as ws:
        ws.receive_json()
        ws.send_json({"type": "message", "text": "x" * 301})
        msg = ws.receive_json()
        assert msg["type"] == "error"
        assert msg["detail"] == "Message is too long"


def test_user_removed_after_disconnect(client):
    with client.websocket_connect("/ws/rooms/python?username=alice"):
        response = client.get("/rooms/python/users")
        assert "alice" in response.json()["users"]

    response = client.get("/rooms/python/users")
    assert "alice" not in response.json()["users"]


def test_empty_username_closes_connection(client):
    from starlette.websockets import WebSocketDisconnect
    import pytest

    with pytest.raises(WebSocketDisconnect):
        with client.websocket_connect("/ws/rooms/python?username=") as ws:
            ws.receive_json()
