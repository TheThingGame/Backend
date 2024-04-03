from pony.orm import db_session
from passlib.hash import bcrypt
from database.models.models import Match, Player
from view_entities.match_view_entities import NewMatch
from typing import Dict


@db_session
def create_new_match(new_match: NewMatch):
    match_password = bcrypt.hash(new_match.password) if new_match.password else ""
    creator_player = Player(name=new_match.creator_player)

    try:
        match = Match(
            name=new_match.name,
            creator_player=creator_player,
            hashed_password=match_password,
        )

        print("match players:", creator_player.match)

        return True
    except:
        return False


@db_session
def get_match_by_name_and_user(match_name: str, creator_player: str):
    return Match.select(
        lambda m: m.name == match_name or m.creator_player.name == creator_player
    ).first()


@db_session
def get_all_matches():
    return [
        {
            "match_id": m.match_id,
            "name": m.name,
            "players": m.players,
            "creator_player:": m.creator_player.name,
        }
        for m in Match.select()
    ]
