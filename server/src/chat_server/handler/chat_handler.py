from datetime import datetime
import logging
import uuid

from pydantic import ValidationError

from chat_server.db.db import async_session
from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.db import crud
from chat_server.protocol.enums import MessageType
from chat_server.protocol.messages import (
    ChatSend,
    ChatSendPayload,
    ReactAdd,
    ReactPayload,
    ReactRemove,
    UserFrom,
)
from chat_server.protocol.basemessage import BaseMessage

# TODO: Too many code duplicated here


async def handler_chat_send(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
) -> None:
    """
    Handle an incoming message of the type ChatSend
    """
    try:
        msg_in = ChatSend.model_validate(message)
    except ValidationError:
        await manager.send_error(ctx.websocket, "Malformed message")
        return

    try:
        channel = manager.channel_srvc.get_channel_by_id(msg_in.payload.channel_id)

        if channel is None:
            await manager.send_error(ctx.websocket, "Channel does not exist.")
            logging.error(
                f"{repr(ctx.user)} attempted to send a message to a channel that does not exist: {msg_in.payload.channel_id}"
            )
            return

        response_payload = ChatSendPayload(
            channel_id=channel.id,
            sender=UserFrom.model_validate(ctx.user),
            content=msg_in.payload.content,
        )

        server_response = ChatSend(
            timestamp=datetime.now(), id=uuid.uuid4(), payload=response_payload
        )

        logging.info(
            f"Server sending <{server_response.model_dump_json()}> to {repr(ctx.user)}"
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

        # Save message to database
        async with async_session() as session:
            await crud.create_message(session, server_response)

        await manager.channel_srvc.send_to_channel(channel, server_response)
        logging.info(f"Message sent to channel {repr(channel)} by {repr(ctx.user)}")
    except Exception as e:
        logging.error(f"Error handling CHAT_SEND: {e}")
        await manager.send_error(ctx.websocket, "Failed to send message")


async def handler_chat_react(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
):
    """
    Handles add/remove reactions to messages
    """
    try:
        msg_in = ReactAdd.model_validate(message)
    except ValidationError:
        # FIX: I think this code never happens
        try:
            msg_in = ReactRemove.model_validate(message)
        except ValidationError:
            await manager.send_error(ctx.websocket, "Malformed message")
        return

    channel = manager.channel_srvc.get_channel_by_id(msg_in.payload.channel_id)

    if channel is None:
        await manager.send_error(ctx.websocket, "Channel does not exist.")
        logging.error(
            f"{repr(ctx.user)} attempted to send a message to a channel that does not exist: {msg_in.payload.channel_id}"
        )
        return

    # FIX: Does this message even exist ? How to check
    # if the message_id exists?
    # Also, how to block the user from sending many react add ?
    payload = ReactPayload(
        emote=msg_in.payload.emote,
        message_id=msg_in.payload.message_id,
        channel_id=channel.id,
    )

    if msg_in.type is MessageType.REACT_ADD:
        response = ReactAdd(timestamp=datetime.now(), id=uuid.uuid4(), payload=payload)
    else:
        response = ReactRemove(
            timestamp=datetime.now(), id=uuid.uuid4(), payload=payload
        )

    # Validate if user is a member of the channel
    if not manager.channel_srvc.is_member(ctx.user, channel):
        logging.warning(
            f"{repr(ctx.user)} tried to send a reaction to channel {repr(channel)} without being a member."
        )
        await manager.send_error(
            ctx.websocket,
            "You must join this channel before reacting messages",
        )
        return
    await manager.channel_srvc.send_to_channel(channel, response)
