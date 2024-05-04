import uuid
import json
import random
from copy import deepcopy
from pony.orm import (
    Database,
    PrimaryKey,
    Required,
    Optional,
    Optional,
    Set,
    IntArray,
    StrArray,
    composite_key,
    db_session,
)
from exceptions.match_exceptions import NOT_ENOUGH_PLAYERS
from .enums import CardType, CardColor, Direction

db = Database()
CARDS = json.load(open("static/cards.json"))


class Player(db.Entity):
    player_id = PrimaryKey(int, auto=True)
    name = Required(str, autostrip=True, unique=True)
    hand = Optional(IntArray)
    match = Optional("Match", reverse="players")
    creator = Optional("Match", reverse="creator")


class Match(db.Entity):
    __randomized_cards = None

    match_id = PrimaryKey(int, auto=True)
    name = Required(str, autostrip=True, unique=True)
    creator = Required(Player)
    code = Required(uuid.UUID, default=uuid.uuid4)
    min_players = Required(int, default=2)
    max_players = Required(int, default=10)
    started = Required(bool, default=False)
    players = Set(Player)
    state = Optional("MatchState", reverse="match")

    @property
    def num_players(self):
        return len(self.players)

    @property
    def shuffle_cards(self):
        # Debe ser llamada una sola vez
        if self.__randomized_cards is not None:
            return
        self.__randomized_cards = deepcopy(CARDS)
        random.shuffle(self.__randomized_cards)

    @property
    def deal_cards(self):
        for player in self.players:
            for _ in range(7):
                player.hand.append(self.__randomized_cards.pop()["id"])

    @property
    def initialize_pot_and_deck(self):
        while self.__randomized_cards[-1]["type"] == CardType.TAKE_FOUR_WILDCARD:
            random.shuffle(self.__randomized_cards)

        pot = [self.__randomized_cards.pop()["id"]]
        deck = [card["id"] for card in self.__randomized_cards]
        return pot, deck

    def start(self):
        # if self.min_players > self.num_players or self.max_players < self.num_players:
        # raise NOT_ENOUGH_PLAYERS

        # Mezclamos las cartas
        self.shuffle_cards

        # Repartimos las cartas
        self.deal_cards

        # Inicializamos el pot y el deck
        pot, deck = self.initialize_pot_and_deck

        # Damos un orden a los jugadores
        ordered_players = [player.name for player in self.players]

        state = MatchState(
            match=self, pot=pot, deck=deck, ordered_players=ordered_players
        )
        state.apply_action_card_penalty

        self.started = True


class MatchState(db.Entity):
    __turn = 0

    ordered_players = Required(StrArray)
    acumulator = Required(int, default=0)
    color = Optional(CardColor)
    direction = Required(Direction, default=Direction.RIGHT)
    match = Required(Match)
    deck = Required(IntArray)
    pot = Required(IntArray)

    @property
    def top_card(self):
        return self.pot[-1]

    @property
    def apply_action_card_penalty(self):
        card_type = CARDS[self.top_card]["type"]

        if card_type == CardType.REVERSE:
            self.direction = self.reverse()
        if card_type == CardType.JUMP:
            self.advance_turn(2)
        if card_type == CardType.TAKE_TWO:
            draw_cards = self.draw_cards(2, self.turn())
            self.advance_turn(1)

    def turn(self):
        return self.ordered_players[self.__turn]

    def advance_turn(self, steps: int):
        self.__turn = (self.__turn + (self.direction * steps)) % len(
            self.ordered_players
        )

    def reverse(self):
        self.direction = (
            Direction.RIGHT if self.direction == Direction.RIGHT else Direction.LEFT
        )

    def draw_cards(self, quantity: int, player_name: str):
        draw_cards = [self.deck.pop() for _ in range(quantity)]
        player = Player.get(name=player_name)
        player.hand.extend(draw_cards)
        return draw_cards


db.bind(provider="sqlite", filename="database.sqlite", create_db=True)
db.generate_mapping(create_tables=True)
