from fastapi import WebSocket
from pydantic import BaseModel


class ConnectionContext(BaseModel):
    # Required for WebSocket
    model_config = {"arbitrary_types_allowed": True}

    websocket: WebSocket
    id: int
    username: str
    channel_id: int | None = None
