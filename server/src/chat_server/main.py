from contextlib import asynccontextmanager
from fastapi import APIRouter, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect

from chat_server.api import auth
from chat_server.connection.manager import ConnectionManager
from chat_server.db.db import init_db
from chat_server.settings import get_settings

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} - {levelname} - ({filename}::{funcName}) - {message}",
    style="{",
    datefmt="%d-%m-%Y %H:%M",
)

settings = get_settings()

api_router = APIRouter()
api_router.include_router(auth.router)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Initializing Database.")
    await init_db()
    yield
    logging.info("Program Exit.")


# Create FastAPI app with settings
app = FastAPI(
    title="Chat Server API",
    version="0.1.0",
    debug=settings.is_development,
    lifespan=lifespan,
)

app.include_router(api_router)

origins = ["http://localhost:5173"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if settings.is_development else origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Chat Server API",
        "environment": settings.ENVIRONMENT,
    }


manager = ConnectionManager()


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await manager.connect(websocket)
        try:
            while True:
                data = await websocket.receive_text()
                await manager.handle_message(websocket, data)
        except WebSocketDisconnect:
            logging.info(f"Connection closed by the client: {websocket = }")
            await manager.disconnect(websocket)
    except WebSocketDisconnect:
        logging.info("Connection closed by the server: Invalid HELO initiaition")
