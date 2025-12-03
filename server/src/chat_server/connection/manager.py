from datetime import datetime
import logging
from fastapi import WebSocket
from fastapi.websockets import WebSocketDisconnect
import jwt
from pydantic import ValidationError

from chat_server.connection.channel import Channel
from chat_server.connection.context import ConnectionContext
from chat_server.connection.user import User
from chat_server.db import crud
from chat_server.db.db import async_session
from chat_server.protocol import client, server
from chat_server.protocol.enums import MessageType
from chat_server.protocol.message import BaseMessage, ErrorMessage
from chat_server.security.utils import ALGORITHM
from chat_server.settings import get_settings

SERVER_ONLY_MESSAGES = {
    MessageType.CHANNEL_JOIN,
}


class ConnectionManager:
    """
    Manages WebSocket connections.
    """

    def __init__(self) -> None:
        self.active_connections: dict[WebSocket, ConnectionContext] = {}
        self.connections_by_user_id: dict[int, ConnectionContext] = {}
        self.subsmanager = SubscriptionManager()

        # Map a Channel ID to its own Channel for fast lookups
        self._channels: dict[int, Channel] = {}

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept and register a new WebSocket connection.

        If invalid connection raise a WebSocketDisconnect
        """

        await websocket.accept()

        helo = await websocket.receive_text()

        # Validate the message received
        try:
            data = client.Hello.model_validate_json(helo)
        except ValidationError:
            logging.warning(f"Expected HELLO message. Got: {helo}")
            await websocket.close(reason="Invalid HELLO")
            raise WebSocketDisconnect

        # Check if there is a JWT token in the HELLO message
        access_token = data.payload.token
        if not access_token:
            # Handle Guest User
            logging.debug(f"No Access Access Token in Payload: {access_token =}")
            user_db = User(username=data.payload.username)
            conn_data = ConnectionContext(websocket=websocket, user=user_db)
        else:
            # Handle Authenticated User
            logging.debug(f"Access Token in Payload: {access_token =}")
            try:
                token = jwt.decode(
                    access_token,
                    get_settings().SECRET_KEY,
                    algorithms=[ALGORITHM],
                )
                logging.debug(f"Token Decoded: {token =}")
                user_id = token.get("sub")

                # Verify user exists in database
                async with async_session() as session:
                    user_db = await crud.get_user_by_id(session, user_id)
                    if not user_db:
                        await websocket.close(reason="User does not exist")
                        raise WebSocketDisconnect

                user = User(id=user_db.id, username=user_db.username)
                conn_data = ConnectionContext(websocket=websocket, user=user)
            except Exception as e:
                logging.warning(f"Invalid authentication: {e}")
                await websocket.close(reason="Authentication failed")
                raise WebSocketDisconnect

            logging.info(f"Created ConnectionContext: {conn_data}")
            self.active_connections[websocket] = conn_data
            self.connections_by_user_id[user.id] = conn_data

    def get_connection(self, websocket: WebSocket) -> "ConnectionContext | None":
        """
        Get the ConnectionContext for a given WebSocket.
        """
        return self.active_connections.get(websocket)

    def get_connection_by_user_id(self, user_id: int) -> "WebSocket | None":
        """
        Get the ConnectionContext for a given ID.
        """
        user = self.connections_by_user_id.get(user_id)
        return user.websocket if user else None

    def add_channel(self, channel: Channel):
        """
        Add a channel
        """
        self._channels[channel.id] = channel

    def get_channel(self, channel_id: int) -> Channel:
        """
        Get a channel using its ID
        """
        return self._channels[channel_id]

    async def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a WebSocket connection from active connections.
        """
        if websocket in self.active_connections:
            ctx = self.active_connections.pop(websocket)
            # self.connections_by_id.pop(conn.id, None)

            logging.info(f"<{ctx.user.username}> has disconnected.")

            await self.send_channel_leave(ctx)

    async def send_error(self, websocket: WebSocket, msg: str) -> None:
        err = ErrorMessage(detail=msg)
        await websocket.send_text(err.model_dump_json())

    async def handle_message(self, websocket: WebSocket, data: str) -> None:
        """
        Handle the message received by client appropriately
        """
        from chat_server.handler import router

        logging.info(f"CLIENT SENT: {data}")
        msg = BaseMessage.from_json(data)
        if msg is None:
            logging.warning("Client sent a malformed data.")
            msg = BaseMessage.model_validate_json(data)
            logging.debug(f"{msg =}")
            if msg.type in SERVER_ONLY_MESSAGES:
                conn = self.get_connection(websocket)
                logging.warning(
                    f"Client attempted to send server-only message: <{conn.user}> "
                )
            await self.send_error(websocket, "Invalid message type")
            return

        ctx = self.get_connection(websocket)
        if ctx is not None:
            await router.dispatch(ctx, msg, self)
        else:
            logging.warning("Received message from unknown connection")

    async def broadcast(self, message: BaseMessage) -> None:
        msg_str = message.model_dump_json()

        for conn in self.active_connections:
            try:
                await conn.send_text(msg_str)
            except Exception as e:
                logging.error(
                    f"Error sending message to {self.active_connections.get(conn).user}: {e}"
                )

    async def send_msg_to_channel(self, message: BaseMessage, channel_id: int) -> None:
        channel = self.get_channel(channel_id)
        # Retrieve all users that is in the channel
        users_id_in_channel = self.subsmanager.get_users_in_channel(channel)

        for user_id in users_id_in_channel:
            conn = self.get_connection_by_user_id(user_id)
            if conn:
                await conn.send_text(message.model_dump_json())
            else:
                logging.error(f"Couldn't send message to UserID: {user_id}")

    async def send_channel_join(self, ctx: ConnectionContext, channel: Channel) -> None:
        payload = server.ChannelJoinPayload(
            username=ctx.user.username, channel_id=channel.id
        )
        join_msg = server.ChannelJoin(timestamp=datetime.now(), payload=payload)

        await self.send_msg_to_channel(join_msg, channel.id)

    async def send_channel_leave(self, ctx: ConnectionContext) -> None:
        timestamp = datetime.now()

        logging.info(
            f"{repr(ctx.user)} has left the channels: {self.subsmanager.get_channels_id_from_user(ctx.user)}"
        )
        for channel_id in self.subsmanager.get_channels_id_from_user(ctx.user):
            self.subsmanager.remove_user_from_channel(ctx.user, channel_id)

            payload = server.ChannelLeavePayload(
                username=ctx.user.username, channel_id=channel_id
            )
            leave_msg = server.ChannelLeave(timestamp=timestamp, payload=payload)
            await self.send_msg_to_channel(leave_msg, channel_id)


