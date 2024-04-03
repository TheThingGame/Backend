from fastapi import HTTPException, status
from view_entities.match_view_entities import NewMatch
from database.dao.match_dao import get_match_by_name_and_user


def new_match_validator(new_match: NewMatch):
    match = get_match_by_name_and_user(new_match.name, new_match.creator_player)
    errors = []

    if len(new_match.name) < 3 or len(new_match.name) > 16:
        errors.append("The match name has to have between 3 and 16 characters.")

    if len(new_match.password) > 16:
        errors.append("The password can't have more than 16 characters.")

    if match:
        errors.append(
            "A match with the same name or a player with the same name already exists."
        )

    if errors:
        detail = "\n".join(errors)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)
