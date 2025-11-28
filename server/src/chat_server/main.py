from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.websockets import WebSocketDisconnect
from sqlalchemy.ext.asyncio import create_async_engine

from chat_server.connection.manager import ConnectionManager
from chat_server.settings import get_settings

import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="{asctime} - {levelname} - ({filename}::{funcName}) - {message}",
    style="{",
    datefmt="%d-%m-%Y %H:%M",
)

settings = get_settings()

# Create FastAPI app with settings
app = FastAPI(
    title="Chat Server API",
    version="0.1.0",
    debug=settings.is_development,
)


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
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await manager.handle_message(data)

    except WebSocketDisconnect:
        await manager.disconnect(websocket)
        await manager.broadcast_message("User has left the chat")


# async_engine = create_async_engine(
#     settings.async_database_url,
#     pool_size=settings.DB_POOL_SIZE,
#     max_overflow=settings.DB_MAX_OVERFLOW,
# )
async_engine = create_async_engine(settings.async_database_url)
