import logging

from fastapi.websockets import WebSocket
from chat_server.protocol.enums import MessageType
from chat_server.protocol.message import BaseMessage, ChatSend


async def handler_chat_send(websocket: WebSocket, message: BaseMessage):
    """
    Handle an incoming message of the type ChatSend
    """
    msg_in = ChatSend.model_validate(message)
    msg_in.type = MessageType.CHAT_BROADCAST
    logging.debug(f"Sending: {msg_in.model_dump_json()}")
    await websocket.send_text(msg_in.model_dump_json())
