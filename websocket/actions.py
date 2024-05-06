from pony.orm import db_session
from database.models.models import Match, Player, CARDS
from database.models.enums import CardType
from deserializers.match_deserializers import cards_deserializer
from websocket import messages
from utils.match_utils import lobbys


@db_session
async def start(match_id: int):
    match = Match[match_id]
    state = match.state
    turn = state.get_current_turn
    player_affected = state.get_prev_turn
    pot = cards_deserializer([state.top_card])[0]
    pot_type = pot["type"]

    # Envía un mensaje de inicio del juego a cada jugador
    for player in match.players:
        hand = cards_deserializer(player.hand)
        await lobbys[match_id].send_personal_message(
            messages.start_message(hand, pot, turn), player.name
        )

    # Maneja las penalizaciones de las cartas de acción
    if pot_type == CardType.NUMBER:
        return

    if pot_type == CardType.TAKE_TWO:
        player = Player.get(name=player_affected)
        cards = state.steal()
        player.hand.extend(cards)

        await lobbys[match_id].send_personal_message(
            {"action": "TAKE", "cards": cards_deserializer(cards)}, player_affected
        )

    await lobbys[match_id].broadcast({"action": pot_type, "player": player_affected})

    return True


@db_session
async def play_card(match_id: int, card: dict):
    state = Match[match_id].state
    turn = state.get_current_turn

    message_to_broadcast = {
        "action": card["type"],
        "turn": turn,
        "pot": card,
    }
    await lobbys[match_id].broadcast(message_to_broadcast)
