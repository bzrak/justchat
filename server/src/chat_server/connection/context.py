import logging

from fastapi import WebSocket
from pydantic import BaseModel, ValidationError

from chat_server.protocol.message import Hello


class ConnectionContext(BaseModel):
    # Required for WebSocket
    model_config = {"arbitrary_types_allowed": True}

    websocket: WebSocket
    id: int
    username: str | None = None
    channel_id: int | None = None

    async def establish_connection(self) -> bool:
        helo = await self.websocket.receive_text()
        try:
            data = Hello.model_validate_json(helo)
            self.username = data.payload.username
            logging.info(f"Hello received from user: {self.username}")
            return True
        except ValidationError:
            logging.warning(f"Expected HELLO message. Got: {helo}")
            return False

