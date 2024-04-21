from pony.orm import db_session
from ..models.models import Match, Player, Pot, CardType, Card
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
    # Iniciamos la partida
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
def update_turn(match: Match, current_turn: int, direction: int, length: int):
    match.current_player_index = (current_turn + direction) % length


@db_session
def get_player_turn(match_id: int) -> str:
    match = Match[match_id]

    players_ordered = list(match.players.order_by(lambda p: p.player_id))

    current_player = players_ordered[match.current_player_index]

    return current_player.name


@db_session
def apply_card_effect(match: Match, card: Card, color: str | None):
    card.player = None
    card.match_in_deck = None
    card.pot = match.pot
    card.pot.last_played_in_pot = card
    length = len(match.players)

    if card.stealer:
        card.stealer = None

    # Ajustar acumulador para TAKE_TWO o TAKE_FOUR_WILDCARD
    if card.card_type == CardType.TAKE_TWO:
        match.pot.acumulator += 2
    elif card.card_type == CardType.TAKE_FOUR_WILDCARD:
        match.pot.acumulator += 4

    # Configurar color para WILDCARD y TAKE_FOUR_WILDCARD
    if card.card_type in [CardType.WILDCARD, CardType.TAKE_FOUR_WILDCARD]:
        match.pot.color = color

    # Cambiar dirección para REVERSE
    if card.card_type == CardType.REVERSE:
        match.turn_direction *= -1

    # Saltar el siguiente turno para JUMP
    if card.card_type == CardType.JUMP:
        update_turn(match, match.current_player_index, match.turn_direction * 2, length)
    else:
        update_turn(match, match.current_player_index, match.turn_direction, length)
