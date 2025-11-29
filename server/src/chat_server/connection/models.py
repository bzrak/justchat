import logging
from typing import TYPE_CHECKING

from fastapi import WebSocket
from pydantic import BaseModel, ValidationError

from chat_server.protocol.message import (
    ChannelJoin,
    ChannelLeave,
    ChatSend,
    Hello,
)

if TYPE_CHECKING:
    from chat_server.connection.manager import ConnectionManager


class ConnectionContext(BaseModel):
    # Required for WebSocket
    model_config = {"arbitrary_types_allowed": True}

    websocket: WebSocket
    id: int
    username: str | None = None
    channel_id: int | None = None
    manager: "ConnectionManager"

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

    async def chat_send(self, message: ChatSend):
        await self.manager.send_text_all(message.model_dump_json())

    async def channel_join(self, message: ChannelJoin):
        await self.manager.send_text_all(message.model_dump_json())

    async def channel_leave(self, message: ChannelLeave):
        await self.manager.send_text_all(message.model_dump_json())
