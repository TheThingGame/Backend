from fastapi import HTTPException, status


INTERNAL_ERROR_CREATING_MATCH = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error creating the match.",
)


INVALID_MATCH_LENGTH = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The match name has to have between 3 and 16 characters.",
)


MATCH_EXISTS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The match name is already in use.",
)

NOT_EXISTENT_MATCH = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The match doesn't exist."
)

MATCH_ALREADY_STARTED = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="The match has already started."
)

MATCH_FULL = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The game you are trying to join is already full.",
)


NOT_CREATOR = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Only the creator can start the match."
)


NOT_ENOUGH_PLAYERS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The minimum amount of players hasn't been reached.",
)