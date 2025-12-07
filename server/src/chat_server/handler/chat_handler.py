import logging

from pydantic import ValidationError

from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.protocol import client, server
from chat_server.protocol.message import BaseMessage


async def handler_chat_send(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
) -> None:
    """
    Handle an incoming message of the type ChatSend
    """
    try:
        msg_in = client.ChatSend.model_validate(message)
    except ValidationError:
        await manager.send_error(ctx.websocket, "Malformed message")
        return

    try:
        channel = manager.channel_srvc.get_channel_by_id(msg_in.payload.channel_id)
        sender = ctx.user.username

        if channel is None:
            await manager.send_error(ctx.websocket, "Channel does not exist.")
            logging.error(
                f"{repr(ctx.user)} attempted to send a message to a channel that does not exist: {msg_in.payload.channel_id}"
            )
            return

        response = server.ChatSend(
            timestamp=msg_in.timestamp,
            payload=server.ChatSendPayload(
                channel_id=channel.id,
                sender=sender,
                content=msg_in.payload.content,
            ),
        )
        logging.info(
            f"Server sending <{response.model_dump_json()}> to {repr(ctx.user)}"
        )

        # Validate if user is a member of the channel
        if not manager.channel_srvc.is_member(ctx.user, channel):
            logging.warning(
                f"{repr(ctx.user)} tried to send a message to channel {repr(channel)} without being a member."
            )
            await manager.send_error(
                ctx.websocket,
                "You must join this channel before sending messages",
            )
            return

        await manager.channel_srvc.send_to_channel(channel, response)
        logging.info(f"Message sent to channel {repr(channel)} by {repr(ctx.user)}")
    except Exception as e:
        logging.error(f"Error handling CHAT_SEND: {e}")
        await manager.send_error(ctx.websocket, "Failed to send message")
