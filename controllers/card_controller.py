from fastapi import APIRouter
from validators.card_validators import play_card_validator
from view_entities.card_view_entities import PlayCard
from database.models.models import CardType, Match, Card

card_controller = APIRouter()


@card_controller.put("/play-card/{match_id}")
def play_card(match_id: int, play_card_data: PlayCard):
    play_card_validator(match_id, play_card_data.player_id, play_card_data.card_id)
    message = {"action": "", "turn": "", "player_name": ""}

    card = Card[play_card_data.card_id]
    match = Match[match_id]

    if card.card_type == CardType.TAKE_TWO:
        match.pot.acumulator += 2
        match.current_player_index = (
            match.current_player_index + match.turn_direction
        ) % len(match.players)

    if card.card_type == CardType.TAKE_FOUR_WILDCARD:
        match.pot.acumulator += 4
        match.current_player_index = (
            match.current_player_index + match.turn_direction
        ) % len(match.players)

    if card.card_type == CardType.WILDCARD:
        match.pot.color = play_card_data.color
        match.current_player_index = (
            match.current_player_index + match.turn_direction
        ) % len(match.players)

    if card.card_type == CardType.REVERSE:
        match.turn_direction *= -1
        match.current_player_index = (
            (match.current_player_index + (match.turn_direction * -1))
        ) % len(match.players)

    if card.card_type == CardType.JUMP:
        match.current_player_index = (
            match.current_player_index + (2 * match.turn_direction)
        ) % len(match.players)

    if card.card_type == CardType.NUMBER:
        match.current_player_index = (
            match.current_player_index + match.turn_direction
        ) % len(match.players)

    # update_plaay_card(match_id, play_card_data)
    # Si la carta es toma 2 actualizamos el acumulador, turno y enviamos un mensaje(action:take_two, take:2 + acumulador)

    # Si la carta es toma 4 actualizamos el acumulador, turno y enviamos un mensaje(action:take_four, take:4 + acumulador color:"red")

    # Si la carta es reverse actualizamos la direccion a la inversa, osea que pasamos el turno a la inversa

    # Si la carta es comodin actualizamos el color y turno

    # Si la carta es jump actualizamos turno saltando al jugador de la izquierda

    return
