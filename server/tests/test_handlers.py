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
from chat_server.handler.commands_handler import (
    handler_kick,
    handler_mute,
    handler_unmute,
)
from chat_server.protocol.messages import (
    ChannelJoin,
    ChannelJoinPayload,
    ChannelLeave,
    ChannelLeavePayload,
    ChatSend,
    ChatSendPayload,
    KickCommand,
    KickCommandPayload,
    MuteCommand,
    MuteCommandPayload,
    UnMuteCommand,
    UnMuteCommandPayload,
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
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.moderation.is_muted.return_value = True

        await handler_chat_send(ctx, msg, mock_manager)

        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "You are muted in this channel."
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


class TestKickHandler:
    """Tests for handler_kick."""

    @pytest.mark.asyncio
    async def test_kick_success(
        self, mock_websocket, test_user, test_channel, target_user, mock_manager
    ):
        """Target is removed from channel and kick broadcast sent."""
        ctx = make_context(mock_websocket, test_user)
        msg = KickCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=KickCommandPayload(channel_id=1, target="victim", reason="spam"),
        )

        # Decorator dependencies
        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.channel_srvc.find_member_by_username.return_value = target_user

        await handler_kick(ctx, msg, mock_manager)

        # Verify kick was broadcast
        mock_manager.channel_srvc.send_to_channel.assert_called_once()
        # Verify target was removed from channel
        mock_manager.channel_srvc.leave_channel.assert_awaited_once_with(
            target_user, test_channel
        )

    @pytest.mark.asyncio
    async def test_kick_target_not_found(
        self, mock_websocket, test_user, test_channel, mock_manager
    ):
        """No action when target username doesn't exist."""
        ctx = make_context(mock_websocket, test_user)
        msg = KickCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=KickCommandPayload(channel_id=1, target="nonexistent", reason=""),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.channel_srvc.find_member_by_username.return_value = None

        await handler_kick(ctx, msg, mock_manager)

        # No broadcast or leave should happen
        mock_manager.channel_srvc.send_to_channel.assert_not_called()
        mock_manager.channel_srvc.leave_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_kick_no_permission(
        self, mock_websocket, guest_user, test_channel, mock_manager
    ):
        """User cannot kick (permission denied)."""
        ctx = make_context(mock_websocket, guest_user)
        msg = KickCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=KickCommandPayload(channel_id=1, target="victim", reason=""),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True

        await handler_kick(ctx, msg, mock_manager)

        # Permission denied error
        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "You don't have permission to run this command."
        )
        # No kick action
        mock_manager.channel_srvc.send_to_channel.assert_not_called()


