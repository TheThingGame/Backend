import uuid
import random
from typing import Dict
from pony.orm import db_session
from passlib.hash import bcrypt
from view_entities.match_view_entities import NewMatch, JoinMatch
from ..models.models import Match, Player, Card, CardType, CardColor, Pot
from ..dao.card_dao import create_deck
from view_entities.match_view_entities import MatchInfo
from pony.orm import ERDiagramError
from utils.match_utils import INTERNAL_ERROR_CREATING_MATCH


@db_session
def create_new_match(name: str, creator_player: str, code: str) -> Match:
    new_player = Player(name=creator_player)
    new_player.flush()

    try:
        return Match(
            name=name,
            creator_player=new_player,
            code=code,
            players=[new_player],
        )
    except (ERDiagramError, ValueError) as e:
        raise INTERNAL_ERROR_CREATING_MATCH from e


@db_session
def get_match_info(match_id: int, player_name: str) -> MatchInfo:
    match = Match[match_id]
    player_id = Player.get(name=player_name).player_id

    return MatchInfo(
        **{
            **match.to_dict(),
            "player_id": player_id,
            "creator_player": match.creator_player.name,
            "players": [p.name for p in match.players],
        }
    )


@db_session
def get_match_by_name_and_user(match_name: str, creator_player: str):
    return Match.select(
        lambda m: m.name == match_name or m.creator_player.name == creator_player
    ).first()


@db_session
def get_match_by_id(match_id: int):
    return Match.get(match_id=match_id)


@db_session
def get_all_matches():
    return [
        {
            "code": m.code,
            "name": m.name,
            "players": [{"name": p.name} for p in m.players],
            "creator_player:": m.creator_player.name,
        }
        for m in Match.select()
    ]


@db_session
def get_match_by_code(code: str) -> Match:
    return Match.get(code=code)


@db_session
def update_joining_user_match(match_id: int, player_name: str):
    match = Match[match_id]

    new_player = Player(name=player_name)
    new_player.flush()

    try:
        match.players.add(new_player)
        return True
    except:
        return False


@db_session
def update_executed_match(match_id: int):
    match = Match[match_id]
    match.started = True

    deck = create_deck(match)

    # Sacamos una carta del mazo y la ponemos en el pozo
    card_pot = deck[0]
    pot = Pot(cards=[card_pot], last_played_card=card_pot, match=match)
    match.deck = deck[1:]

    return True


@db_session
def get_players_by_match_id(match_id: int):
    return [
        {
            "name": p.name,
            "hand": [c.to_dict() for c in p.hand],
        }
        for p in Match[match_id].players
    ]


@db_session
def update_turn_and_direction(
    match_id: int, current_turn: int, direction: int, length: int
):
    match = Match[match_id].current_player_index = (current_turn + direction) % length
    match.current_player_index = (current_turn + direction) % length
    if direction in [2, -2]:
        pass
