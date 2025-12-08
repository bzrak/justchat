from datetime import datetime
import logging
import uuid
from chat_server.connection.channel import Channel
from chat_server.connection.user import User
from chat_server.infrastructure.channel_manager import ChannelManager
from chat_server.protocol.messages import (
    BaseMessage,
    ChannelJoin,
    ChannelJoinPayload,
    ChannelLeave,
    ChannelLeavePayload,
    UserFrom,
)
from chat_server.services.membership_service import MembershipService
from chat_server.services.message_broker import MessageBroker


class ChannelService:
    """
    Service for Channel-related operations.

    Contains High-Level API for interaction related to Channels.
    """

    def __init__(
        self,
        channel_manager: ChannelManager,
        membership_srvc: MembershipService,
        message_broker: MessageBroker,
    ) -> None:
        self._channelmanager = channel_manager
        self._membershipsrvc = membership_srvc
        self._broker = message_broker

    def create_channel(self, channel: Channel) -> Channel:
        return self._channelmanager.add(channel)

    async def join_channel(self, user: User, channel: Channel) -> None:
        """
        Join a User to a Channel and send an alert to the Channel.
        """
        self._membershipsrvc.join(user, channel)

        await self._alert_user_join(user, channel)

    async def leave_channel(self, user: User, channel: Channel) -> None:
        """
        Remove a User from a Channel and send an alert to to the Channel.
        """
        self._membershipsrvc.leave(user, channel)

        await self._alert_user_left(user, channel)

    async def leave_all_channels(self, user: User) -> None:
        """
        Remove a User from all of its joined Channels and send an alert in all channels.
        """
        channels = self._membershipsrvc.leave_all(user)

        for channel in channels:
            await self._alert_user_left(user, channel)

    def get_channel_members(self, channel: Channel) -> set[User]:
        """
        Get all members of a Channel.
        """
        return self._membershipsrvc.get_channel_members(channel)

    def get_channel_by_id(self, channel_id: int) -> Channel | None:
        """
        Get a Channel by its ID.
        """
        return self._channelmanager.get(channel_id)

    def is_member(self, user: User, channel: Channel) -> bool:
        """
        Check if User is member of a Channel.
        """
        return self._membershipsrvc.is_member(user, channel)

    async def send_to_channel(self, channel: Channel, message: BaseMessage) -> None:
        """
        Send a message to all members of a Channel.
        """

        members = self._membershipsrvc.get_channel_members(channel)
        await self._broker.send_to_channel(members, message)

    async def _alert_user_join(self, user: User, channel: Channel) -> None:
        """
        Send an alert notification that an User has joined the Channel.
        """
        payload = ChannelJoinPayload(
            channel_id=channel.id, user=UserFrom.model_validate(user)
        )
        msg = ChannelJoin(timestamp=datetime.now(), id=uuid.uuid4(), payload=payload)

        logging.info(f"User Join Alert: {repr(user)} has joined {repr(channel)}")

        await self.send_to_channel(channel, msg)

    async def _alert_user_left(self, user: User, channel: Channel) -> None:
        """
        Send an alert notification that an User has left the Channel.
        """
        payload = ChannelLeavePayload(
            channel_id=channel.id, user=UserFrom.model_validate(user)
        )
        msg = ChannelLeave(timestamp=datetime.now(), id=uuid.uuid4(), payload=payload)

        logging.info(f"User Left Alert: {repr(user)} has left {repr(channel)}")

        await self.send_to_channel(channel, msg)
