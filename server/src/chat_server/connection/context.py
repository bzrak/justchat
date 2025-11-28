from fastapi.websockets import WebSocket
from pydantic import BaseModel


class ConnectionMetadata(BaseModel):
    # Required for WebSocket
    model_config = {"arbitrary_types_allowed": True}

    websocket: WebSocket
    id: int
    username: str | None = None
    channel_id: int | None = None
