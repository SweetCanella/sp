from fastapi import WebSocket


class RoomManager:
    """Управление WebSocket-комнатами."""

    def __init__(self):
        # room_id -> {username: [websocket, ...]}
        self.rooms: dict[str, dict[str, list[WebSocket]]] = {}

    async def connect(self, room_id: str, username: str, websocket: WebSocket):
        await websocket.accept()
        room = self.rooms.setdefault(room_id, {})
        room.setdefault(username, []).append(websocket)

    def disconnect(self, room_id: str, username: str, websocket: WebSocket):
        room = self.rooms.get(room_id)
        if not room:
            return

        sockets = room.get(username, [])
        if websocket in sockets:
            sockets.remove(websocket)

        if not sockets:
            room.pop(username, None)

        if not room:
            self.rooms.pop(room_id, None)

    async def broadcast(self, room_id: str, payload: dict):
        room = self.rooms.get(room_id, {})
        for sockets in list(room.values()):
            for ws in list(sockets):
                try:
                    await ws.send_json(payload)
                except Exception:
                    pass

    def get_users(self, room_id: str) -> list[str]:
        return list(self.rooms.get(room_id, {}).keys())

    def clear(self):
        self.rooms.clear()


room_manager = RoomManager()
