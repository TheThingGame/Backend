import re
from pony.orm import db_session, ObjectNotFound
from fastapi import HTTPException, status, WebSocket, Body
from view_entities.match_view_entities import NewMatch, JoinMatch, MatchID
from database.dao.match_dao import (
    get_match_by_code,
    get_match_by_id,
    get_player_turn,
)
from database.models.models import Match, Player

from utils.player_utils import NOT_EXISTENT_PLAYER, NOT_YOUR_TURN, NOT_A_PLAY_WAS_MADE
from exceptions import match_exceptions
from . import player_validators
from typing import Annotated


def match_name_validator(match_name: str):
    if len(match_name) < 3 or len(match_name) > 16:
        raise match_exceptions.INVALID_MATCH_LENGTH


def new_match_validator(match: NewMatch):
    match_name_validator(match.match_name)
    player_validators.player_name_validator(match.creator_name)


@db_session
def join_match_validator(join: JoinMatch):
    # Chequeamos si el nombre es correcto
    player_validators.player_name_validator(join.player_name)


@db_session
def match_exists_validator(match_id: int):
    try:
        Match[match_id]
    except ObjectNotFound:
        raise match_exceptions.NOT_EXISTENT_MATCH


@db_session
def match_started_validator(match_id: int):
    match = Match[match_id]
    if match.started:
        raise match_exceptions.MATCH_ALREADY_STARTED


@db_session
def start_match_validator(player_id: Annotated[int, Body(embed=True)], match_id: int):
    # Comprobar si la partida existe
    match_exists_validator(match_id)

    # Comprobar si la partida está iniciada
    match_started_validator(match_id)

    # Comprobar si el jugador existe
    player_validators.player_exists_validator(player_id)

    # Comprobar si el que inicia la partida es el creador
    player_validators.is_creator_validator(player_id)


@db_session
def follow_match_validator(match_id: int, player_id: int) -> bool:
    match = get_match_by_id(match_id)
    if not match:
        return False

    player = Player.get(player_id=player_id, match=match)
    if not player:
        return False

    return True


@db_session
def pass_turn_validator(match_id: int, player_id: int):
    # Chequeamos si la partida existe
    match = get_match_by_id(match_id)
    if not match:
        raise NOT_EXISTENT_MATCH

    # Chequeamos si el jugador existe
    player = Player.get(player_id=player_id, match=match)
    if not player:
        raise NOT_EXISTENT_PLAYER

    # Chequeamos si es el turno del jugador
    current_turn = get_player_turn(match_id)
    if current_turn != player.name:
        raise NOT_YOUR_TURN

    # Chequeamos si el jugador hizo una jugada antes de pasar el turno
    if not player.stolen_card:
        raise NOT_A_PLAY_WAS_MADE
