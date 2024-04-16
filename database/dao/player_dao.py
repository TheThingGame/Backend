from pony.orm import db_session
from ..models.models import Player


@db_session
def create_new_player(name: str) -> Player:
    try:
        player = Player(name=name)
        player.flush()
        return player
    except:
        return None


@db_session
def get_player_by_id(player_id: int) -> Player:
    return Player.get(player_id=player_id)
