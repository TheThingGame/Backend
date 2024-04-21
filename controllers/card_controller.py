from fastapi import APIRouter, status
from pony.orm import db_session
from validators.card_validators import play_card_validator
from view_entities.card_view_entities import PlayCard
from database.models.models import Match, Card
from database.dao.match_dao import get_player_turn, apply_card_effect
from database.dao.card_dao import card_db_to_dict
from utils.match_utils import lobbys

card_controller = APIRouter()


@card_controller.put("/play-card/{match_id}", status_code=status.HTTP_200_OK)
async def play_card(match_id: int, play_card_data: PlayCard):
    play_card_validator(match_id, play_card_data.player_id, play_card_data.card_id)

    with db_session:
        match = Match[match_id]
        card = Card[play_card_data.card_id]
        apply_card_effect(match, card, play_card_data.color)
        player_turn = get_player_turn(match_id)

        message_to_broadcast = {
            "action": card.card_type,
            "turn": player_turn,
            "pot": card_db_to_dict(card.pot.last_played_card),
        }
        await lobbys[match_id].broadcast(message_to_broadcast)

    return True