class SubscriptionManager:
    """
    Manage the User and Channel relation. Keep track of "who" is connected to "where".
    """

    def __init__(self) -> None:
        # Maps Channel_ID to a Set of User_ID
        self._channel_members: dict[int, set[int]] = {}
        # Maps User_ID to a set of Channel_ID
        self._user_channels: dict[int, set[int]] = {}

    def add_user_to_channel(self, user: User, channel: Channel):
        """
        Add a User to a Channel
        """

        if not user.id:
            raise ValueError("Guest users can not join a channel.")
        logging.info(f"Subscribing {repr(user)} to {repr(channel)}")
        if channel.id not in self._channel_members:
            # Initialize
            self._channel_members[channel.id] = set()
        if user.id not in self._user_channels:
            # Initialize
            self._user_channels[user.id] = set()

        self._channel_members[channel.id].add(user.id)
        self._user_channels[user.id].add(channel.id)
        logging.debug(f"{self._channel_members = }")
        logging.debug(f"{self._user_channels = }")

    def remove_user_from_channel(self, user: User, channel_id: int):
        """
        Remove a User from a Channel
        """
        logging.info(f"Removing {repr(user)} from {repr(channel_id)}")

        self._channel_members[channel_id].remove(user.id)

    def get_users_in_channel(self, channel: Channel) -> set[int]:
        """
        Retrieve all Users ID connected to a Channel.
        Returns empty set if channel has no members.
        """
        return self._channel_members.get(channel.id, set())

    def get_channels_id_from_user(self, user: User) -> set[int]:
        """
        Retrieve all channels a User is connected to.
        Returns empty set if user hasn't joined any channels.
        """
        logging.debug(f"{self._user_channels = }")
        return self._user_channels.get(user.id, set())
