from fastapi import FastAPI
from routers import chat_app

app = FastAPI()

app.include_router(chat_app.router)