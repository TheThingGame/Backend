from fastapi import HTTPException, status


INTERNAL_ERROR_CREATING_PLAYER = HTTPException(
    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    detail="Internal error creating player.",
)

INVALID_PLAYER_LENGTH = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The player name has to have between 3 and 16 characters.",
)


PLAYER_EXISTS = HTTPException(
    status_code=status.HTTP_400_BAD_REQUEST,
    detail="The player name is already in use.",
)

NOT_EXISTS_PLAYER = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The player doesn't exist."
)


NOT_CREATOR = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Only the creator can start the match."
)
