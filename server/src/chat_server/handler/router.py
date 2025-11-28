import logging

from fastapi.websockets import WebSocket
from chat_server.handler import chat_handler
from chat_server.protocol.message import BaseMessage
from chat_server.protocol.enums import MessageType


HANDLERS = {
    MessageType.CHAT_SEND: chat_handler.handler_chat_send,
}


async def dispatch(websockets: list[WebSocket], message: BaseMessage):
    """
    Route a Message to its appropriate Handler
    """

    handler = HANDLERS.get(message.type)
    logging.debug(
        f"Dispatch Handler: {handler.__name__ if handler else 'Unknown Handler'} "
    )

    if handler is None:
        # TODO: Return a message error or some exception
        logging.debug(f"Unknown Message Type: {message.type}. Payload: {message}")
        return

    for websocket in websockets:
        await handler(websocket, message)
