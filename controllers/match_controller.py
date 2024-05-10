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
    play_card_update,
    steal_card_update,
)
from validators.match_validators import (
    new_match_validator,
    join_match_validator,
    start_match_validator,
    follow_match_validator,
    next_turn_validator,
    play_card_validator,
    steal_card_validator,
    change_color_validator,
)
from utils.match_utils import (
    LobbyManager,
    lobbys,
)
from view_entities.match_view_entities import (
    NewMatch,
    JoinMatch,
    MatchInfo,
    PlayCard,
    ChangeColor,
)
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
    cards = play_card_update(match_id, payload.player_id, card)
    # Si hay cartas significa que el jugador no canto 'UNO'
    if cards:
        actions.uno(match_id, cards)

    # Enviamos mensajes a los jugadores con la carta jugada
    await actions.play_card(match_id, card)

    return True


@match_controller.put("/steal-card/{match_id}", status_code=status.HTTP_200_OK)
async def steal_card(
    match_id: int,
    player_id: Annotated[int, Body(embed=True)],
    _=Depends(steal_card_validator),
):
    # Actualizamos la bd con la carta robada
    cards = steal_card_update(match_id, player_id)

    # Avisamos que se robo una carta
    await actions.steal_card(match_id, cards)

    return True


@match_controller.put("/next-turn/{match_id}", status_code=status.HTTP_200_OK)
async def next_turn(
    match_id: int,
    player_id: Annotated[int, Body(embed=True)],
    _=Depends(next_turn_validator),
):
    with db_session:
        state = Match[match_id].state.next_turn(1)
        state.acumulator = 0

    await actions.next_turn(match_id)

    return True


@match_controller.put("/change-color/{match_id}", status_code=status.HTTP_200_OK)
async def change_color(
    match_id: int,
    payload: ChangeColor,
    _=Depends(change_color_validator),
):
    with db_session:
        # Para el caso inicial no deberia pasar el turno
        # ACA HAY QUE HACER UN CAMBIO
        if state.color == CardColor.WILDCARD:
            state = Match[match_id].state.next_turn(1)
        state.color = payload.color

    # Avisamos a los jugadores del cambio de color
    await actions.change_color(match_id, payload.color)

    return True
