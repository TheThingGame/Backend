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
def play_card_update(match_id: int, player_id: int, card: dict):
    state = Match[match_id].state
    player = Player[player_id]
    card_type = card["type"]

    # Ahora la carta no pertenece al jugador sino al pozo
    state.pot.append(card["id"])
    player.hand.remove(card["id"])

    # El jugador tiro la carta robada, ajustamos el acumulador
    if state.acumulator == 1:
        state.acumulator = 0

    if state.color:
        state.color = None

    # Ajustamos acumulador para TAKE_TWO o TAKE_FOUR_WILDCARD
    if card_type == CardType.TAKE_TWO:
        state.acumulator += 2
        # Retornamos porque el jugador tiene que cambiar de color, por lo tanto sigue teniendo el turno
        return
    elif card_type == CardType.TAKE_FOUR_WILDCARD:
        state.acumulator += 4
        # Retornamos porque el jugador tiene que cambiar de color, por lo tanto sigue teniendo el turno
        return

    # Cambiar dirección para REVERSE
    if card_type == CardType.REVERSE:
        state.reverse

    # Pasamoss el turno
    if card_type == CardType.JUMP:
        state.next_turn(2)
    else:
        state.next_turn(1)


@db_session
async def steal_card_update(match_id: int, player_id: int) -> dict:
    state = Match[match_id].state
    player = Player[player_id]
    steal_cards = state.steal()
    player.hand.extend(steal_cards)
    cards = cards_deserializer(steal_cards)

    # ----------PODRIA SACAR ESTE CODIGO Y PONERLO EN LA FUNCION QUE MANEJE LOS MENSAJES......
    if state.acumulator > 0:
        return {
            "action": "TAKE",
            "player": state.get_prev_turn,
            "turn": state.get_current_turn,
            "cards": cards,
        }

    return {"action": "STEAL", "player": state.get_current_turn, "card": cards[0]}
