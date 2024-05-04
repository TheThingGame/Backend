from pony.orm import db_session
from database.models.models import Match
from deserializers.match_deserializers import cards_deserializer
from websocket import messages
from utils.match_utils import lobbys


@db_session
async def start(match_id: int):
    match = Match[match_id]
    state = match.state
    turn = state.turn()
    pot = cards_deserializer(state.pot)

    for player in match.players:
        hand = cards_deserializer(player.hand)
        await lobbys[match_id].send_personal_message(
            messages.start_message(hand, pot, turn), player.name
        )
