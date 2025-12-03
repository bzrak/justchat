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

        msg = server.ChatSend(
            timestamp=msg_in.timestamp,
            payload=server.ChatSendPayload(
                channel_id=msg_in.payload.channel_id,
                sender=ctx.user.username,
                content=msg_in.payload.content,
            ),
        )
        logging.info(f"Server sending <{msg.model_dump_json()}> to {repr(ctx.user)}")
        # FIX: It's possible to send messages while not being in the channel
        # TODO: Check authorization: if user can send message to that channel
        # or if actually is in the channel
        await manager.send_msg_to_channel(msg, msg_in.payload.channel_id)
    except ValidationError:
        await manager.send_error(ctx.websocket, "Malformed message")
    except Exception as e:
        logging.error(f"Couldn't process User <ChatSend>: {e}")
