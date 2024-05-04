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
