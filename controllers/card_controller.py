from fastapi import APIRouter, status, Body
from typing import Annotated
from pony.orm import db_session
from validators.card_validators import play_card_validator, steal_card_validator
from view_entities.card_view_entities import PlayCard
from database.models.models import Match, Card, Player, CardType
from database.dao.match_dao import get_player_turn, apply_card_effect, update_turn
from database.dao.card_dao import card_db_to_dict, card_db_to_dict
from utils.match_utils import lobbys


card_controller = APIRouter()


@card_controller.put("/play-card/{match_id}", status_code=status.HTTP_200_OK)
async def play_card(match_id: int, play_card_data: PlayCard):
    play_card_validator(
        match_id, play_card_data.player_id, play_card_data.card_id, play_card_data.color
    )

    with db_session:
        match = Match[match_id]
        card = Card[play_card_data.card_id]
        apply_card_effect(match_id, play_card_data.card_id, play_card_data.color)
        player_turn = get_player_turn(match_id)

        message_to_broadcast = {
            "action": card.card_type,
            "turn": player_turn,
            "pot": card_db_to_dict(card.pot.last_played_card),
        }
        await lobbys[match_id].broadcast(message_to_broadcast)

    return True


@card_controller.put("/steal-card/{match_id}", status_code=status.HTTP_200_OK)
async def steal_card(match_id: int, player_id: Annotated[int, Body(embed=True)]):
    steal_card_validator(match_id, player_id)

    with db_session:
        match = Match[match_id]
        player = Player[player_id]
        player_turn = get_player_turn(match_id)

        if match.pot.acumulator > 0:
            # Si hay cartas acumuladas por acciones anteriores
            steal_cards = list(match.deck)[: match.pot.acumulator]
            for c in steal_cards:
                c.match_in_deck = None
                c.player = player

            # Actualizamos el acumulador a 0
            match.pot.acumulator = 0
            update_turn(
                match,
                match.current_player_index,
                match.turn_direction,
                len(match.players),
            )

            # Enviamos un mensaje al jugador con las cartas robadas
            message_to_player = {
                "action": "TAKE_RESPONSE",
                "cards": [card_db_to_dict(c) for c in steal_cards],
            }
            await lobbys[match_id].send_personal_message(message_to_player, player_id)

            # Notificamos a todos los jugadores que se robaron cartas

            message_to_broadcast = {"action": "TAKE", "turn": player_turn}
            await lobbys[match_id].broadcast(message_to_broadcast)
            return

        # Si no hay cartas acumuladas, se roba una carta normalmente
        steal_card = list(match.deck)[0]
        steal_card.player = player
        steal_card.stealer = player
        steal_card.match_in_deck = None
        pot = match.pot.last_played_card

        # Enviamos un mensaje al jugador con la carta robada
        message_to_player = {
            "action": "STEAL_CARD",
            "card": card_db_to_dict(steal_card),
        }
        await lobbys[match_id].send_personal_message(message_to_player, player_id)

        # Si la carta robada no coindice con el pozo, se pasa el turno automaticamente
        if steal_card.card_type in [CardType.TAKE_FOUR_WILDCARD, CardType.WILDCARD]:
            return

        if match.pot.color and (steal_card.color == match.pot.color):
            return

        if steal_card.card_type == CardType.NUMBER:
            if steal_card.number == pot.number or steal_card.color == pot.color:
                return
        else:
            if steal_card.color == pot.color or steal_card.card_type == pot.card_type:
                return

        # Pasamos el turno
        update_turn(
            match,
            match.current_player_index,
            match.turn_direction,
            len(match.players),
        )
        player.stolen_card = None
        message_to_broadcast = {
            "action": "PASS_TURN",
            "turn": player_turn,
        }

        await lobbys[match_id].broadcast(message_to_broadcast)

        return True
