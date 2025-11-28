import logging

from chat_server.connection.context import ConnectionMetadata
from chat_server.handler import channel_handler, chat_handler
from chat_server.protocol.message import BaseMessage
from chat_server.protocol.enums import MessageType


HANDLERS = {
    MessageType.CHAT_SEND: chat_handler.handler_chat_send,
    MessageType.CHANNEL_JOIN: channel_handler.handle_channel_join,
}


async def dispatch(ctx: list[ConnectionMetadata], message: BaseMessage):
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

    for conns in ctx:
        await handler(conns.websocket, message)
