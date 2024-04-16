import json
from fastapi import HTTPException, status, WebSocket
from typing import Dict, List
from database.models.models import Match

INTERNAL_ERROR_CREATING_MATCH = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error creating the match.",
)

INTERNAL_ERROR_UPDATING_MATCH_INFO = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error when updating the match info.",
)

NOT_EXISTENT_MATCH = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The match doesn't exist."
)

INVALID_MATCH_CODE = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The match code must be exactly 3 characters long and contain only lowercase letters and numbers.",
)

INVALID_PLAYER_NAME_LENGTH = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The name must be between 3 and 16 characters long.",
)


NOT_CREATOR = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Only the creator can start the match."
)

MATCH_ALREADY_STARTED = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="The match has already started."
)

NOT_ENOUGH_PLAYERS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The minimum amount of players hasn't been reached.",
)

MATCH_FULL = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game you are trying to join is already full.",
)


USER_ALREADY_JOINED = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="The user has already joined."
)


class LobbyManager:
    def __init__(self):
        # [{player_id:websocket}]
        self.active_connections: List[Dict[int:WebSocket]] = []

    async def connect(self, player_id: int, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append({player_id: websocket})

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: dict, player_id: int):
        ws = [
            connection[player_id]
            for connection in self.active_connections
            if player_id in connection
        ][0]
        await ws.send_text(json.dumps(message))

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            ws = list(connection.values())[0]
            await ws.send_text(json.dumps(message))


lobbys: Dict[int, LobbyManager] = {}
