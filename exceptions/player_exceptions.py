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

PLAYER_NOT_IN_MATCH = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The player is not in the match."
)


NOT_CREATOR = HTTPException(
    status_code=status.HTTP_409_CONFLICT, detail="Only the creator can start the match."
)

CARD_NOT_FOUND = HTTPException(
    status_code=status.HTTP_404_NOT_FOUND, detail="The card does not exist."
)

UNPLAYED_STOLEN_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must play the card you just stole.",
)


INVALID_RESPONSE_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="Invalid response card.",
)


INVALID_PLAYED_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The played card is not valid.",
)


ALREADY_TOOK_CARD = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="The player has already taken a card from the deck and cannot do so again.",
)

INVALID_COLOR_CHANGE_EXCEPTION = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must play a Wildcard or Take Four Wildcard to change the color.",
)

INVALID_COLOR = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must play a card of the selected color.",
)


NO_COLOR_CHOSEN_BEFORE_PLAY = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must choose a color before making a play.",
)

NOT_A_PLAY_WAS_MADE = HTTPException(
    status_code=status.HTTP_409_CONFLICT,
    detail="You must draw a card from the deck before passing the turn.",
)
