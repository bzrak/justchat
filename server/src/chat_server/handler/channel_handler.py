import logging

from chat_server.connection.context import ConnectionContext
from chat_server.protocol.message import BaseMessage, ChannelJoin, ChannelLeave


async def handle_channel_join(ctx: ConnectionContext, message: BaseMessage):
    """
    Handle incoming message from Channel Join
    """
    msg_in = ChannelJoin.model_validate(message)
    logging.info(f"SERVER SENDING -> {msg_in.model_dump_json()}")
    await ctx.channel_join(msg_in)


async def handle_channel_leave(ctx: ConnectionContext, message: BaseMessage):
    msg_in = ChannelLeave.model_validate(message)
    logging.info(f"SERVER SENDING -> {msg_in.model_dump_json()}")
    await ctx.channel_leave(msg_in)
