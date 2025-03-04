import json
from datetime import datetime

from fastapi import WebSocket

from app.models.schemas import UserSession


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict = {}
        self.user_sessions: dict = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket
        self.user_sessions[user_id] = UserSession(user_id)

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]
        if user_id in self.user_sessions:
            del self.user_sessions[user_id]

    async def send_message(self, message: str, user_id: str):
        if user_id in self.active_connections:
            await self.active_connections[user_id].send_text(
                json.dumps(
                    {
                        "message": message,
                        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "is_bot": True,
                    }
                )
            )
