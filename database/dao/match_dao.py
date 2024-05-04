from pony.orm import db_session, TransactionIntegrityError
from ..models.models import Match, Player, CardType
from .player_dao import create_player_or_400
from view_entities.match_view_entities import MatchInfo
from exceptions import player_exceptions
from exceptions import match_exceptions
from ..models.models import CARDS
from utils.match_utils import lobbys
from deserializers.match_deserializers import cards_deserializer


@db_session
def create_match_or_400(match_name: str, creator_id: int) -> int:
    try:
        creator = Player[creator_id]
        match = Match(name=match_name, creator=creator, players=[creator])
        match.flush()
        return match.match_id
    except TransactionIntegrityError:
        raise match_exceptions.MATCH_EXISTS
    except Exception as e:
        raise match_exceptions.INTERNAL_ERROR_CREATING_MATCH from e


@db_session
def create_new_match(match_name: str, creator_name: str) -> tuple[int, int]:
    creator_id = create_player_or_400(creator_name)
    match_id = create_match_or_400(match_name, creator_id)
    return match_id, creator_id


@db_session
def get_match_by_id(match_id: int):
    return Match.get(match_id=match_id)


@db_session
def get_match_by_code(code: str) -> Match:
    return Match.get(code=code)


@db_session
def join_update(player_name: str, code: str) -> tuple[int, int]:
    # Chequeamos si la partida existe
    match = get_match_by_code(code)
    if not match:
        raise match_exceptions.NOT_EXISTENT_MATCH

    # Chequeamos si la partida esta iniciada
    if match.started:
        raise match_exceptions.MATCH_ALREADY_STARTED

    # Chequeamos si la partida esta llena
    if match.max_players == len(match.players):
        raise match_exceptions.MATCH_FULL

    # Agregamos el jugador a la partida
    player = Player[create_player_or_400(player_name)]
    match.players.add(player)

    return match.match_id, player.player_id


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
def apply_card_effect(match_id: int, card_id: int, color: str | None = None):
    match = Match[match_id]
    card = Card[card_id]
    pot = match.pot

    # Ahora la carta no pertenece al jugador sino al pozo
    card.player = None
    card.match_in_deck = None
    pot.last_played_card = card
    card.pot = pot
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

    if match.pot.color and card.card_type not in [
        CardType.WILDCARD,
        CardType.TAKE_FOUR_WILDCARD,
    ]:
        match.pot.color = None

    # Saltar el siguiente turno
    if card.card_type == CardType.JUMP:
        update_turn(match, match.current_player_index, match.turn_direction * 2, length)
    elif card.card_type == CardType.TAKE_FOUR_WILDCARD:
        next_turn = match.current_player_index + match.turn_direction % len(
            match.players
        )
        next_player_hand = list(match.players)[next_turn].hand

        if CardType.TAKE_FOUR_WILDCARD in [c.card_type for c in next_player_hand]:
            pass

        pass
    else:
        update_turn(match, match.current_player_index, match.turn_direction, length)
