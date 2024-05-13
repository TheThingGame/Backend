from pony.orm import db_session
from database.models.models import Match, Player, CARDS
from database.models.enums import CardType, CardColor
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
    if pot_type in [CardType.NUMBER, CardType.REVERSE]:
        return

    if pot_type == CardType.WILDCARD:
        await lobbys[match_id].broadcast(
            {"action": "WILDCARD", "player": state.get_current_turn}
        )
        return

    if pot_type == CardType.TAKE_TWO:
        player = Player.get(name=player_affected)
        cards = state.steal()
        player.hand.extend(cards)

        await lobbys[match_id].send_personal_message(
            {
                "action": "TAKE",
                "turn": state.get_current_turn,
                "cards": cards_deserializer(cards),
            },
            player_affected,
        )

    await lobbys[match_id].broadcast(
        {"action": pot_type, "player": player_affected, "turn": state.get_current_turn},
        player_affected,
    )

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


@db_session
async def steal_card(match_id: int, cards: list):
    state = Match[match_id].state
    current_turn = state.get_current_turn
    prev_turn = state.get_prev_turn

    message_data = {"action": "TAKE", "cards": cards}
    broadcast_data = {"action": "TAKE"}

    if len(cards) > 1:
        message_data["turn"] = current_turn
        await lobbys[match_id].send_personal_message(message_data, prev_turn)
        broadcast_data["player"] = prev_turn
        broadcast_data["turn"] = current_turn
    else:
        await lobbys[match_id].send_personal_message(message_data, current_turn)
        broadcast_data["player"] = current_turn
    await lobbys[match_id].broadcast(broadcast_data, broadcast_data["player"])


@db_session
async def next_turn(match_id: int):
    current_turn = Match[match_id].state.get_current_turn

    message_to_broadcast = {
        "action": "NEXT_TURN",
        "turn": current_turn,
    }

    await lobbys[match_id].broadcast(message_to_broadcast)


@db_session
async def change_color(match_id: int, color: str):
    state = Match[match_id].state

    message_to_broadcast = {
        "action": "CHANGE_COLOR",
        "color": color,
        "player": state.get_prev_turn,
    }
    # podriamos chequear si current=prev
    if state.color != CardColor.START:
        message_to_broadcast["turn"] = state.get_current_turn

    await lobbys[match_id].broadcast(message_to_broadcast)


@db_session
async def uno(match_id: int, cards: list):
    state = Match[match_id].state

    await lobbys[match_id].send_personal_message(
        {"action": "NO_WIN", "cards": cards_deserializer(cards)}
    )
    await lobbys[match_id].broadcast(
        {
            "action": "NO_WIN",
            "turn": state.get_current_turn,
            "player": state.get_prev_turn,
        }
    )
