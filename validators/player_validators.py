from pony.orm import db_session, ObjectNotFound
from exceptions import player_exceptions
from database.models.models import Player


def player_name_validator(player_name: str):
    if len(player_name) < 3 or len(player_name) > 16:
        raise player_exceptions.INVALID_PLAYER_LENGTH


@db_session
def player_exists_validator(player_id: int):
    try:
        Player[player_id]
    except ObjectNotFound:
        raise player_exceptions.NOT_EXISTS_PLAYER


@db_session
def is_creator_validator(player_id: int):
    player = Player[player_id]
    if not player.creator:
        raise player_exceptions.NOT_CREATOR
