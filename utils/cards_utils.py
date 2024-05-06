from fastapi import HTTPException, status


ALREADY_TOOK_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The player has already taken a card from the deck and cannot do so again.",
)


INVALID_COLOR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must play a card of the selected color.",
)


COLOR_REQUIRED_FOR_WILDCARDS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="To play a Wildcard or Take Four Wildcard, you must specify a color.",
)
