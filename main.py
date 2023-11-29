from fastapi import FastAPI
from routers import chat_app
from starlette.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")

app.include_router(chat_app.router)