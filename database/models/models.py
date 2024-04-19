from pony.orm import *
from enum import Enum

db = Database()


class CardType(str, Enum):
    NUMBER = "NUMBER"
    TAKE_TWO = "TAKE_TWO"
    REVERSE = "REVERSE"
    JUMP = "JUMP"
    WILDCARD = "WILDCARD"
    TAKE_FOUR_WILDCARD = "TAKE_FOUR_WILDCARD"


class CardColor(str, Enum):
    RED = "RED"
    BLUE = "BLUE"
    GREEN = "GREEN"
    YELLOW = "YELLOW"


class Card(db.Entity):
    card_id = PrimaryKey(int, auto=True)
    number = Optional(int)
    color = Optional(CardColor)
    card_type = Required(CardType, default=CardType.NUMBER)
    player = Optional("Player")
    stealer = Optional("Player")
    pot = Optional("Pot", reverse="cards")
    last_played_in_pot = Set("Pot")
    match_in_deck = Optional("Match", reverse="deck")


class Pot(db.Entity):
    pot_id = PrimaryKey(int, auto=True)
    acumulator = Optional(int)
    cards = Set(Card)
    color = Optional(CardColor)
    last_played_card = Optional(Card)
    match = Required("Match")


class Player(db.Entity):
    player_id = PrimaryKey(int, auto=True)
    name = Required(str, autostrip=True)
    hand = Set(Card)
    stolen_card = Optional(Card, reverse="stealer")
    match = Optional("Match", reverse="players")
    creator_match = Optional("Match")


class Match(db.Entity):
    match_id = PrimaryKey(int, auto=True)
    name = Required(str, autostrip=True)
    creator_player = Required(Player)
    code = Required(str, unique=True)
    min_players = Required(int, default=2)
    max_players = Required(int, default=10)
    started = Required(bool, default=False)
    players = Set(Player)
    deck = Set(Card)
    pot = Optional(Pot)
    current_player_index = Required(int, default=0)
    turn_direction = Required(int, default=1)
    composite_key(name, creator_player)


db.bind(provider="sqlite", filename="database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
