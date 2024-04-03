from fastapi import APIRouter, status, Response
from view_entities.match_view_entities import NewMatch
from validators.match_validators import new_match_validator
from database.dao.match_dao import create_new_match
from utils.match_utils import ERROR_CREATING_MATCH, LobbyManager, lobbys
from database.models.models import Match
from database.dao.match_dao import get_match_by_name_and_user, get_all_matches

match_controller = APIRouter()


@match_controller.post("/new-match", status_code=status.HTTP_201_CREATED)
async def create_match(new_match: NewMatch):
    new_match_validator(new_match)
    created_match = create_new_match(new_match)

    match_id = get_match_by_name_and_user(
        new_match.name, new_match.creator_player
    ).match_id

    lobbys[match_id] = LobbyManager()

    return {"match_id": match_id}


@match_controller.get("/matches/")
async def get_matches():
    matches = get_all_matches()
    return matches
