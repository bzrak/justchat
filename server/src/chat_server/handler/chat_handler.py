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
    logging.info(f"SERVER SEND -> {msg_in.model_dump_json()}")

    try:
        await websocket.send_text(msg_in.model_dump_json())
    except RuntimeError as e:
        # Connection already closed, ignore
        logging.warning(f"Failed to send message to closed connection: {e}")
