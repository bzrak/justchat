import logging

from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.protocol.message import BaseMessage, ChannelJoin, ChannelLeave


async def handle_channel_join(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
):
    """
    Handle incoming message from Channel Join
    """
    msg_in = ChannelJoin.model_validate(message)
    logging.info(f"SERVER SENDING -> {msg_in.model_dump_json()}")
    # TODO: Verify if user can join the channel.
    await manager.channel_join()


async def handle_channel_leave(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
):
    msg_in = ChannelLeave.model_validate(message)
    logging.info(f"SERVER SENDING -> {msg_in.model_dump_json()}")
    await manager.broadcast(msg_in)
