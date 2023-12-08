from fastapi import FastAPI
from app.routers import chat_app
from starlette.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(chat_app.router)