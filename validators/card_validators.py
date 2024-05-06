""" @db_session
def steal_card_validator(match_id: int, player_id: int):
    # Chequeamos si la partida existe
    match = get_match_by_id(match_id)
    if not match:
        raise NOT_EXISTENT_MATCH

    # Chequeamos si el jugador existe
    player = Player.get(player_id=player_id, match=match)
    if not player:
        raise NOT_EXISTENT_PLAYER

    # Chequeamos si es el turno del jugador
    current_turn = get_player_turn(match_id)
    if current_turn != player.name:
        raise NOT_YOUR_TURN

    # Chequeamos que el jugador no vuelva a robar otra carta si ya lo hizo
    if player.stolen_card:
        raise ALREADY_TOOK_CARD
 """
