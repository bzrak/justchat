import logging

from pydantic import ValidationError

from chat_server.connection.channel import Channel
from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.protocol import client
from chat_server.protocol.message import BaseMessage


async def handle_channel_join(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
) -> None:
    """
    Handle incoming message from Channel Join
    """

    try:
        msg_in = client.ChannelJoin.model_validate(message)
    except ValidationError:
        return await manager.send_error(ctx.websocket, "Malformed message")

    channel = Channel(
        id=msg_in.payload.channel_id, name=f"Channel {msg_in.payload.channel_id}"
    )

    manager.add_channel(channel)

    try:
        logging.info(f"Adding {repr(ctx.user)} to {repr(channel)}")
        # NOTE: Should the validation of the user joining a channel happen here
        # or in the subsmanager.add_user_to_channel?
        manager.subsmanager.add_user_to_channel(ctx.user, channel)

        # NOTE: Is this method send_channel_join() needed ?
        # Maybe the craft of the channel join message happen here
        # and make use of send_msg_to_channel()
        await manager.send_channel_join(ctx, channel)
    except ValueError:
        logging.info(
            f"Error adding {repr(ctx.user)} to {repr(channel)} because of Guest Account"
        )
        await manager.send_error(ctx.websocket, "Guest users can NOT join a Channel.")
    except Exception as e:
        logging.info(f"Error adding {repr(ctx.user)} to {repr(channel)}: {e}")
        await manager.send_error(ctx.websocket, "Error trying to join the channel.")
