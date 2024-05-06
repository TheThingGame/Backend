import uuid
from pony.orm import db_session
from fastapi import APIRouter, status, WebSocket, WebSocketDisconnect, Body, Depends
from typing import Annotated
from database.models.models import Match, Player
from database.dao.player_dao import create_player_or_400
from database.dao.match_dao import (
    create_match_or_400,
    create_new_match,
    join_update,
    get_player_turn,
    update_turn,
    play_card_update,
    steal_card_update,
)

from validators.match_validators import (
    new_match_validator,
    join_match_validator,
    start_match_validator,
    follow_match_validator,
    pass_turn_validator,
    play_card_validator,
)
from utils.match_utils import (
    LobbyManager,
    lobbys,
)
from view_entities.match_view_entities import NewMatch, JoinMatch, MatchInfo, PlayCard
from deserializers.match_deserializers import match_deserializer, cards_deserializer
from websocket import messages, actions
from database.models.models import CARDS, CardType

match_controller = APIRouter()


@match_controller.post("/new-match", status_code=status.HTTP_201_CREATED)
async def create(match: NewMatch, _=Depends(new_match_validator)) -> MatchInfo:
    # Creamos el match
    match_id, creator_id = create_new_match(match.match_name, match.creator_name)

    # Creamos el manejador de conexiones para websockets
    lobbys[match_id] = LobbyManager()

    # Retornamos la info del match deserializada
    return match_deserializer(match_id, creator_id)


@match_controller.post("/join-match", status_code=status.HTTP_201_CREATED)
async def join(join: JoinMatch, _=Depends(join_match_validator)) -> MatchInfo:
    # Agregamos el jugador recien ingresado a la db
    match_id, player_id = join_update(join.player_name, join.code)

    # Avisamos a los jugadores presentes en el lobby que ingreso un nuevo jugador
    await lobbys[match_id].broadcast(messages.join_message(join.player_name))

    # Retornamos la info del match deserializada
    return match_deserializer(match_id, player_id)


@match_controller.websocket("/ws/follow-lobby/{match_id}")
async def follow_lobby(websocket: WebSocket, match_id: int, player_id: int):
    if not follow_match_validator(match_id, player_id):
        await websocket.close()
        return
    try:
        with db_session:
            player_name = Player[player_id].name
            await lobbys[match_id].connect(player_name, websocket)
        while True:
            await websocket.receive_text()

    except WebSocketDisconnect:
        return


@match_controller.put("/start-match/{match_id}", status_code=status.HTTP_200_OK)
async def start(
    player_id: Annotated[int, Body(embed=True)],
    match_id: int,
    _=Depends(start_match_validator),
):
    # Repartimos las cartas, creamos el mazo y pozo.
    with db_session:
        match = Match[match_id]
        match.start()

    # Enviamos un mensaje a cada jugador con su mano, carta inicial y turno actual
    await actions.start(match_id)

    return True


@match_controller.put("/play-card/{match_id}", status_code=status.HTTP_200_OK)
async def play_card(match_id: int, payload: PlayCard, _=Depends(play_card_validator)):
    card = cards_deserializer([payload.card_id])[0]

    # Actualizamos la bd en base a la carta jugada
    play_card_update(match_id, card)

    # Enviamos mensajes a los jugadores con la carta jugada
    await actions.play_card(match_id, card)

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


@match_controller.put("/steal-card/{match_id}", status_code=status.HTTP_200_OK)
async def steal_card(match_id: int, player_id: Annotated[int, Body(embed=True)]):
    steal_card_validator(match_id, player_id)

    message = steal_card_update(match_id, player_id)
    if message["action"] == "TAKE":
        await lobbys[match_id].send_personal_message(message, message["player"])
        del message["cards"]
        await lobbys[match_id].broadcast(message)
    else:
        await lobbys[match_id].send_personal_message(message, message["player"])
        del message["card"]
        await lobbys[match_id].broadcast(message)

    return True
