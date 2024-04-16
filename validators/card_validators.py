from database.models.models import Match, Player, Card
from pony.orm import db_session
from database.dao.match_dao import get_match_by_id
from database.dao.player_dao import get_player_by_id
from utils.match_utils import NOT_EXISTENT_MATCH
from utils.player_utils import NOT_EXISTENT_PLAYER, NOT_YOUR_TURN
from utils.cards_utils import INVALID_PLAYED_CARD
from database.models.models import CardType


@db_session
def play_card_validator(match_id: int, player_id: int, card_id: int):

    # Chequeamos si la partida existe
    match = get_match_by_id(match_id)
    if not match:
        raise NOT_EXISTENT_MATCH

    # Chequeamos si el jugador existe
    player = get_player_by_id(player_id)
    if not player:
        raise NOT_EXISTENT_PLAYER

    # Chequeamos si es el turno del jugador
    players = [p.name for p in match.players]
    if players[match.current_player_index] != player.name:
        raise NOT_YOUR_TURN

    # Chequeamos si la carta existe
    card = Card.get(card_id=card_id, player=player)
    if not card:
        raise CARD_NOT_FOUND

    # Chequeamos si la carta puede ser lanzada al pozo
    if card_type in {CardType.WILDCARD, CardType.TAKE_FOUR_WILDCARD}:
        return

    if card_type == CardType.NUMBER:
        if card.number == pot.number or card.color == pot.color:
            return
        raise INVALID_PLAYED_CARD

    if card.color == pot.color or card_type == pot.card_type:
        return

    raise INVALID_PLAYED_CARD
