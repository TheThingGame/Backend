from deserializers.match_deserializers import cards_deserializer


def join_message(player_name: str):
    return {"action": "join", "player_name": player_name}


def start(hand: list, pot: list, turn: str) -> dict:
    return {"action": "start", "data": {"hand": hand, "pot": pot, "turn": turn}}


def not_uno(cards: list, turn: str) -> dict:
    cards_parse = cards_deserializer(cards)
    return {"action": "NOT_UNO", "cards": cards_parse, "turn": turn}


def not_uno_all(turn: str, player: str) -> dict:
    return {"action": "NOT_UNO", "turn": turn, "player": player}


def uno(player: str) -> dict:
    return {"action": "UNO", "player": player}


def card_played(card: dict, turn: str, player: str) -> dict:
    return {"action": card["type"], "player": player, "turn": turn, "pot": card}


def winner(player: str) -> dict:
    return {"action": "WINNER", "player": player}


def wildcard(player: str) -> dict:
    return {"action": "WILDCARD", "player": player}


def steal(cards: list) -> dict:
    return {"action": "STEAL", "cards": cards}


def steal_all() -> dict:
    return {"action": "STEAL"}


def take(turn: str, cards: list) -> dict:
    return {"action": "TAKE", "turn": turn, "cards": cards_deserializer(cards)}


def take_all(player: str, turn: str, length: int) -> dict:
    return {"action": "TAKE", "player": player, "turn": turn, "length": length}


def jump(player: str, turn: str) -> dict:
    return {"action": "JUMP", "player": player, "turn": turn}


def leave(player: str):
    return {"action": "PLAYER_LEFT", "player": player}


def next_turn(turn: str):
    return {"action": "NEXT_TURN", "turn": turn}


def change_color(color: str, turn: str):
    return {"action": "CHANGE_COLOR", "color": color, "turn": turn}
