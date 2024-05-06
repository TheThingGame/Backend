from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from controllers import match_controller

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(match_controller.match_controller)
