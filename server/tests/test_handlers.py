"""
Tests for the core chat handlers.

Tests verify that chatting functionality works:
- Joining channels
- Sending messages
- Leaving channels
"""

from datetime import datetime
from uuid import uuid4

import pytest

from chat_server.connection.context import ConnectionContext
from chat_server.handler.channel_handler import (
    handler_channel_join,
    handler_channel_leave,
)
from chat_server.handler.chat_handler import handler_chat_send
from chat_server.protocol.messages import (
    ChannelJoin,
    ChannelJoinPayload,
    ChannelLeave,
    ChannelLeavePayload,
    ChatSend,
    ChatSendPayload,
)


def make_context(websocket, user):
    """Create ConnectionContext bypassing Pydantic validation for mocks."""
    return ConnectionContext.model_construct(websocket=websocket, user=user)


class TestChannelJoinHandler:
    """Tests for handler_channel_join."""

    @pytest.mark.asyncio
    async def test_channel_join_creates_channel(
        self, mock_websocket, test_user, mock_manager, patched_session
    ):
        """User can join a channel that doesn't exist yet (creates it)."""
        ctx = make_context(mock_websocket, test_user)
        msg = ChannelJoin(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChannelJoinPayload(channel_id=1),
        )

        # Decorators will inject msg_in automatically
        await handler_channel_join(ctx, msg, mock_manager)

        # Verify channel was created
        mock_manager.channel_srvc.create_channel.assert_called_once()
        created_channel = mock_manager.channel_srvc.create_channel.call_args[0][0]
        assert created_channel.id == 1

    @pytest.mark.asyncio
    async def test_channel_join_adds_user_to_channel(
        self, mock_websocket, test_user, mock_manager, patched_session
    ):
        """User is added to the channel after joining."""
        ctx = make_context(mock_websocket, test_user)
        msg = ChannelJoin(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChannelJoinPayload(channel_id=1),
        )

        await handler_channel_join(ctx, msg, mock_manager)

        # Verify join_channel was called with correct user
        mock_manager.channel_srvc.join_channel.assert_called_once()
        call_args = mock_manager.channel_srvc.join_channel.call_args[0]
        assert call_args[0] == test_user  # First arg is user

    @pytest.mark.asyncio
    async def test_channel_join_no_history_sends_nothing(
        self, mock_websocket, test_user, mock_manager, patched_session
    ):
        """When channel has no history, no messages are sent to user."""
        ctx = make_context(mock_websocket, test_user)
        msg = ChannelJoin(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChannelJoinPayload(channel_id=999),
        )

        await handler_channel_join(ctx, msg, mock_manager)

        # broker.send_to_user should not be called (no history)
        mock_manager.broker.send_to_user.assert_not_called()


