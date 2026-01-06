import logging

from pydantic import ValidationError

from chat_server.db.db import async_session
from chat_server.db import crud
from chat_server.connection.channel import Channel
from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.protocol.basemessage import BaseMessage
from chat_server.protocol.messages import (
    ChannelJoin,
    ChatSend,
    ChatSendPayload,
    UserFrom,
)


logger = logging.getLogger(__name__)


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

    channel_response = Channel(
        id=msg_in.payload.channel_id, name=f"Channel {msg_in.payload.channel_id}"
    )

    try:
        manager.channel_srvc.create_channel(channel_response)

        # Send previous messages
        # HACK: Not really beautiful
        async with async_session() as session:
            history_messages = await crud.get_channel_messages(
                session, msg_in.payload.channel_id
            )
            print(f"{history_messages = }")
        if history_messages is not None:
            for history_msg in history_messages:
                payload = ChatSendPayload(
                    channel_id=history_msg.channel_id,
                    sender=UserFrom(username=history_msg.sender_username),
                    content=history_msg.content,
                )
                history_send = ChatSend(
                    timestamp=history_msg.timestamp, id=history_msg.id, payload=payload
                )
                await manager.broker.send_to_user(ctx.user, history_send)

        await manager.channel_srvc.join_channel(ctx.user, channel_response)
        logging.info(f"{repr(ctx.user)} joined {repr(channel_response)}")
    except Exception as e:
        logging.info(f"Error adding {repr(ctx.user)} to {repr(channel_response)}: {e}")
        await manager.send_error(ctx.websocket, "Error trying to join the channel.")
