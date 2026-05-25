from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.ws_manager import room_manager

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/rooms/{room_id}")
async def websocket_room(websocket: WebSocket, room_id: str, username: str = ""):
    if not username or not username.strip():
        await websocket.close(code=1008)
        return

    await room_manager.connect(room_id, username, websocket)

    try:
        await room_manager.broadcast(
            room_id,
            {"type": "user_joined", "room_id": room_id, "username": username},
        )

        while True:
            data = await websocket.receive_json()

            if data.get("type") != "message":
                continue

            text = data.get("text", "")

            if len(text) > 300:
                await websocket.send_json({"type": "error", "detail": "Message is too long"})
                continue

            await room_manager.broadcast(
                room_id,
                {
                    "type": "message",
                    "room_id": room_id,
                    "username": username,
                    "text": text,
                },
            )

    except WebSocketDisconnect:
        room_manager.disconnect(room_id, username, websocket)
        await room_manager.broadcast(
            room_id,
            {"type": "user_left", "room_id": room_id, "username": username},
        )


@router.get("/rooms/{room_id}/users")
def get_room_users(room_id: str):
    return {"room_id": room_id, "users": room_manager.get_users(room_id)}
