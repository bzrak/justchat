import logging
from datetime import datetime
from uuid import uuid4

from chat_server.connection.channel import Channel
from chat_server.connection.context import ConnectionContext
from chat_server.connection.manager import ConnectionManager
from chat_server.handler.decorators import (
    require_channel,
    require_membership,
    require_permission,
    validate_message,
)
from chat_server.protocol.basemessage import BaseMessage
from chat_server.protocol.messages import KickCommand


@validate_message(KickCommand)
@require_channel
@require_membership
@require_permission("kick")
async def handler_kick(
    ctx: ConnectionContext,
    message: BaseMessage,
    manager: ConnectionManager,
    *,
    msg_in,  # require_channel
    channel: Channel,  # @require_membership
):
    """
    Handle kick command
    """
    try:
        # TODO: Check permission
        target = manager.channel_srvc.find_member_by_username(
            msg_in.payload.channel_id, msg_in.payload.target
        )

        if target:
            payload = msg_in.payload
            kick_msg = KickCommand(
                timestamp=datetime.now(), id=uuid4(), payload=payload
            )
            await manager.channel_srvc.send_to_channel(channel, kick_msg)
            await manager.channel_srvc.leave_channel(target, channel)
    except Exception as e:
        logging.error(f"Error handling CHAT_SEND: {e}")


async def handler_mute(
    ctx: ConnectionContext, message: BaseMessage, manager: ConnectionManager
):
    """
    Handle mute command
    """
    pass
