import logging

from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.protocol.message import BaseMessage, ChatSend


async def handler_chat_send(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
):
    """
    Handle an incoming message of the type ChatSend
    """
    msg_in = ChatSend.model_validate(message)
    logging.info(f"SERVER SEND -> {msg_in.model_dump_json()}")

    await manager.broadcast(msg_in)
