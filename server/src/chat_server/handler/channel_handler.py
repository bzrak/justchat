import logging

from pydantic import ValidationError

from chat_server.connection.channel import Channel
from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.protocol.basemessage import BaseMessage
from chat_server.protocol.messages import ChannelJoin


async def handler_channel_join(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
) -> None:
    """
    Handle incoming message from Channel Join
    """

    try:
        msg_in = ChannelJoin.model_validate(message)
    except ValidationError:
        await manager.send_error(ctx.websocket, "Malformed message")
        return

    channel = Channel(
        id=msg_in.payload.channel_id, name=f"Channel {msg_in.payload.channel_id}"
    )

    try:
        manager.channel_srvc.create_channel(channel)
        await manager.channel_srvc.join_channel(ctx.user, channel)
        logging.info(f"{repr(ctx.user)} joined {repr(channel)}")
    except Exception as e:
        logging.info(f"Error adding {repr(ctx.user)} to {repr(channel)}: {e}")
        await manager.send_error(ctx.websocket, "Error trying to join the channel.")
