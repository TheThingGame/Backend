from deserializers.match_deserializers import cards_deserializer


def join_message(player_name: str):
    return {
        "action": "join",
        "player_name": player_name,
    }


def start_message(hand: list, pot: list, turn: str) -> dict:
    return {
        "action": "start",
        "data": {"hand": hand, "pot": pot, "turn": turn},
    }


def not_uno(cards: list, turn: str) -> dict:
    print("CARDS IN MESSAGE:", cards)

    cards_parse = cards_deserializer(cards)
    print("CARDS DESERIALIZER:", cards_parse)

    return {
        "action": "NOT_UNO",
        "cards": cards_parse,
        "turn": turn,
    }


def not_uno_broadcast(turn: str, player: str) -> dict:
    return {
        "action": "NOT_UNO",
        "turn": turn,
        "player": player,
    }


def card_played(card: dict, turn: str, player: str) -> dict:
    return {
        "action": card["type"],
        "player": player,
        "turn": turn,
        "pot": card,
    }


def winner(player: str) -> dict:
    return {
        "action": "WINNER",
        "player": player,
    }


def wildcard(player: str) -> dict:
    return {
        "action": "WILDCARD",
        "player": player,
    }


def take(turn: str, cards: list) -> dict:
    return {
        "action": "TAKE",
        "turn": turn,
        "cards": cards_deserializer(cards),
    }


def take_broadcast(action: str, player: str, turn: str) -> dict:
    return {
        "action": action,
        "player": player,
        "turn": turn,
    }


def jump(player: str, turn: str) -> dict:
    return {
        "action": "JUMP",
        "player": player,
        "turn": turn,
    }
