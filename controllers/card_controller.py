from fastapi import APIRouter, status, Body
from typing import Annotated
from pony.orm import db_session
from view_entities.card_view_entities import PlayCard
from database.models.models import Match, Player, CardType
from database.dao.match_dao import get_player_turn, update_turn
from utils.match_utils import lobbys


card_controller = APIRouter()
