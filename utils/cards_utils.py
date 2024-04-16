from fastapi import HTTPException

INVALID_PLAYED_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The played card is not valid.",
)

CARD_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The card does not exist"
)
