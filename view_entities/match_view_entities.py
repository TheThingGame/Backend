from fastapi import HTTPException, status
from pydantic import BaseModel, field_validator
from pydantic_core import PydanticCustomError
from pydantic import BaseModel, ValidationError, field_validator
from typing import List
from re import match


class NewMatch(BaseModel):
    name: str
    creator_player: str


class JoinMatch(BaseModel):
    player_name: str
    code: str


class MatchID(BaseModel):
    match_id: int


class Player(BaseModel):
    name: str


class MatchInfo(BaseModel):
    match_id: int
    player_id: int
    name: str
    code: str
    creator_player: str
    min_players: int
    max_players: int
    started: bool
    players: List[str]


class StartMatch(BaseModel):
    creator_player: str
