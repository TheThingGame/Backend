from fastapi import HTTPException, status

PLAYER_DB_EXCEPTION = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error when creating the new player in the database.",
)


NOT_EXISTENT_PLAYER = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The player doesn't exist."
)


NOT_YOUR_TURN = HTTPException(
    status_code=status.HTTP_403_FORBIDDEN, detail="It's not your turn to play a card."
)
