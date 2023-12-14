from fastapi import FastAPI
from app.routers import chat_app
from starlette.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
async def home():
    return {"Home": "Welcome to the Confluence Voice AI Chat App"}

app.include_router(chat_app.router)