from pydantic import BaseModel
from typing import Optional


class PlayCard(BaseModel):
    player_id: int
    card_id: int
    color: Optional[str] = ""
