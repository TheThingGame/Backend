from pony.orm import db_session, TransactionIntegrityError, CacheIndexError
from ..models.models import Player
from exceptions import player_exceptions


@db_session
def create_player_or_400(player_name: str) -> int:
    try:
        player = Player(name=player_name)
        player.flush()
        return player.player_id
    except (TransactionIntegrityError, CacheIndexError):
        raise player_exceptions.PLAYER_EXISTS
    except Exception as e:
        raise player_exceptions.INTERNAL_ERROR_CREATING_PLAYER from e


@db_session
def get_player_by_id(player_id: int) -> Player:
    return Player.get(player_id=player_id)
