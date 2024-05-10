import json
from fastapi import HTTPException, status, WebSocket
from typing import Dict, List


INVALID_PLAYER_NAME_LENGTH = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The name must be between 3 and 16 characters long.",
)


NOT_CREATOR = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Only the creator can start the match."
)


NOT_ENOUGH_PLAYERS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The minimum amount of players hasn't been reached.",
)


USER_ALREADY_JOINED = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="The user has already joined."
)


class LobbyManager:
    def __init__(self):
        # {player_name:websocket}
        self.active_connections: Dict[str:WebSocket] = {}

    async def connect(self, player_name: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[player_name] = websocket

    def disconnect(self, player_name: str):
        self.active_connections.pop(player_name)

    async def send_personal_message(self, message: dict, player_name: str):
        await self.active_connections[player_name].send_text(json.dumps(message))

    async def broadcast(self, message: dict, player_name_ignore: str | None = None):
        for player_name, websocket in self.active_connections.items():
            if player_name != player_name_ignore:
                await websocket.send_text(json.dumps(message))


# {match_id:LobbyManager}
lobbys: Dict[int, LobbyManager] = {}
