from fastapi import HTTPException


def throw(status, detail):
    raise HTTPException(status, detail)


# MATCH ERRORS
INTERNAL_ERROR_CREATING_MATCH = "INTERNAL_ERROR_CREATING_MATCH"
INVALID_MATCH_NAME_LENGTH = "INVALID_MATCH_NAME_LENGTH"
MATCH_EXISTS = "MATCH_EXISTS"
MATCH_NOT_EXISTENT = "NOT_EXISTENT_MATCH"
MATCH_ALREADY_STARTED = "MATCH_ALREADY_STARTED"
MATCH_FULL = "MATCH_FULL"
NOT_CREATOR = "NOT_CREATOR"
NOT_ENOUGH_PLAYERS = "NOT_ENOUGH_PLAYERS"
NOT_YOUR_TURN = "NOT_YOUR_TURN"


# PLAYER ERRORS
INTERNAL_ERROR_CREATING_PLAYER = "INTERNAL_ERROR_CREATING_PLAYER"
INVALID_PLAYER_NAME_LENGTH = "INVALID_PLAYER_NAME_LENGTH"
PLAYER_EXISTS = "PLAYER_EXISTS"
