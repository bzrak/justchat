import logging

from chat_server.connection.context import ConnectionContext
from chat_server.handler import channel_handler, chat_handler
from chat_server.protocol.message import BaseMessage
from chat_server.protocol.enums import MessageType


HANDLERS = {
    MessageType.CHAT_SEND: chat_handler.handler_chat_send,
    MessageType.CHANNEL_JOIN: channel_handler.handle_channel_join,
}


async def dispatch(ctx: ConnectionContext, message: BaseMessage):
    """
    Route a Message to its appropriate Handler
    """

    handler = HANDLERS.get(message.type)
    logging.debug(
        f"Dispatch Handler: {handler.__name__ if handler else 'Unknown Handler'} "
    )

    if handler is None:
        # TODO: Return a message error or some exception. It will never happen
        # here since there are a verification done in manager.handle_message()
        logging.debug(f"Unknown Message Type: {message.type}. Payload: {message}")
        return

    await handler(ctx, message)
