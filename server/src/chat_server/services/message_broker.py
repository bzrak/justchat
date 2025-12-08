import logging
from fastapi import WebSocket
from chat_server.connection.channel import Channel
from chat_server.connection.user import User
from chat_server.infrastructure.connection_registry import ConnectionRegistry
from chat_server.protocol.basemessage import BaseMessage
from chat_server.services.membership_service import MembershipService


class MessageBroker:
    """
    Broker for routing messages to WebSocket connections.
    """

    def __init__(self, connection_registry: ConnectionRegistry) -> None:
        self._registry = connection_registry

    async def send_to_websocket(
        self, websocket: WebSocket, message: BaseMessage
    ) -> None:
        """
        Send a message to a specific WebSocket.
        """
        try:
            await websocket.send_text(message.model_dump_json())
            logging.debug(f"Sent message to websocket: {message}")
        except Exception as e:
            ctx = self._registry.get_by_websocket(websocket)
            logging.error(f"Failed to send message to {repr(ctx.user)}: {e}")

    async def send_to_user(self, user_to: User, message: BaseMessage) -> None:
        """
        Send a message to a User.
        """
        ctx = self._registry.get_by_user(user_to)

        if ctx is None:
            logging.warning(f"Cannot send message to {repr(user_to)}: Not connected")
            return

        await self.send_to_websocket(ctx.websocket, message)

    async def send_to_channel(self, members: set[User], message: BaseMessage) -> None:
        """
        Send a message to all members in a channel.
        """
        for user in members:
            await self.send_to_user(user, message)

    # NOTE: send_broadcast() ?
    # connections = self._registry.get_all()
