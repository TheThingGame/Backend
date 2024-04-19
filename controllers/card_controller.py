from fastapi import APIRouter, status
from pony.orm import db_session
from validators.card_validators import play_card_validator
from view_entities.card_view_entities import PlayCard
from database.models.models import CardType, Match, Card
from database.dao.match_dao import update_match_play_card
from utils.match_utils import lobbys

card_controller = APIRouter()


@card_controller.put("/play-card/{match_id}", status_code=status.HTTP_200_OK)
async def play_card(match_id: int, play_card_data: PlayCard):
    # play_card_validator(match_id, play_card_data.player_id, play_card_data.card_id)
    # update_match_play_card(match_id, play_card_data.card_id, play_card_data.color)

    # with db_session:
    #   card = Card[play_card_data.card_id]
    #  match = Match[match_id]

    # print("MATCH:", match)
    # message_to_broadcast = {
    #   "action": card.card_type,
    #  "turn": match.current_player_index,
    # }
    # await lobbys[match_id].broadcast(message_to_broadcast)

    return True

    # update_plaay_card(match_id, play_card_data)
    # Si la carta es toma 2 actualizamos el acumulador, turno y enviamos un mensaje(action:take_two, take:2 + acumulador)

    # Si la carta es toma 4 actualizamos el acumulador, turno y enviamos un mensaje(action:take_four, take:4 + acumulador color:"red")

    # Si la carta es reverse actualizamos la direccion a la inversa, osea que pasamos el turno a la inversa

    # Si la carta es comodin actualizamos el color y turno

    # Si la carta es jump actualizamos turno saltando al jugador de la izquierda
