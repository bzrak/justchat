import logging

from chat_server.connection.channel import Channel
from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.protocol import client
from chat_server.protocol.message import BaseMessage


async def handle_channel_join(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
):
    """
    Handle incoming message from Channel Join
    """
    msg_in = client.ChannelJoin.model_validate(message)
    logging.debug(f"SERVER SENDING -> {msg_in.model_dump_json()}")
    # TODO: Verify if user can join the channel.
    channel = Channel(
        id=msg_in.payload.channel_id, name=f"Channel {msg_in.payload.channel_id}"
    )
    manager.add_channel(channel)
    logging.info(f"Created {repr((channel))}")
    try:
        logging.info(f"Adding {repr(ctx.user)} to {repr(channel)}")
        manager.subsmanager.add_user_to_channel(ctx.user, channel)
        await manager.send_channel_join(ctx, channel)
    except Exception as e:
        logging.info(f"Error adding {repr(ctx.user)} to {repr(channel)}: {e}")
        await manager.send_error(ctx.websocket, "Error trying to join the channel.")
