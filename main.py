from fastapi import FastAPI
from controllers import match_controller, card_controller

app = FastAPI()
app.include_router(match_controller.match_controller)
app.include_router(card_controller.card_controller)
