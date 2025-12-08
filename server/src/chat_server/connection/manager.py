import logging
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
from pydantic import ValidationError

from chat_server.connection.context import ConnectionContext
from chat_server.infrastructure.connection_registry import ConnectionRegistry
from chat_server.protocol import messages
from chat_server.protocol.basemessage import BaseMessage
from chat_server.protocol.enums import MessageType
from chat_server.services.authorization_service import (
    AuthenticationError,
    AuthenticationService,
)
from chat_server.services.channel_service import ChannelService

SERVER_ONLY_MESSAGES = {
    MessageType.CHANNEL_JOIN,
}


class ConnectionManager:
    """
    Manages WebSocket connections.
    """

    def __init__(
        self,
        connection_registry: ConnectionRegistry,
        # channel_manager: ChannelManager,
        auth_service: AuthenticationService,
        # membership_service: MembershipService,
        # message_broker: MessageBroker,
        channel_service: ChannelService,
    ) -> None:
        self.connections = connection_registry
        # self.channels = channel_manager
        self.auth = auth_service
        # self.membership = membership_service
        # self.broker = message_broker
        self.channel_srvc = channel_service

    async def accept_connection(self, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket connection.

        For the connection to be accepted it needs to send
        a proper message (HELLO) to the server.

        If invalid HELLO message raise a WebSocketDisconnect
        """

        await websocket.accept()

        # Wait for HELLO Message and
        # Validate the message received is a proper HELLO
        try:
            hello_msg = await websocket.receive_text()
            hello = messages.Hello.model_validate_json(hello_msg)
            logging.debug(f"{hello =}")
        except ValidationError as e:
            logging.warning(f"Invalid HELLO message {e}")
            await self.send_error(websocket, "Invalid HELLO message")
            await websocket.close(reason="Invalid HELLO message")
            raise WebSocketDisconnect

        # Authenticate User
        try:
            user = await self.auth.authenticate(hello.payload.token)
        except AuthenticationError as e:
            logging.warning(f"Authentication failed: {e}")
            await websocket.close(reason=str(e))
            raise WebSocketDisconnect

        payload = messages.HelloPayload(user=messages.UserFrom.model_validate(user))
        msg = messages.Hello(payload=payload)

        await websocket.send_text(msg.model_dump_json())

        # Register Connection
        ctx = ConnectionContext(websocket=websocket, user=user)
        self.connections.add(ctx)

        logging.info(f"Connection accepted: {repr(ctx)}")

    async def handle_disconnect(self, websocket: WebSocket) -> None:
        """
        Clean up for disconnect.
        """
        ctx = self.connections.remove(websocket)

        if ctx is None:
            logging.warning("Disconnect called for unknown connection")
            return

        # Leave all channels
        await self.channel_srvc.leave_all_channels(ctx.user)

        logging.info(f"Connection closed: {repr(ctx)}")

    async def send_error(self, websocket: WebSocket, detail: str) -> None:
        """
        Send error message to client.
        """
        payload = messages.ErrorMessagePayload(detail=detail)
        err = messages.ErrorMessage(payload=payload)
        await websocket.send_text(err.model_dump_json())

    async def handle_message(self, websocket: WebSocket, data: str) -> None:
        """
        Handle all the messages/data received from the client.
        """
        from chat_server.handler import router

        logging.info(f"Received: {data}")

        # Parse message
        msg = BaseMessage.from_json(data)

        if msg is None:
            logging.warning(f"Client sent a malformed data: {msg}")
            msg = BaseMessage.model_validate_json(data)

            await self.send_error(websocket, "Invalid message format")
            return

        ctx = self.connections.get_by_websocket(websocket)

        if ctx is None:
            logging.warning("Received message from connection without a Context")
            return

        await router.dispatch(ctx, msg, self)