class TestChatSendHandler:
    """Tests for handler_chat_send."""

    @pytest.mark.asyncio
    async def test_chat_send_broadcasts_to_channel(
        self, mock_websocket, test_user, test_channel, mock_manager, patched_session
    ):
        """Message is broadcast to all channel members."""
        ctx = make_context(mock_websocket, test_user)
        msg = ChatSend(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChatSendPayload(channel_id=1, content="Hello, world!"),
        )

        # Mock decorator dependencies
        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.moderation.is_muted.return_value = False

        await handler_chat_send(ctx, msg, mock_manager)

        # Verify message was broadcast
        mock_manager.channel_srvc.send_to_channel.assert_called_once()
        call_args = mock_manager.channel_srvc.send_to_channel.call_args[0]
        assert call_args[0] == test_channel  # First arg is channel

    @pytest.mark.asyncio
    async def test_chat_send_includes_sender_info(
        self, mock_websocket, test_user, test_channel, mock_manager, patched_session
    ):
        """Broadcast message includes sender username."""
        ctx = make_context(mock_websocket, test_user)
        msg = ChatSend(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChatSendPayload(channel_id=1, content="Test message"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.moderation.is_muted.return_value = False

        await handler_chat_send(ctx, msg, mock_manager)

        # Get the broadcast message
        broadcast_msg = mock_manager.channel_srvc.send_to_channel.call_args[0][1]
        assert broadcast_msg.payload.sender.username == test_user.username

    @pytest.mark.asyncio
    async def test_chat_send_preserves_content(
        self, mock_websocket, test_user, test_channel, mock_manager, patched_session
    ):
        """Broadcast message contains the original content."""
        ctx = make_context(mock_websocket, test_user)
        content = "This is my test message content"
        msg = ChatSend(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChatSendPayload(channel_id=1, content=content),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.moderation.is_muted.return_value = False

        await handler_chat_send(ctx, msg, mock_manager)

        broadcast_msg = mock_manager.channel_srvc.send_to_channel.call_args[0][1]
        assert broadcast_msg.payload.content == content

    @pytest.mark.asyncio
    async def test_chat_send_channel_doesnt_exist(
        self, mock_websocket, test_user, mock_manager, patched_session
    ):
        """
        Ensure user can not send a message when the server doesn't exist and that the message was never sent to the channel.
        """
        ctx = make_context(mock_websocket, test_user)
        msg = ChatSend(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChatSendPayload(channel_id=1, content="Test"),
        )

        # Channel doesn't eist
        mock_manager.channel_srvc.get_channel_by_id.return_value = None

        await handler_chat_send(ctx, msg, mock_manager)

        # send_error was called
        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "Channel does not exist."
        )

        # Ensure no broadcast happened
        mock_manager.channel_srvc.send_to_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_chat_send_not_a_member_of_channel(
        self, mock_websocket, test_user, test_channel, mock_manager, patched_session
    ):
        """
        Ensure user can not send a message when not a member of the channel and that the message was never sent to the channel.
        """
        ctx = make_context(mock_websocket, test_user)
        msg = ChatSend(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChatSendPayload(channel_id=1, content="Test"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = False

        await handler_chat_send(ctx, msg, mock_manager)

        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "You must join this channel first"
        )

        # Ensure no broadcast happened
        mock_manager.channel_srvc.send_to_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_chat_send_muted(
        self, mock_websocket, test_user, test_channel, mock_manager, patched_session
    ):
        """
        Ensure user can not send a message when muted and that the message was never sent to the channel.
        """
        ctx = make_context(mock_websocket, test_user)
        msg = ChatSend(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChatSendPayload(channel_id=1, content="Test"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = False

        await handler_chat_send(ctx, msg, mock_manager)

        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "You must join this channel first"
        )

        # Ensure no broadcast happened
        mock_manager.channel_srvc.send_to_channel.assert_not_called()


class TestChannelLeaveHandler:
    """Tests for handler_channel_leave."""

    @pytest.mark.asyncio
    async def test_channel_leave_success(
        self, mock_websocket, test_user, test_channel, mock_manager
    ):
        """User successfully leaves a channel."""
        ctx = make_context(mock_websocket, test_user)
        msg = ChannelLeave(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChannelLeavePayload(channel_id=1),
        )

        # Mock decorator dependencies
        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True

        await handler_channel_leave(ctx, msg, mock_manager)

        # Verify leave was called
        mock_manager.channel_srvc.leave_channel.assert_called_once()
        call_args = mock_manager.channel_srvc.leave_channel.call_args[0]
        assert call_args[0] == test_user
        assert call_args[1] == test_channel

    @pytest.mark.asyncio
    async def test_channel_leave_calls_service_correctly(
        self, mock_websocket, test_user, test_channel, mock_manager
    ):
        """Leave handler delegates to channel service with correct arguments."""
        ctx = make_context(mock_websocket, test_user)
        msg = ChannelLeave(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChannelLeavePayload(channel_id=1),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True

        await handler_channel_leave(ctx, msg, mock_manager)

        # Verify the service method was called with user and channel objects
        mock_manager.channel_srvc.leave_channel.assert_awaited_once_with(
            test_user, test_channel
        )

    @pytest.mark.asyncio
    async def test_channel_leave_channel_doesnt_exist(
        self, mock_websocket, test_user, mock_manager, patched_session
    ):
        """
        Ensure there is no attempt to leave a channel that doesn't exist.
        """
        ctx = make_context(mock_websocket, test_user)
        msg = ChannelLeave(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChannelLeavePayload(channel_id=1),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = None

        await handler_channel_leave(ctx, msg, mock_manager)

        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "Channel does not exist."
        )

        # Ensure no broadcast happened
        mock_manager.channel_srvc.send_to_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_channel_leave_not_a_member_of_channel(
        self, mock_websocket, test_user, test_channel, mock_manager, patched_session
    ):
        """
        Ensure there is no attempt to leave a channel that the user is not a member of.
        """
        ctx = make_context(mock_websocket, test_user)
        msg = ChannelLeave(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChannelLeavePayload(channel_id=1),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = False

        await handler_channel_leave(ctx, msg, mock_manager)

        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "You must join this channel first"
        )

        # Ensure no broadcast happened
        mock_manager.channel_srvc.send_to_channel.assert_not_called()
