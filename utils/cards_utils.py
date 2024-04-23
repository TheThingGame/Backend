from fastapi import HTTPException, status

INVALID_PLAYED_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The played card is not valid.",
)

CARD_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The card does not exist."
)

ALREADY_TOOK_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The player has already taken a card from the deck and cannot do so again.",
)


INVALID_RESPONSE_CARD_TYPE = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Invalid card type for response. Must be TAKE_FOUR_WILDCARD.",
)


UNPLAYED_STOLEN_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must play the card you just stole.",
)


INVALID_COLOR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must play a card of the selected color.",
)


COLOR_REQUIRED_FOR_WILDCARDS = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="To play a Wildcard or Take Four Wildcard, you must specify a color.",
)
