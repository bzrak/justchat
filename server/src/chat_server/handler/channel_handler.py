import logging
from fastapi.websockets import WebSocket

from chat_server.protocol.message import BaseMessage, ChannelJoin


async def handle_channel_join(websocket: WebSocket, message: BaseMessage):
    """
    Handle incoming message from Channel Join
    """
    msg_in = ChannelJoin.model_validate(message)
    logging.info(f"SERVER SENDING -> {msg_in.model_dump_json()}")
    await websocket.send_text(msg_in.model_dump_json())
