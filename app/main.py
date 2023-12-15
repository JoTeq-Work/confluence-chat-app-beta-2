from contextlib import asynccontextmanager

from fastapi import FastAPI
from app.routers import chat_app
from fastapi.testclient import TestClient
from starlette.staticfiles import StaticFiles

from app.dependencies import start_chromadb

@asynccontextmanager
async def lifespan(app: FastAPI):
    global chroma_client
    print("Starting Chromadb")    
    chroma_client = start_chromadb()
    print("Chromadb started")
    yield


app = FastAPI(lifespan=lifespan)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# @app.on_event("startup")
# async def startup_event():
    # print("Starting Chromadb")
    # chroma_client = chromadb.HttpClient(
    #     host='localhost', 
    #     port=8000,
    #     settings=Settings(allow_reset=True)
    #     )
    # print("Chromadb started")

  
@app.get("/")
async def home():    
    print("Chroma Client", chroma_client)
    return {"Home": "Welcome to the Confluence Voice AI Chat App"}


    
def test_home():
    with TestClient(app) as client:
        response = client.get("/")
        assert response.status_code == 200
    
    
app.include_router(chat_app.router)