import re
from pony.orm import db_session, ObjectNotFound
from fastapi import HTTPException, status, WebSocket
from view_entities.match_view_entities import NewMatch, JoinMatch, MatchID
from database.dao.match_dao import (
    get_match_by_name_and_user,
    get_match_by_code,
    get_match_by_id,
)
from database.models.models import Match, Player
from utils.match_utils import (
    NOT_EXISTENT_MATCH,
    INVALID_MATCH_CODE,
    INVALID_PLAYER_NAME_LENGTH,
    MATCH_ALREADY_STARTED,
    MATCH_FULL,
    NOT_CREATOR,
    NOT_ENOUGH_PLAYERS,
)

from utils.player_utils import NOT_EXISTENT_PLAYER


def new_match_validator(new_match: NewMatch):
    match = get_match_by_name_and_user(new_match.name, new_match.creator_player)
    errors = []

    if len(new_match.name) < 3 or len(new_match.name) > 16:
        errors.append("The match name has to have between 3 and 16 characters.")

    if match:
        errors.append(
            "A match with the same name or a player with the same name already exists."
        )

    if errors:
        detail = "\n".join(errors)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)


@db_session
def join_match_validator(join_match: JoinMatch) -> int:
    # Validamos los datos del cuerpo de solicitud
    if not re.match(r"^[a-z0-9]{3}$", join_match.code):
        raise INVALID_MATCH_CODE

    if len(join_match.player_name) < 3 or len(join_match.player_name) > 16:
        raise INVALID_PLAYER_NAME_LENGTH

    # Chequeamos si la partida existe
    match = get_match_by_code(join_match.code)
    if not match:
        raise NOT_EXISTENT_MATCH

    # Chequeamos si la partida esta iniciada
    if match.started:
        raise MATCH_ALREADY_STARTED

    # Chequeamos si la partida esta llena
    if match.max_players == len(match.players):
        raise MATCH_FULL

    # Chequeamos si el nombre de jugador existe en la partida
    players_in_match = [p.name for p in match.players]
    if join_match.player_name in players_in_match:
        raise USER_ALREADY_JOINED

    return match.match_id


@db_session
def start_match_validator(player_id: int, match_id: int):
    # Comprobar si la partida existe
    match = get_match_by_id(match_id)
    if not match:
        raise NOT_EXISTENT_MATCH

    # Comprobar si la partida está iniciada
    if match.started:
        raise MATCH_ALREADY_STARTED

    # Comprobar si el jugador existe
    player = Player.get(player_id=player_id)
    if not player:
        raise NOT_EXISTENT_PLAYER

    # Comprobar si el que inicia la partida es el creador
    if not player.creator_match:
        raise NOT_CREATOR

    # Comprobar si la cantidad de jugadores es mayor al mínimo
    if len(match.players) < match.min_players:
        raise NOT_ENOUGH_PLAYERS


@db_session
def follow_match_validator(match_id: int, player_id: int) -> bool:
    match = get_match_by_id(match_id)
    if not match:
        return False

    player = Player.get(player_id=player_id, match=match)
    if not player:
        return False

    return True
