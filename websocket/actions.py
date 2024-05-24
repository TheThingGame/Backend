from pony.orm import db_session
from database.models.models import Match, Player
from database.models.enums import CardType, CardColor
from deserializers.match_deserializers import cards_deserializer
from websocket import messages
from utils.match_utils import lobbys


@db_session
async def start(match_id: int):
    match = Match[match_id]
    state = match.state
    turn = state.get_current_turn
    prev_turn = state.get_prev_turn
    pot = cards_deserializer([state.top_card])[0]
    pot_type = pot["type"]
    lobby = await lobbys[match_id]

    # Envía un mensaje de inicio del juego a cada jugador
    for player in match.players:
        hand = cards_deserializer(player.hand)
        await lobby.send_personal_message(
            messages.start_message(hand, pot, turn), player.name
        )

    if pot_type in [CardType.NUMBER, CardType.REVERSE]:
        return

    if pot_type == CardType.WILDCARD:
        await lobby.broadcast(messages.wildcard)

    if pot_type == CardType.TAKE_TWO:
        player = Player.get(name=prev_turn)
        cards = state.steal()
        player.hand.extend(cards)

        await lobby.send_personal_message(messages.take, prev_turn)
        await lobby.broadcast(messages.take_broadcast, prev_turn)

    if pot_type == CardType.JUMP:
        await lobby.broadcast(messages.jump)


@db_session
async def play_card(match_id: int, card: dict = None, cards: list = None):
    state = Match[match_id].state
    lobby = lobbys[match_id]
    current_turn = state.get_current_turn
    prev_turn = state.get_prev_turn

    if cards:
        await lobby.send_personal_message(
            messages.not_uno(cards, current_turn), prev_turn
        )
        await lobby.broadcast(
            messages.not_uno_broadcast(current_turn, prev_turn), prev_turn
        )
    else:
        await lobby.broadcast(messages.card_played(card, current_turn, prev_turn))

    if state.winner:
        await lobby.broadcast(messages.winner(prev_turn))


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
    if state.color != CardColor.START:
        message_to_broadcast["turn"] = state.get_current_turn

    await lobbys[match_id].broadcast(message_to_broadcast)


@db_session
async def leave(match_id: int, player_name: str):

    match = Match.get(match_id=match_id)
    if not match:
        await lobbys[match_id].broadcast({"action": "lobby_destroy"})
        await lobbys[match_id].destroy()
    else:
        await lobbys[match_id].broadcast(
            {"action": "player_left", "player": player_name}, player_name
        )
        await lobbys[match_id].disconnect(player_name)
