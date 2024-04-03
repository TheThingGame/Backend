from pony.orm import *
from enum import Enum

db = Database()


class CardType(str, Enum):
    NUMBER = "number"
    ACTION = "action"


class CardColor(str, Enum):
    RED = "red"
    BLUE = "blue"
    GREEN = "green"
    YELLOW = "yellow"


class Card(db.Entity):
    card_id = PrimaryKey(int, auto=True)
    number = Optional(int)
    color = Optional(CardColor)
    card_type = Required(CardType, default=CardType.NUMBER)
    player = Optional("Player")
    pot = Optional("Pot", reverse="cards")
    last_played_in_pot = Set("Pot", reverse="last_played_card")
    match_in_deck = Optional("Match", reverse="deck")


class Pot(db.Entity):
    pot_id = PrimaryKey(int, auto=True)
    cards = Set(Card)
    last_played_card = Optional(Card)
    match = Required("Match")


class Player(db.Entity):
    player_id = PrimaryKey(int, auto=True)
    name = Required(str)
    hand = Set("Card")
    match = Optional("Match", reverse="players")
    creator_match = Optional("Match", reverse="creator_player")


class Match(db.Entity):
    match_id = PrimaryKey(int, auto=True)
    name = Required(str)
    creator_player = Required(Player, reverse="creator_match")
    hashed_password = Optional(str)
    min_players = Required(int, default=2)
    max_players = Required(int, default=10)
    started = Required(bool, default=False)
    finished = Required(bool, default=False)
    players = Set(Player, reverse="match")
    deck = Set(Card)
    pot = Optional(Pot)
    current_player_index = Required(int, default=0)
    turn_direction = Required(int, default=1)
    composite_key(name, creator_player)


db.bind(provider="sqlite", filename="database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
