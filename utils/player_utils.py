from fastapi import HTTPException, status

PLAYER_DB_EXCEPTION = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error when creating the new player in the database.",
)


PLAYER_EXISTS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The player name is already in use.",
)


NOT_EXISTENT_PLAYER = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The player doesn't exist."
)


NOT_YOUR_TURN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="It's not your turn to play a card."
)


NOT_A_PLAY_WAS_MADE = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must draw a card from the deck before passing the turn.",
)
