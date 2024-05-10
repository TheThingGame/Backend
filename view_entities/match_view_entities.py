from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
from pydantic import BaseModel, UUID4
from typing import List
from re import match
from database.models.enums import CardColor


class NewMatch(BaseModel):
    match_name: str
    creator_name: str


class JoinMatch(BaseModel):
    player_name: str
    code: UUID4


class Player(BaseModel):
    name: str


class MatchInfo(BaseModel):
    match_id: int
    player_id: int
    name: str
    code: UUID4
    creator: str
    min_players: int
    max_players: int
    started: bool
    players: List[str]


class StartMatch(BaseModel):
    creator_player: str


class PlayCard(BaseModel):
    player_id: int
    card_id: int


class ChangeColor(BaseModel):
    player_id: int
    color: CardColor
