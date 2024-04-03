from fastapi import FastAPI
from controllers import match_controller

app = FastAPI()
app.include_router(match_controller.match_controller)
