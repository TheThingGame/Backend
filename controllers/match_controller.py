import uuid
from pony.orm import db_session
from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect, Body
from typing import Annotated
from database.models.models import Match, Player
from database.dao.match_dao import (
    create_new_match,
    update_joining_user_match,
    get_all_matches,
    update_executed_match,
    get_match_info,
    get_player_turn,
    update_turn,
)
from database.dao.card_dao import card_db_to_dict
from validators.match_validators import (
    new_match_validator,
    join_match_validator,
    start_match_validator,
    follow_match_validator,
    pass_turn_validator,
)
from utils.match_utils import (
    INTERNAL_ERROR_CREATING_MATCH,
    INTERNAL_ERROR_UPDATING_MATCH_INFO,
    LobbyManager,
    lobbys,
)
from view_entities.match_view_entities import NewMatch, JoinMatch, MatchInfo


match_controller = APIRouter()


@match_controller.post("/new-match", status_code=status.HTTP_201_CREATED)
async def create_match(new_match: NewMatch) -> MatchInfo:
    # Validamos los datos del cuerpo de solicitud
    new_match_validator(new_match)

    # Generamos el codigo para unirse a la partida
    code = str(uuid.uuid4())[:3]

    # Creamos el lobby
    match_id = create_new_match(new_match.name, new_match.creator_player, code).match_id

    # Creamos el manejador de conexiones para websockets
    lobbys[match_id] = LobbyManager()

    # Obtenemos informacion del lobby parseada
    match_info: MatchInfo = get_match_info(match_id, new_match.creator_player)

    return match_info


@match_controller.post("/join-match", status_code=status.HTTP_201_CREATED)
async def join_match(join_match: JoinMatch) -> MatchInfo:
    # Validar los datos del cuerpo de solicitud
    match_id = join_match_validator(join_match)

    # Agregamos el jugador recien ingresado, a la DB
    if not update_joining_user_match(match_id, join_match.player_name):
        raise INTERNAL_ERROR_UPDATING_MATCH_INFO

    # Avisamos a los jugadores presentes en el lobby que ingreso un nuevo jugador
    message_to_broadcast = {
        "action": "join",
        "data": {
            "new_player": join_match.player_name,
        },
    }
    await lobbys[match_id].broadcast(message_to_broadcast)

    # Obtenemos la informacion del lobby parseada
    match_info = get_match_info(match_id, join_match.player_name)

    return match_info


@match_controller.websocket("/ws/follow-lobby/{match_id}")
async def follow_lobby(websocket: WebSocket, match_id: int, player_id: int):
    if not follow_match_validator(match_id, player_id):
        await websocket.close()
        return

    await lobbys[match_id].connect(player_id, websocket)
    while True:
        try:
            await websocket.receive_text()
        except WebSocketDisconnect:
            return


@match_controller.put("/start-match/{match_id}", status_code=status.HTTP_200_OK)
async def start_match(player_id: Annotated[int, Body(embed=True)], match_id: int):
    start_match_validator(player_id, match_id)

    # Actualizamos la partida
    if not update_executed_match(match_id):
        raise INTERNAL_ERROR_UPDATING_MATCH_INFO

    with db_session:
        match = Match[match_id]
        pot = card_db_to_dict(match.pot.last_played_card)
        turn = get_player_turn(match_id)
        deck = [card_db_to_dict(c) for c in match.deck]

        # Avisamos a los jugadores que la partida inicio, le pasamos su mano, el pozo y el turno actual
        for p in match.players:
            hand = []
            for c in p.hand:
                hand.append(card_db_to_dict(c))

            message_to_player = {
                "action": "start",
                "data": {"hand": hand, "pot": pot, "deck": deck, "turn": turn},
            }
            # Avisamos a cada jugador que la partida inicio, le pasamos su mano, la carta inicial del pozo y el turno actual
            await lobbys[match_id].send_personal_message(message_to_player, p.player_id)
    return True


@match_controller.put("/pass-turn/{match_id}", status_code=status.HTTP_200_OK)
async def pass_turn(match_id: int, player_id: Annotated[int, Body(embed=True)]):
    pass_turn_validator(match_id, player_id)
    with db_session:
        player = Player[player_id]
        match = Match[match_id]

        player.stolen_card = None
        update_turn(
            match,
            match.current_player_index,
            match.turn_direction,
            len(match.players),
        )
        player_turn = get_player_turn(match_id)

        message_to_broadcast = {
            "action": "PASS_TURN",
            "turn": player_turn,
        }
        await lobbys[match_id].broadcast(message_to_broadcast)

    return True


@match_controller.get("/matches/")
async def get_matches():
    matches = get_all_matches()
    return matches
