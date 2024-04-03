from fastapi import HTTPException, status
from pydantic import BaseModel

class NewMatch(BaseModel):
    name: str
    creator_player: str
    password: str | None = None
   