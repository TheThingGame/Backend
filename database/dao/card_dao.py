import random
from pony.orm import db_session
from typing import List
from ..models.models import Card, CardType, CardColor, Match, Pot


# Crear cartas numeradas
@db_session
def create_number_cards(color: str, match: Match) -> List[Card]:
    cards = []

    for number in range(10):
        count = 1 if number == 0 else 2
        for _ in range(count):
            cards.append(
                Card(
                    number=number,
                    color=color,
                    card_type=CardType.NUMBER,
                )
            )

    return cards


# Crear cartas de acción
@db_session
def create_action_cards(color: str, match: Match) -> List[Card]:
    cards = []

    action_cards = [
        (CardType.TAKE_TWO, 2),
        (CardType.REVERSE, 2),
        (CardType.JUMP, 2),
    ]

    for card_type, count in action_cards:
        for _ in range(count):
            cards.append(Card(color=color, card_type=card_type))

    return cards


# Crear cartas de comodines
@db_session
def create_wild_cards(match: Match) -> List[Card]:
    cards = []
    wildcards = [(CardType.WILDCARD, 4), (CardType.TAKE_FOUR_WILDCARD, 4)]

    for card_type, count in wildcards:
        for _ in range(count):
            cards.append(Card(card_type=card_type))

    return cards


@db_session
def create_deck(match: Match) -> List[Card]:
    # Creamos las cartas de comodin
    deck = create_wild_cards(match)

    # Creamos las cartas de color (Número y Acción)
    for color in CardColor:
        deck.extend(create_action_cards(color.value, match))
        deck.extend(create_number_cards(color.value, match))

    # Barajamos las cartas
    random.shuffle(deck)

    # Repartimos las cartas
    current_card_index = 0
    for player in match.players:
        hand = deck[current_card_index : current_card_index + 5]
        current_card_index += 5
        player.hand = hand

    deck = deck[current_card_index:]

    return deck


@db_session
def card_db_to_dict(card: Card):
    return {
        "number": card.number if card.number is not None else "",
        "color": card.color if card.color is not None else "",
        "card_type": card.card_type,
    }