class TestMuteHandler:
    """Tests for handler_mute."""

    @pytest.mark.asyncio
    async def test_mute_success(
        self, mock_websocket, test_user, test_channel, target_user, mock_manager
    ):
        """Target is muted and mute broadcast sent."""
        ctx = make_context(mock_websocket, test_user)
        msg = MuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=MuteCommandPayload(
                channel_id=1, target="victim", duration=300, reason="spam"
            ),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.channel_srvc.find_member_by_username.return_value = target_user

        await handler_mute(ctx, msg, mock_manager)

        # Verify mute was called with correct args
        mock_manager.moderation.mute_user.assert_awaited_once_with(
            target=target_user,
            issuer=test_user,
            channel=test_channel,
            duration=300,
            reason="spam",
        )
        # Verify broadcast was sent
        mock_manager.channel_srvc.send_to_channel.assert_called_once()

    @pytest.mark.asyncio
    async def test_mute_target_cant_send_message(
        self, mock_websocket, test_user, test_channel, target_user, mock_manager
    ):
        """Target is muted and mute broadcast sent."""
        ctx = make_context(mock_websocket, test_user)
        msg_mute = MuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=MuteCommandPayload(
                channel_id=1, target="victim", duration=300, reason="spam"
            ),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.channel_srvc.find_member_by_username.return_value = target_user
        mock_manager.moderation.is_muted.return_value = True

        await handler_mute(ctx, msg_mute, mock_manager)

        msg = ChatSend(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChatSendPayload(channel_id=1, content="Hello, world!"),
        )

        await handler_chat_send(ctx, msg, mock_manager)

        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "You are muted in this channel."
        )

    @pytest.mark.asyncio
    async def test_mute_target_not_found(
        self, mock_websocket, test_user, test_channel, mock_manager
    ):
        """No action when target username doesn't exist."""
        ctx = make_context(mock_websocket, test_user)
        msg = MuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=MuteCommandPayload(channel_id=1, target="nonexistent"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.channel_srvc.find_member_by_username.return_value = None

        await handler_mute(ctx, msg, mock_manager)

        # No mute or broadcast
        mock_manager.moderation.mute_user.assert_not_called()
        mock_manager.channel_srvc.send_to_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_mute_no_permission(
        self, mock_websocket, guest_user, test_channel, mock_manager
    ):
        """Guest user cannot mute."""
        ctx = make_context(mock_websocket, guest_user)
        msg = MuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=MuteCommandPayload(channel_id=1, target="victim"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True

        await handler_mute(ctx, msg, mock_manager)

        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "You don't have permission to run this command."
        )
        mock_manager.moderation.mute_user.assert_not_called()


class TestUnmuteHandler:
    """Tests for handler_unmute."""

    @pytest.mark.asyncio
    async def test_unmute_success(
        self, mock_websocket, test_user, test_channel, target_user, mock_manager
    ):
        """Target is unmuted and unmute broadcast sent."""
        ctx = make_context(mock_websocket, test_user)
        msg = UnMuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=UnMuteCommandPayload(channel_id=1, target="victim"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.channel_srvc.find_member_by_username.return_value = target_user

        await handler_unmute(ctx, msg, mock_manager)

        # Verify unmute was called
        mock_manager.moderation.unmute_user.assert_awaited_once_with(
            target_user, test_channel
        )
        # Verify broadcast
        mock_manager.channel_srvc.send_to_channel.assert_called_once()

    @pytest.mark.asyncio
    async def test_unmute_target_not_found(
        self, mock_websocket, test_user, test_channel, mock_manager
    ):
        """No action when target username doesn't exist."""
        ctx = make_context(mock_websocket, test_user)
        msg = UnMuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=UnMuteCommandPayload(channel_id=1, target="nonexistent"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.channel_srvc.find_member_by_username.return_value = None

        await handler_unmute(ctx, msg, mock_manager)

        mock_manager.moderation.unmute_user.assert_not_called()
        mock_manager.channel_srvc.send_to_channel.assert_not_called()

    @pytest.mark.asyncio
    async def test_unmute_no_permission(
        self, mock_websocket, guest_user, test_channel, mock_manager
    ):
        """Guest user cannot unmute."""
        ctx = make_context(mock_websocket, guest_user)
        msg = UnMuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=UnMuteCommandPayload(channel_id=1, target="victim"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True

        await handler_unmute(ctx, msg, mock_manager)

        mock_manager.send_error.assert_called_once_with(
            mock_websocket, "You don't have permission to run this command."
        )
        mock_manager.moderation.unmute_user.assert_not_called()

    @pytest.mark.asyncio
    async def test_unmute_target_can_send_message(
        self, mock_websocket, test_user, test_channel, target_user, mock_manager
    ):
        """Target is unmuted and can send message."""
        ctx = make_context(mock_websocket, test_user)
        msg_mute = MuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=MuteCommandPayload(
                channel_id=1, target="victim", duration=300, reason="spam"
            ),
        )

        await handler_mute(ctx, msg_mute, mock_manager)

        msg = UnMuteCommand(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=UnMuteCommandPayload(channel_id=1, target="victim"),
        )

        mock_manager.channel_srvc.get_channel_by_id.return_value = test_channel
        mock_manager.channel_srvc.is_member.return_value = True
        mock_manager.channel_srvc.find_member_by_username.return_value = target_user

        await handler_unmute(ctx, msg, mock_manager)
        mock_manager.moderation.is_muted.return_value = False

        # Verify unmute was called
        mock_manager.moderation.unmute_user.assert_awaited_once_with(
            target_user, test_channel
        )

        content = "Hello Test Message"
        msg_send = ChatSend(
            timestamp=datetime.now(),
            id=uuid4(),
            payload=ChatSendPayload(channel_id=1, content=content),
        )

        ctx = make_context(mock_websocket, target_user)
        await handler_chat_send(ctx, msg_send, mock_manager)
        broadcast_msg = mock_manager.channel_srvc.send_to_channel.call_args[0][1]
        assert broadcast_msg.payload.sender.username == target_user.username
        assert broadcast_msg.payload.content == content
