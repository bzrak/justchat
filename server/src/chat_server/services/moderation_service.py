import logging

from chat_server.connection.channel import Channel
from chat_server.connection.user import User
from chat_server.db import crud
from chat_server.db.db import async_session


class ModerationService:
    """
    Moderate users.

    Manage kick, bans, mutes, ...
    """

    def __init__(self) -> None:
        self._mutes = dict()

    async def mute_user(
        self,
        target: User,
        issuer: User,
        channel: Channel,
        duration: int | None = None,
        reason="",
    ):
        async with async_session() as session:
            await crud.mute_user(
                session, target.id, issuer.id, channel.id, duration, reason
            )

    async def is_muted(self, target: User, channel: Channel) -> bool:
        """
        Check if `target` is muted at the `channel`.
        """
        # FIX: Handle mute in Guest User
        async with async_session() as session:
            return await crud.get_mute(session, target.id, channel.id) is not None
